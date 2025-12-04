import matplotlib.pyplot as plt

def plot_TUD(res,
             lam_min=8.0,
             lam_max=13.0,
             figsize=(10, 8)):
    """
    Figure 3x1: 
    1) Upwelling L↑ [µflick] 
    2) Downwelling L↓ [µflick] 
    3) Transmittance T(λ) 

    res : TUDResult returned by run_TUD.
    """
    wl = res.wavelength
    U  = res.upwelling      # microflicks
    D  = res.downwelling    # microflicks
    T  = res.transmittance  # 0–1

    fig, (ax_up, ax_down, ax_T) = plt.subplots(
        3, 1, figsize=figsize, sharex=True
    )

    # --- Upwelling ---
    ax_up.plot(wl, U, color="red", linewidth=0.8)
    ax_up.set_title("Upwelling L↑ (microflicks)")
    ax_up.set_ylabel("Radiance [µflick]")
    ax_up.grid(True, alpha=0.3)

    # --- Downwelling ---
    ax_down.plot(wl, D, color="blue", linewidth=0.8)
    ax_down.set_title("Downwelling L↓ (microflicks)")
    ax_down.set_ylabel("Radiance [µflick]")
    ax_down.grid(True, alpha=0.3)

    # --- Transmittance ---
    ax_T.plot(wl, T, color="green", linewidth=0.8)
    ax_T.set_title("Transmittance T(λ)")
    ax_T.set_xlabel("Wavelength (µm)")
    ax_T.set_ylabel("T(λ)")
    ax_T.set_ylim(0, 1)
    ax_T.grid(True, alpha=0.3)

    # Spectral range
    ax_T.set_xlim(lam_min, lam_max)

    plt.tight_layout()
    plt.show()
