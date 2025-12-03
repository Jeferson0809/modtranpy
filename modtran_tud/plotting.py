import matplotlib.pyplot as plt

def plot_TUD(res, figsize=(10, 6)):
    """
    Grafica los vectores T, U y D del resultado TUDResult.
    """
    wl = res.wavelength

    plt.figure(figsize=figsize)

    # Transmitancia
    plt.plot(wl, res.transmittance, label="Transmittance (T)", linewidth=2)

    # Upwelling
    plt.plot(wl, res.upwelling, label="Upwelling (U)", linewidth=2)

    # Downwelling
    plt.plot(wl, res.downwelling, label="Downwelling (D)", linewidth=2)

    plt.xlabel("Wavelength [µm]")
    plt.ylabel("Value")
    plt.title("TUD Spectra")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.show()
