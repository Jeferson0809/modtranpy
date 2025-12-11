from dataclasses import dataclass
import numpy as np

from .plotting import plot_TUD, plot_standoff
from .rtm_simple import simulate_one, simulate_standoff_TUD
from .io_utils import (
    save_tud_npz,
    load_tud_npz,
    save_standoff_npz,
    load_standoff_npz,
)

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
# MODTRAN configuration
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


def run_standoff_TUD(
    h2o_scale: float = 1.0,
    o3_scale: float = 1.0,
    h_sensor: float = 0.0015,
    h_ground: float = 0.0,
    range_km: float = 0.1,
    sensor_center: float | None = None,
    sensor_width: float | None = None,
    T_surf: float = 1.0,
) -> TUDResult:
    """
    High-level interface for standoff-based TUD following the TES recipe:

      - Horizontal path at h_sensor over range_km (tape5_template_standoff)
          -> T(λ) and path radiance (treated as upwelling)
      - Down-looking path from h_sensor to h_ground with SURREF=1
          (tape5_template_standoff_D)
          -> hemispherical downwelling radiance

    Returns a TUDResult with:
        wavelength, transmittance, upwelling, downwelling

    NOTE:
      T_surf is the boundary temperature used in both runs (≈ 0 K).
      It is stored as T_surface in the output for bookkeeping only.
    """
    case_name = (
        f"STANDOFF_H{h_sensor:.4f}_R{range_km:.3f}_"
        f"H2O{h2o_scale:.2f}_O3{o3_scale:.2f}"
    ).replace(".", "p")

    sim = simulate_standoff_TUD(
        case_name=case_name,
        h2o_scale=h2o_scale,
        o3_scale=o3_scale,
        h_sensor=h_sensor,
        h_ground=h_ground,
        range_km=range_km,
        sensor_center=sensor_center,
        sensor_width=sensor_width,
        T_surf=T_surf,
    )

    return TUDResult(
        wavelength=sim["wavelength"],
        transmittance=sim["transmittance"],
        upwelling=sim["up_microflicks"],
        downwelling=sim["down_microflicks"],
        T_surface=T_surf,   
        h2o_scale=h2o_scale,
        o3_scale=o3_scale,
    )
