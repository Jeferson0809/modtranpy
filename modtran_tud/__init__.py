# __init__.py dentro de modtran_tud

from dataclasses import dataclass
import numpy as np

from .plotting import plot_TUD, plot_standoff
from .rtm_simple import simulate_one, simulate_standoff, simulate_standoff_TUD
from .io_utils import (
    save_tud_npz,
    load_tud_npz,
    save_standoff_npz,
    load_standoff_npz,
)

# ----------------------
# Dataclasses de salida
# ----------------------

@dataclass
class TUDResult:
    wavelength: np.ndarray
    transmittance: np.ndarray
    upwelling: np.ndarray
    downwelling: np.ndarray
    T_surface: float
    h2o_scale: float
    o3_scale: float


@dataclass
class StandoffResult:
    wavelength: np.ndarray
    transmittance: np.ndarray
    path_radiance: np.ndarray   # µflick a lo largo del LOS
    T_surface: float
    h2o_scale: float
    o3_scale: float
    h1: float | None
    h2: float | None
    range_km: float

@dataclass
class StandoffTUDResult:
    wavelength: np.ndarray
    transmittance: np.ndarray
    upwelling: np.ndarray       # path radiance (µflick)
    downwelling: np.ndarray     # hemispheric downwelling (µflick)
    T_surface: float
    h2o_scale: float
    o3_scale: float
    h_sensor_km: float
    h_top_km: float
    range_km: float

__all__ = [
    "run_TUD",
    "TUDResult",
    "run_standoff_TUD",
    "StandoffTUDResult",
    "set_modtran_dir",
    "plot_TUD",
    "plot_standoff",
    "save_tud_npz",
    "load_tud_npz",
    "save_standoff_npz",
    "load_standoff_npz",
]


# ----------------------
# Configuración MODTRAN
# ----------------------

def set_modtran_dir(path: str):
    """
    Configure the MODTRAN directory (PcModWin5/Bin).
    """
    import os
    from . import rtm_simple

    rtm_simple.MODTRAN_DIR = path
    rtm_simple.MODTRAN_EXE = os.path.join(path, "Mod5.2.1.0.exe")
    rtm_simple.OUTPUTS_DIR = os.path.join(path, "outputs_tape6")
    os.makedirs(rtm_simple.OUTPUTS_DIR, exist_ok=True)

# ----------------------
# Nadir TUD
# ----------------------

def run_TUD(
    Tsurf: float,
    h2o_scale: float = 1.0,
    o3_scale: float = 1.0,
    h1: float | None = None,
    h2: float | None = None,
    sensor_center: float | None = None,
    sensor_width: float | None = None,
) -> TUDResult:
    """
    High-level interface for nadir TUD simulation (UP + DOWN).
    """
    case_name = f"T{int(Tsurf)}_H{h2o_scale:.2f}_O{o3_scale:.2f}".replace(".", "p")

    sim = simulate_one(
        Tsurf,
        case_name,
        h2o_scale=h2o_scale,
        o3_scale=o3_scale,
        h1=h1,
        h2=h2,
        sensor_center=sensor_center,
        sensor_width=sensor_width,
    )

    return TUDResult(
        wavelength=sim["wavelength"],
        transmittance=sim["transmittance"],
        upwelling=sim["up_microflicks"],
        downwelling=sim["down_microflicks"],
        T_surface=sim["T_surface"],
        h2o_scale=sim["h2o_scale"],
        o3_scale=sim["o3_scale"],
    )

# ----------------------
# Standoff (solo path)
# ----------------------

def run_standoff(
    Tsurf: float,
    h2o_scale: float = 1.0,
    o3_scale: float = 1.0,
    h1: float | None = None,
    h2: float | None = None,
    range_km: float = 0.1,
    sensor_center: float | None = None,
    sensor_width: float | None = None,
) -> StandoffResult:
    """
    High-level interface for horizontal standoff:
      - T_LOS(λ): line-of-sight transmittance
      - path_radiance(λ): atmospheric path radiance along LOS (µflick)
    """
    case_name = f"STANDOFF_T{int(Tsurf)}".replace(".", "p")

    sim = simulate_standoff(
        Tsurf,
        case_name,
        h2o_scale=h2o_scale,
        o3_scale=o3_scale,
        h1=h1,
        h2=h2,
        sensor_center=sensor_center,
        sensor_width=sensor_width,
        range_km=range_km,
    )

    return StandoffResult(
        wavelength=sim["wavelength"],
        transmittance=sim["transmittance"],
        path_radiance=sim["path_radiance"],
        T_surface=sim["T_surface"],
        h2o_scale=sim["h2o_scale"],
        o3_scale=sim["o3_scale"],
        h1=sim["h1"],
        h2=sim["h2"],
        range_km=sim["range_km"],
    )

def run_standoff_TUD(
    Tsurf: float,
    h2o_scale: float = 1.0,
    o3_scale: float = 1.0,
    h_sensor_km: float = 0.0015,
    h_top_km: float = 6.0,
    range_km: float = 0.1,
    sensor_center: float | None = None,
    sensor_width: float | None = None,
) -> StandoffTUDResult:
    """
    High-level interface for standoff TUD:
      - horizontal path -> T_LOS(λ) + atmospheric path radiance (upwelling)
      - down-looking near the ground -> hemispheric downwelling

    All radiances are returned in microflicks (µW/cm^2/sr/µm).
    """
    case_name = f"STANDOFF_T{int(Tsurf)}".replace(".", "p")

    sim = simulate_standoff_TUD(
        Tsurf=Tsurf,
        case_name=case_name,
        h2o_scale=h2o_scale,
        o3_scale=o3_scale,
        h_sensor_km=h_sensor_km,
        h_top_km=h_top_km,
        range_km=range_km,
        sensor_center=sensor_center,
        sensor_width=sensor_width,
    )

    return StandoffTUDResult(
        wavelength=sim["wavelength"],
        transmittance=sim["transmittance"],
        upwelling=sim["up_microflicks"],
        downwelling=sim["down_microflicks"],
        T_surface=sim["T_surface"],
        h2o_scale=sim["h2o_scale"],
        o3_scale=sim["o3_scale"],
        h_sensor_km=sim["h_sensor_km"],
        h_top_km=sim["h_top_km"],
        range_km=sim["range_km"],
    )

