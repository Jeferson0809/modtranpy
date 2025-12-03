from dataclasses import dataclass
import numpy as np
from .plotting import plot_TUD
from .rtm_simple import simulate_one, MODTRAN_DIR, OUTPUTS_DIR


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


def set_modtran_dir(path: str):
    """
    Versión simple: solo cambia MODTRAN_DIR y OUTPUTS_DIR en tiempo de ejecución.
    """
    import os
    global MODTRAN_DIR, OUTPUTS_DIR
    MODTRAN_DIR = path
    OUTPUTS_DIR = os.path.join(MODTRAN_DIR, "outputs_tape6")


def run_TUD(Tsurf: float,
            h2o_scale: float = 1.0,
            o3_scale: float = 1.0) -> TUDResult:
    """
    Interfaz de alto nivel:
        Tsurf, H2O_scale, O3_scale  ->  T, U, D (más lambda).
    """
    case_name = f"T{int(Tsurf)}_H{h2o_scale:.2f}_O{o3_scale:.2f}".replace(".", "p")

    sim = simulate_one(Tsurf, case_name, h2o_scale=h2o_scale, o3_scale=o3_scale)

    return TUDResult(
        wavelength     = sim["wavelength"],
        transmittance  = sim["transmittance"],
        upwelling      = sim["up_microflicks"],
        downwelling    = sim["down_microflicks"],
        T_surface      = sim["T_surface"],
        h2o_scale      = sim["h2o_scale"],
        o3_scale       = sim["o3_scale"],
    )
