from dataclasses import dataclass
import numpy as np

from .plotting import plot_TUD
from .rtm_simple import simulate_one, simulate_standoff
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
    path_radiance: np.ndarray  # microflicks along line of sight
    T_surface: float
    h2o_scale: float
    o3_scale: float
    h1: float | None
    h2: float | None
    range_km: float


__all__ = [
    "run_TUD",
    "TUDResult",
    "run_standoff",
    "StandoffResult",
    "set_modtran_dir",
    "plot_TUD",
    "save_tud_npz",
    "load_tud_npz",
    "save_standoff_npz",
    "load_standoff_npz",
]


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
    High-level interface for up/down TUD simulation:
        (Tsurf, h2o_scale, o3_scale, [h1, h2, sensor_center, sensor_width])
        -> TUDResult (T, U, D + wavelength).
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
    High-level interface for a standoff line-of-sight configuration
    using 'tape5_template_standoff'.

    Parameters
    ----------
    Tsurf : float
        Surface/background temperature used in the model.
    h2o_scale, o3_scale : float
        Scaling factors for water vapor and ozone.
    h1, h2 : float, optional
        Heights in km written into H1_VALUE and H2_VALUE.
    range_km : float, optional
        Line-of-sight distance in kilometers.
    sensor_center, sensor_width : float, optional
        Instrument spectral response in cm^-1 (RW flag).

    Returns
    -------
    StandoffResult
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
