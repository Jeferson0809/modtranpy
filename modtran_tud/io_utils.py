import numpy as np


def save_tud_npz(result, path: str) -> None:
    """
    Save a TUDResult object to a compressed .npz file.
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
    Save a StandoffTUDResult object to a compressed .npz file.
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
        h_sensor_km=result.h_sensor_km,
        h_top_km=result.h_top_km,
        range_km=result.range_km,
    )


def load_standoff_npz(path: str):
    """
    Load a StandoffTUDResult object from a .npz file previously saved
    with save_standoff_npz.
    """
    from . import StandoffTUDResult  # avoid circular import

    data = np.load(path)
    return StandoffTUDResult(
        wavelength=data["wavelength"],
        transmittance=data["transmittance"],
        upwelling=data["upwelling"],
        downwelling=data["downwelling"],
        T_surface=float(data["T_surface"]),
        h2o_scale=float(data["h2o_scale"]),
        o3_scale=float(data["o3_scale"]),
        h_sensor_km=float(data["h_sensor_km"]),
        h_top_km=float(data["h_top_km"]),
        range_km=float(data["range_km"]),
    )
