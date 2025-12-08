import os
import subprocess
import numpy as np
import pandas as pd
import re
from io import StringIO
import importlib.resources as resources

# ===== BASIC MODTRAN CONFIGURATION =====
# These globals are set from set_modtran_dir() in __init__.py
MODTRAN_DIR: str | None = None
MODTRAN_EXE: str | None = None
OUTPUTS_DIR: str | None = None


def load_template(template_name: str):
    """
    Return the path to a TAPE5 template stored in
    modtran_tud/templates.

    This does NOT require "templates" to be a Python package.
    """
    pkg_root = resources.files("modtran_tud")
    return pkg_root.joinpath("templates", template_name)


# -------------------------------
# 1) Build TAPE5 from template
# -------------------------------
def build_tape5(
    template_name,
    Tsurf,
    h2o_scale=1.0,
    o3_scale=1.0,
    h1=None,
    h2=None,
    sensor_center=None,
    sensor_width=None,
    range_km=None,
):
    """
    Load a TAPE5 template and replace placeholders:

      TSURF        -> surface temperature (K)
      H2O_SCALE    -> water vapour scale
      O3_SCALE     -> ozone scale
      H1_VALUE     -> H1 (km), if provided
      H2_VALUE     -> H2 (km), if provided
      RANGE_KM     -> standoff path length (km), if provided
      SENSOR_CENTER-> central wavenumber of the band (cm^-1), if provided
      SENSOR_WIDTH -> slit FWHM in cm^-1 (clamped to >= 10 cm^-1)

    The exact interpretation of these values depends on the template
    (nadir TUD, standoff, downwelling, etc.).
    """
    template_path = load_template(template_name)

    with open(template_path, "r", encoding="latin-1", errors="replace") as f:
        txt = f.read()

    # Required scalars
    txt = txt.replace("TSURF", f"{Tsurf:.2f}")
    txt = txt.replace("H2O_SCALE", f"{h2o_scale:.3f}")
    txt = txt.replace("O3_SCALE", f"{o3_scale:.3f}")

    # Heights
    if h1 is not None:
        txt = txt.replace("H1_VALUE", f"{h1:.6f}")
    if h2 is not None:
        txt = txt.replace("H2_VALUE", f"{h2:.6f}")

    # Standoff range
    if range_km is not None:
        txt = txt.replace("RANGE_KM", f"{range_km:.3f}")

    # Spectral response
    if sensor_center is not None:
        txt = txt.replace("SENSOR_CENTER", f"{sensor_center:.5f}")

    if sensor_width is not None:
        # MODTRAN manual recommends FWHM >= 10 cm^-1 when using band model.
        MIN_WIDTH = 10.0
        if sensor_width < MIN_WIDTH:
            print(
                f"[modtran_tud] WARNING: sensor_width={sensor_width} "
                f"is too small for MODTRAN (cm^-1). Using {MIN_WIDTH} instead."
            )
            width_eff = MIN_WIDTH
        else:
            width_eff = sensor_width
        txt = txt.replace("SENSOR_WIDTH", f"{width_eff:.5f}")

    return txt


# -------------------------------
# 2) Run MODTRAN and save TAPE6
# -------------------------------
def run_modtran(tape5_text, out_basename):
    """
    Write TAPE5 to MODTRAN_DIR, run MODTRAN, and move the resulting TAPE6 to
    outputs_tape6/<out_basename>.tp6

    Returns
    -------
    str
        Full path to the generated .tp6 file.
    """
    global MODTRAN_DIR, MODTRAN_EXE, OUTPUTS_DIR

    if MODTRAN_DIR is None or MODTRAN_EXE is None:
        raise RuntimeError(
            "MODTRAN_DIR/MODTRAN_EXE not set. Call first "
            "set_modtran_dir('path/to/PcModWin5/Bin')."
        )

    if OUTPUTS_DIR is None:
        OUTPUTS_DIR = os.path.join(MODTRAN_DIR, "outputs_tape6")

    os.makedirs(OUTPUTS_DIR, exist_ok=True)

    # Write TAPE5
    tape5_path = os.path.join(MODTRAN_DIR, "TAPE5")
    with open(tape5_path, "w", encoding="latin-1", errors="replace") as f:
        f.write(tape5_text)

    # Remove old TAPE6 if present
    tape6_src = os.path.join(MODTRAN_DIR, "TAPE6")
    if os.path.exists(tape6_src):
        os.remove(tape6_src)

    # Run MODTRAN
    subprocess.run([MODTRAN_EXE], cwd=MODTRAN_DIR, check=True)

    if not os.path.exists(tape6_src):
        raise RuntimeError("MODTRAN did not generate TAPE6")

    tape6_dst = os.path.join(OUTPUTS_DIR, out_basename + ".tp6")
    os.replace(tape6_src, tape6_dst)

    return tape6_dst


