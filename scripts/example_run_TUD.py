from modtran_tud import (
    run_TUD, set_modtran_dir,
    save_tud_npz, load_tud_npz,
    plot_TUD
)

set_modtran_dir(r"C:\PcModWin5\Bin")

res = run_TUD(
    Tsurf=100.0,
    h2o_scale=1.0,
    o3_scale=1.0,
    h1=6.0,
    h2=0.0015,
    sensor_center=0.0,
    sensor_width=10.0 # cm-1 min 10
)

# Save to disk
save_tud_npz(res, "T300_H1p0_O1p0.npz")

# Later (or on another machine / in Colab)
res2 = load_tud_npz("T300_H1p0_O1p0.npz")
plot_TUD(res2)
