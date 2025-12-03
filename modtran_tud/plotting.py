import matplotlib.pyplot as plt

def plot_TUD(res,
             lam_min=7.0,
             lam_max=14.0,
             rad_ylim=(0, 1000),
             figsize=(10, 6)):
    """
    Plot tipo 'paper':
      - Eje X: longitud de onda [µm]
      - Eje Y izq: Transmittance (0–1)
      - Eje Y der: Upwelling y Downwelling (µflicks)

    Parámetros
    ----------
    res : TUDResult
        Resultado devuelto por run_TUD.
    lam_min, lam_max : float
        Rango de longitudes de onda a mostrar (µm).
    rad_ylim : tuple
        (ymin, ymax) del eje de radiancia (µflicks).
    figsize : tuple
        Tamaño de la figura.
    """
    wl = res.wavelength
    T  = res.transmittance
    U  = res.upwelling      # ya en microflicks según tu run_TUD
    D  = res.downwelling    # ya en microflicks

    fig, ax_T = plt.subplots(figsize=figsize)

    # --- Transmittance (eje izquierdo) ---
    ax_T.plot(wl, T, linewidth=0.8, color="b", label="Transmission")
    ax_T.set_xlabel("Wavelength (µm)")
    ax_T.set_ylabel("Transmission", color="b")
    ax_T.set_ylim(0, 1)
    ax_T.tick_params(axis="y", labelcolor="b")

    # Rango espectral
    ax_T.set_xlim(lam_min, lam_max)

    # --- Up/Down (eje derecho) ---
    ax_R = ax_T.twinx()
    ax_R.plot(wl, U, linewidth=0.8, color="g", label="Upwelling")
    ax_R.plot(wl, D, linewidth=0.8, color="r", label="Downwelling")
    ax_R.set_ylabel("Upwelling/Downwelling Radiance [µflick]")
    if rad_ylim is not None:
        ax_R.set_ylim(*rad_ylim)

    # Leyenda combinada
    lines_T, labels_T = ax_T.get_legend_handles_labels()
    lines_R, labels_R = ax_R.get_legend_handles_labels()
    ax_R.legend(lines_T + lines_R, labels_T + labels_R, loc="upper right")

    plt.title("Atmospheric TUD Model")
    plt.tight_layout()
    plt.show()
