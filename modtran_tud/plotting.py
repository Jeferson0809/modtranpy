import matplotlib.pyplot as plt


def plot_TUD(res,
             lam_min=8.0,
             lam_max=13.0,
             figsize=(10, 8)):
    """
    3x1 figure for classic TUD:
      1) Upwelling L↑ [µflick]
      2) Downwelling L↓ [µflick]
      3) Transmittance T(λ)

    Parameters
    ----------
    res : TUDResult
        Object returned by run_TUD (or loaded with load_tud_npz).
    """
    wl = res.wavelength
    U  = res.upwelling      # microflicks
    D  = res.downwelling    # microflicks
    T  = res.transmittance  # 0–1

    fig, (ax_up, ax_down, ax_T) = plt.subplots(
        3, 1, figsize=figsize, sharex=True
    )

    # Upwelling
    ax_up.plot(wl, U, color="red", linewidth=0.8)
    ax_up.set_title("Upwelling L↑ (microflicks)")
    ax_up.set_ylabel("Radiance [µflick]")
    ax_up.grid(True, alpha=0.3)

    # Downwelling
    ax_down.plot(wl, D, color="blue", linewidth=0.8)
    ax_down.set_title("Downwelling L↓ (microflicks)")
    ax_down.set_ylabel("Radiance [µflick]")
    ax_down.grid(True, alpha=0.3)

    # Transmittance
    ax_T.plot(wl, T, color="green", linewidth=0.8)
    ax_T.set_title("Transmittance T(λ)")
    ax_T.set_xlabel("Wavelength (µm)")
    ax_T.set_ylabel("T(λ)")
    ax_T.set_ylim(0, 1)
    ax_T.grid(True, alpha=0.3)

    ax_T.set_xlim(lam_min, lam_max)

    plt.tight_layout()
    plt.show()


def plot_standoff(res,
                  lam_min=8.0,
                  lam_max=13.0,
                  figsize=(10, 8)):
    """
    3x1 figure for *standoff* TUD:
      1) Upwelling (path radiance) [µflick]
      2) Downwelling hemispheric [µflick]
      3) Line-of-sight transmittance T(λ)
    """
    wl = res.wavelength
    U  = res.upwelling
    D  = res.downwelling
    T  = res.transmittance

    fig, (ax_up, ax_down, ax_T) = plt.subplots(
        3, 1, figsize=figsize, sharex=True
    )

    # Upwelling (path radiance)
    ax_up.plot(wl, U, color="red", linewidth=0.8)
    ax_up.set_title("Standoff Upwelling (path radiance)")
    ax_up.set_ylabel("Radiance [µflick]")
    ax_up.grid(True, alpha=0.3)

    # Downwelling
    ax_down.plot(wl, D, color="blue", linewidth=0.8)
    ax_down.set_title("Downwelling hemispheric")
    ax_down.set_ylabel("Radiance [µflick]")
    ax_down.grid(True, alpha=0.3)

    # Transmittance
    ax_T.plot(wl, T, color="green", linewidth=0.8)
    ax_T.set_title("Line-of-sight Transmittance T(λ)")
    ax_T.set_xlabel("Wavelength (µm)")
    ax_T.set_ylabel("T(λ)")
    ax_T.set_ylim(0, 1)
    ax_T.grid(True, alpha=0.3)

    ax_T.set_xlim(lam_min, lam_max)
    plt.tight_layout()
    plt.show()
