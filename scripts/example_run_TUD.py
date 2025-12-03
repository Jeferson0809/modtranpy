from modtran_tud import (
    run_TUD,
    set_modtran_dir,
    plot_TUD,
    save_tud_npz,
    load_tud_npz,
)


def main():
    set_modtran_dir(r"C:\PcModWin5\Bin")

    # Run one TUD simulation
    res = run_TUD(295.0, 1.0, 1.0)

    print("Saving TUD to NPZ...")
    save_tud_npz(res, "T295_H1p0_O1p0.npz")

    # Load it back (could be on another machine or Colab)
    print("Loading TUD from NPZ...")
    res2 = load_tud_npz("T295_H1p0_O1p0.npz")

    # Plot from the loaded result
    plot_TUD(res2)


if __name__ == "__main__":
    main()
