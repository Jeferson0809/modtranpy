from dataclasses import dataclass
import numpy as np

from . import rtm_simple as _rtm
from .plotting import plot_TUD


@dataclass
class TUDResult:
    wavelength: np.ndarray
    transmittance: np.ndarray
    upwelling: np.ndarray
    downwelling: np.ndarray
    T_surface: float
    h2o_scale: float
    o3_scale: float


__all__ = ["run_TUD", "TUDResult", "set_modtran_dir", "plot_TUD"]


def set_modtran_dir(path: str, exe_name: str = "Mod5.2.1.0.exe"):
    """
    Configura la ruta a MODTRAN en tiempo de ejecución.
    """
    import os

    _rtm.MODTRAN_DIR = path
    _rtm.MODTRAN_EXE = os.path.join(path, exe_name)
    _rtm.OUTPUTS_DIR = os.path.join(path, "outputs_tape6")
    os.makedirs(_rtm.OUTPUTS_DIR, exist_ok=True)


def run_TUD(Tsurf: float,
            h2o_scale: float = 1.0,
            o3_scale: float = 1.0) -> TUDResult:
    case_name = f"T{int(Tsurf)}_H{h2o_scale:.2f}_O{o3_scale:.2f}".replace(".", "p")

    sim = _rtm.simulate_one(Tsurf, case_name, h2o_scale=h2o_scale, o3_scale=o3_scale)

    return TUDResult(
        wavelength     = sim["wavelength"],
        transmittance  = sim["transmittance"],
        upwelling      = sim["up_microflicks"],
        downwelling    = sim["down_microflicks"],
        T_surface      = sim["T_surface"],
        h2o_scale      = sim["h2o_scale"],
        o3_scale       = sim["o3_scale"],
    )
