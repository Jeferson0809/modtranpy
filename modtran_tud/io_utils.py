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
def save_standoff_npz(result, path: str) -> None:
    """
    Save a StandoffResult object to a compressed .npz file.
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
        h1=result.h1,
        h2=result.h2,
        range_km=result.range_km,
    )


def load_standoff_npz(path: str):
    """
    Load a StandoffResult object from a .npz file previously saved
    with save_standoff_npz.
    """
    from . import StandoffResult

    data = np.load(path)
    return StandoffResult(
        wavelength=data["wavelength"],
        transmittance=data["transmittance"],
        upwelling=data["upwelling"],
        downwelling=data["downwelling"],
        T_surface=float(data["T_surface"]),
        h2o_scale=float(data["h2o_scale"]),
        o3_scale=float(data["o3_scale"]),
        h1=float(data["h1"]),
        h2=float(data["h2"]),
        range_km=float(data["range_km"]),
    )