# -------------------------------
# 3) Parse TAPE6 (RADIANCE block)
# -------------------------------
def parse_tape6(path):
    """
    Read ALL blocks of

        RADIANCE(WATTS/CM2-STER-XXX)

    from a TAPE6 file and concatenate all numeric rows into a single
    pandas DataFrame. Returns a dict with the main fields plus the
    full DataFrame in "raw".
    """

    with open(path, "r", encoding="latin-1", errors="replace") as f:
        text = f.read()

    m = re.search(r"RADIANCE\(WATTS/CM2-STER-XXX\)", text)
    if not m:
        raise RuntimeError("The RADIANCE header was not found on TAPE6")

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
        raise RuntimeError(f"No valid numeric rows in {path}")

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
# 4) Nadir-style UP + DOWN TUD
# -------------------------------
def simulate_one(
    Tsurf,
    case_name,
    h2o_scale,
    o3_scale,
    h1=None,
    h2=None,
    sensor_center=None,
    sensor_width=None,
):
    """
    Classic two-case TUD for nadir / limb:

      - UP case:   sensor looking down to the surface
                   -> upwelling + transmittance
      - DOWN case: sensor looking up to the sky
                   -> hemispheric downwelling

    Extra parameters are written into the TAPE5 templates via placeholders.
    """
    global MODTRAN_DIR, OUTPUTS_DIR

    if MODTRAN_DIR is None:
        raise RuntimeError(
            "MODTRAN_DIR is not set. Use set_modtran_dir('path/to/PcModWin5/Bin') "
            "before calling run_TUD()."
        )

    if OUTPUTS_DIR is None:
        OUTPUTS_DIR = os.path.join(MODTRAN_DIR, "outputs_tape6")
        os.makedirs(OUTPUTS_DIR, exist_ok=True)

    # --- UP case ---
    tape5_up = build_tape5(
        "tape5_template_up",
        Tsurf,
        h2o_scale,
        o3_scale,
        h1=h1,
        h2=h2,
        sensor_center=sensor_center,
        sensor_width=sensor_width,
    )
    tp6_up_path = run_modtran(tape5_up, f"{case_name}_UP")
    res_up = parse_tape6(tp6_up_path)

    # --- DOWN case ---
    tape5_down = build_tape5(
        "tape5_template_down",
        Tsurf,
        h2o_scale,
        o3_scale,
        h1=h1,
        h2=h2,
        sensor_center=sensor_center,
        sensor_width=sensor_width,
    )
    tp6_down_path = run_modtran(tape5_down, f"{case_name}_DOWN")
    res_down = parse_tape6(tp6_down_path)

    up_micro = res_up["total_radiance"] * 1e6
    down_micro = res_down["total_radiance"] * 1e6

    res = {
        "wavelength":        res_up["wavelength"],
        "up_microflicks":    up_micro,
        "down_microflicks":  down_micro,
        "transmittance":     res_up["transmittance"],
        "path_thermal":      res_up["path_thermal"],
        "scat_part":         res_up["scat_part"],
        "surface_emission":  res_up["surface_emission"],
        "surface_reflected": res_up["surface_reflected"],
        "T_surface":         Tsurf,
        "h2o_scale":         h2o_scale,
        "o3_scale":          o3_scale,
        "tp6_up":            tp6_up_path,
        "tp6_down":          tp6_down_path,
    }
    return res


