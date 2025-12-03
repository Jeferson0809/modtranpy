import os
import subprocess
import numpy as np
import pandas as pd
import re
from io import StringIO

# ===== CONFIGURACIÓN BÁSICA =====
MODTRAN_DIR   = r"D:\PcModWin5\Bin"
MODTRAN_EXE   = os.path.join(MODTRAN_DIR, "Mod5.2.1.0.exe")  

OUTPUTS_DIR   = os.path.join(MODTRAN_DIR, "outputs_tape6")
os.makedirs(OUTPUTS_DIR, exist_ok=True)

import importlib.resources as resources

def load_template(template_name: str):
    """
    Devuelve la ruta al template incluido en modtran_tud/templates.
    No requiere que 'templates' sea un paquete Python.
    """
    pkg_root = resources.files("modtran_tud")
    return pkg_root.joinpath("templates", template_name)

# -------------------------------
# 1) Construir TAPE5 desde template
# -------------------------------
def build_tape5(template_name, Tsurf, h2o_scale=1.0, o3_scale=1.0):
    template_path = load_template(template_name)

    with open(template_path, "r", encoding="latin-1", errors="replace") as f:
        txt = f.read()

    txt = txt.replace("TSURF",    f"{Tsurf:.2f}")
    txt = txt.replace("H2O_SCALE", f"{h2o_scale:.3f}")
    txt = txt.replace("O3_SCALE",  f"{o3_scale:.3f}")

    return txt



# -------------------------------
# 2) Ejecutar MODTRAN y guardar TAPE6
# -------------------------------
def run_modtran(tape5_text, out_basename):
    """
    Escribe TAPE5 en MODTRAN_DIR, ejecuta MODTRAN, y mueve el TAPE6 resultante
    a outputs_tape6/<out_basename>.tp6

    Devuelve: ruta completa al .tp6
    """
    tape5_path = os.path.join(MODTRAN_DIR, "TAPE5")
    with open(tape5_path, "w", encoding="latin-1", errors="replace") as f:
        f.write(tape5_text)

    tape6_src = os.path.join(MODTRAN_DIR, "TAPE6")
    if os.path.exists(tape6_src):
        os.remove(tape6_src)

    subprocess.run([MODTRAN_EXE], cwd=MODTRAN_DIR, check=True)

    if not os.path.exists(tape6_src):
        raise RuntimeError("MODTRAN no generó TAPE6")

    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    tape6_dst = os.path.join(OUTPUTS_DIR, out_basename + ".tp6")
    os.replace(tape6_src, tape6_dst)

    return tape6_dst


# -------------------------------
# 3) Parsear un TAPE6 (bloque RADIANCE)
# -------------------------------
def parse_tape6(path):
    """
    Lee TODOS los bloques de
    RADIANCE(WATTS/CM2-STER-XXX)
    de un TAPE6 y concatena todas las filas numéricas
    en un único DataFrame.
    """

    with open(path, "r", encoding="latin-1", errors="replace") as f:
        text = f.read()

    m = re.search(r"RADIANCE\(WATTS/CM2-STER-XXX\)", text)
    if not m:
        raise RuntimeError("No se encontró el encabezado de RADIANCE en el TAPE6")

    lines = text[m.end():].splitlines()

    data_lines = []

    for line in lines:
        s = line.strip()
        if not s:
            continue

        if s.startswith("FREQ") or s.startswith("(CM-1)"):
            continue

        if s[0].isdigit() or s[0] in ".-+":
            data_lines.append(s)

    if not data_lines:
        raise RuntimeError(f"No filas numéricas válidas en {path}")

    header = (
        "FREQ WAVELENGTH DIREC "
        "PATH_TH_CM PATH_TH_UM "
        "SCAT_PART "
        "SURF_EM_CM SURF_EM_UM "
        "SURF_REF_CM SURF_REF_UM "
        "TOTAL_RAD_CM TOTAL_RAD_UM "
        "INTEGRAL TOTAL"
    )

    csv_text = header + "\n" + "\n".join(data_lines)
    df = pd.read_csv(StringIO(csv_text), sep=r"\s+", engine="python")

    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    freq          = df["FREQ"].values
    wavelength_um = df["WAVELENGTH"].values

    path_th_um    = df["PATH_TH_UM"].values
    scat_part     = df["SCAT_PART"].values

    surf_em_um    = df["SURF_EM_UM"].values
    surf_ref_um   = df["SURF_REF_UM"].values
    total_rad_cm  = df["TOTAL_RAD_CM"].values
    total_rad_um  = df["TOTAL_RAD_UM"].values

    integral      = df["INTEGRAL"].values
    trans         = df["TOTAL"].values

    return {
        "freq": freq,
        "wavelength": wavelength_um,
        "path_thermal": path_th_um,
        "scat_part": scat_part,
        "surface_emission": surf_em_um,
        "surface_reflected": surf_ref_um,
        "total_radiance_cm": total_rad_cm,
        "total_radiance": total_rad_um,
        "integral": integral,
        "transmittance": trans,
        "raw": df,
    }


# -------------------------------
# 4) Simulación UP + DOWN y empaquetado
# -------------------------------
def simulate_one(Tsurf, case_name, h2o_scale=1.0, o3_scale=1.0):
    """
    Corre dos casos:
      - UP: tape5_template_up  (sensor arriba, L↑ y T)
      - DOWN: tape5_template_down (sensor abajo mirando al cielo, L↓)

    Devuelve un dict con:
      wavelength,
      up_microflicks,
      down_microflicks,
      transmittance, path_thermal, scat_part, surface_emission, surface_reflected,
      T_surface, h2o_scale, o3_scale,
      tp6_up, tp6_down
    """

    tape5_up = build_tape5("tape5_template_up", Tsurf, h2o_scale, o3_scale)
    tp6_up_path = run_modtran(tape5_up, f"{case_name}_UP")
    res_up = parse_tape6(tp6_up_path)

    tape5_down = build_tape5("tape5_template_down", Tsurf, h2o_scale, o3_scale)
    tp6_down_path = run_modtran(tape5_down, f"{case_name}_DOWN")
    res_down = parse_tape6(tp6_down_path)

    up_micro   = res_up["total_radiance"]   * 1e6
    down_micro = res_down["total_radiance"] * 1e6

    res = {
        "wavelength":       res_up["wavelength"],
        "up_microflicks":   up_micro,
        "down_microflicks": down_micro,
        "transmittance":    res_up["transmittance"],
        "path_thermal":     res_up["path_thermal"],
        "scat_part":        res_up["scat_part"],
        "surface_emission": res_up["surface_emission"],
        "surface_reflected":res_up["surface_reflected"],
        "T_surface":        Tsurf,
        "h2o_scale":        h2o_scale,
        "o3_scale":         o3_scale,
        "tp6_up":           tp6_up_path,
        "tp6_down":         tp6_down_path,
    }
    return res
