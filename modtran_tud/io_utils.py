import numpy as np

def save_tud_npz(result, path: str) -> None:
    """
    Save a TUDResult object to a compressed .npz file.

    Parameters
    ----------
    result : TUDResult
        Output returned by run_TUD.
    path : str
        Output file path, e.g. 'T295_H1p0_O1p0.npz'.
    """
    np.savez(
        path,
        wavelength=result.wavelength,
        transmittance=result.transmittance,
        upwelling=result.upwelling,
        downwelling=result.downwelling,
        T_surface=result.T_surface,
        h2o_scale=result.h2o_scale,
        o3_scale=result.o3_scale,
    )


def load_tud_npz(path: str):
    """
    Load a TUDResult object from a .npz file previously saved
    with save_tud_npz.
    """
    from . import TUDResult  # local import to avoid circular import
    data = np.load(path)
    return TUDResult(
        wavelength=data["wavelength"],
        transmittance=data["transmittance"],
        upwelling=data["upwelling"],
        downwelling=data["downwelling"],
        T_surface=float(data["T_surface"]),
        h2o_scale=float(data["h2o_scale"]),
        o3_scale=float(data["o3_scale"]),
    )