# -------------------------------
# 5) Simple standoff line-of-sight
# -------------------------------
def simulate_standoff(
    Tsurf,
    case_name,
    h2o_scale,
    o3_scale,
    h1=None,
    h2=None,
    sensor_center=None,
    sensor_width=None,
    range_km=None,
):
    """
    Single MODTRAN run for a standoff LOS using `tape5_template_standoff`.

    This gives:
      - T_LOS(λ)  as "transmittance"
      - path radiance along LOS as "path_radiance" (microflicks)
    """
    global MODTRAN_DIR, OUTPUTS_DIR

    if MODTRAN_DIR is None:
        raise RuntimeError(
            "MODTRAN_DIR is not set. Use set_modtran_dir('path/to/PcModWin5/Bin') "
            "before calling run_standoff()."
        )

    if OUTPUTS_DIR is None:
        OUTPUTS_DIR = os.path.join(MODTRAN_DIR, "outputs_tape6")
        os.makedirs(OUTPUTS_DIR, exist_ok=True)

    tape5_standoff = build_tape5(
        "tape5_template_standoff",
        Tsurf,
        h2o_scale=h2o_scale,
        o3_scale=o3_scale,
        h1=h1,
        h2=h2,
        sensor_center=sensor_center,
        sensor_width=sensor_width,
        range_km=range_km,
    )

    tp6_path = run_modtran(tape5_standoff, f"{case_name}_STANDOFF")
    res = parse_tape6(tp6_path)

    path_mf = res["total_radiance"] * 1e6

    return {
        "wavelength":    res["wavelength"],
        "transmittance": res["transmittance"],
        "path_radiance": path_mf,
        "T_surface":     Tsurf,
        "h2o_scale":     h2o_scale,
        "o3_scale":      o3_scale,
        "h1":            h1,
        "h2":            h2,
        "range_km":      range_km,
        "tp6":           tp6_path,
    }


# -------------------------------
# 6) Full standoff TUD (T, U, D)
# -------------------------------
def simulate_standoff_TUD(
    Tsurf: float,
    case_name: str,
    h2o_scale: float,
    o3_scale: float,
    h1: float | None = None,
    h2: float | None = None,
    sensor_center: float | None = None,
    sensor_width: float | None = None,
    range_km: float = 1.0,
):
    """
    Standoff TUD simulation in two steps:

      1) STANDOFF case (horizontal LOS, `tape5_template_standoff`)
         -> T_LOS(λ) and atmospheric path radiance (Upwelling-equivalent).

      2) DOWN case (`tape5_template_down`)
         -> hemispheric downwelling D(λ) at the ground.

    Notes:
      * For a "pure" atmospheric TUD as in the paper, the standoff
        template should use a very cold, black ground (T ~ 0 K,
        reflectance ~ 0), and the DOWN template a perfectly reflective
        ground (reflectance = 1).
    """
    global MODTRAN_DIR, OUTPUTS_DIR

    if MODTRAN_DIR is None:
        raise RuntimeError(
            "MODTRAN_DIR is not set. Use set_modtran_dir('path/to/PcModWin5/Bin') "
            "before calling run_standoff()."
        )

    if OUTPUTS_DIR is None:
        OUTPUTS_DIR = os.path.join(MODTRAN_DIR, "outputs_tape6")
        os.makedirs(OUTPUTS_DIR, exist_ok=True)

    # ---- 1) STANDOFF CASE: horizontal path
    tape5_stand = build_tape5(
        "tape5_template_standoff",
        Tsurf,
        h2o_scale=h2o_scale,
        o3_scale=o3_scale,
        h1=h1,
        h2=h2,
        sensor_center=sensor_center,
        sensor_width=sensor_width,
        range_km=range_km,
    )
    tp6_stand_path = run_modtran(tape5_stand, f"{case_name}_STAND")
    res_stand = parse_tape6(tp6_stand_path)

    lam = res_stand["wavelength"]
    T_los = res_stand["transmittance"]
    U_path = res_stand["total_radiance"] * 1e6  # microflicks

    # ---- 2) DOWN CASE: hemispheric downwelling at ground
    tape5_down = build_tape5(
        "tape5_template_down",
        Tsurf,
        h2o_scale=h2o_scale,
        o3_scale=o3_scale,
        h1=h1,
        h2=h2,
        sensor_center=sensor_center,
        sensor_width=sensor_width,
    )
    tp6_down_path = run_modtran(tape5_down, f"{case_name}_DOWN")
    res_down = parse_tape6(tp6_down_path)

    D_hemi = res_down["total_radiance"] * 1e6  # microflicks

    return {
        "wavelength": lam,
        "transmittance": T_los,
        "up_microflicks": U_path,
        "down_microflicks": D_hemi,
        "T_surface": Tsurf,
        "h2o_scale": h2o_scale,
        "o3_scale": o3_scale,
        "h1": h1,
        "h2": h2,
        "range_km": range_km,
        "tp6_standoff": tp6_stand_path,
        "tp6_down": tp6_down_path,
    }
