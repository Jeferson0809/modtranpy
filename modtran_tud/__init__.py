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
    transmittance: np.ndarray        # T_LOS(λ)
    upwelling: np.ndarray            # path radiance (µflick)
    downwelling: np.ndarray          # hemispheric downwelling (µflick)
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
    "plot_standoff",
    "save_tud_npz",
    "load_tud_npz",
    "save_standoff_npz",
    "load_standoff_npz",
]


def set_modtran_dir(path: str):
    """
    Configure the MODTRAN directory (PcModWin5/Bin). This must be
    called once before running run_TUD or run_standoff.
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
    High-level interface for nadir-style TUD (UP + DOWN).

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
    range_km: float = 1.0,
    sensor_center: float | None = None,
    sensor_width: float | None = None,
) -> StandoffResult:
    """
    High-level interface for horizontal standoff TUD:

      - T_LOS(λ): line-of-sight transmittance
      - Upwelling(λ): atmospheric path radiance along the LOS
      - Downwelling(λ): hemispheric downwelling at the ground

    Radiances are returned in microflicks (µW / cm^2 / sr / µm).
    """
    case_name = f"STANDOFF_T{int(Tsurf)}".replace(".", "p")

    sim = simulate_standoff_TUD(
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
        upwelling=sim["up_microflicks"],
        downwelling=sim["down_microflicks"],
        T_surface=sim["T_surface"],
        h2o_scale=sim["h2o_scale"],
        o3_scale=sim["o3_scale"],
        h1=sim["h1"],
        h2=sim["h2"],
        range_km=sim["range_km"],
    )
