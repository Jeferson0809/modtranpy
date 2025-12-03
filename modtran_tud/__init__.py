from dataclasses import dataclass
import numpy as np

from .plotting import plot_TUD
from .rtm_simple import simulate_one, MODTRAN_DIR, OUTPUTS_DIR
from .io_utils import save_tud_npz, load_tud_npz  # si ya lo tienes

@dataclass
class TUDResult:
    wavelength: np.ndarray
    transmittance: np.ndarray
    upwelling: np.ndarray
    downwelling: np.ndarray
    T_surface: float
    h2o_scale: float
    o3_scale: float


__all__ = [
    "run_TUD",
    "TUDResult",
    "set_modtran_dir",
    "plot_TUD",
    "save_tud_npz",
    "load_tud_npz",
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
    High-level interface:
        (Tsurf, h2o_scale, o3_scale, [h1, h2, sensor_center, sensor_width])
        -> TUDResult (T, U, D + wavelength).

    Extra parameters:
      h1, h2           -> written into TAPE5 placeholders H1_VALUE, H2_VALUE
      sensor_center    -> written into SENSOR_CENTER (TAPE5)
      sensor_width     -> written into SENSOR_WIDTH (TAPE5)
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
