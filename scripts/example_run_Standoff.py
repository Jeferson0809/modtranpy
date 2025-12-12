from modtran_tud import (
    set_modtran_dir,
    run_standoff_TUD,
    plot_TUD,
    save_tud_npz,
    load_tud_npz,
)

set_modtran_dir(r"C:\PcModWin5\Bin")

# Generate standoff-based T, U, D
res = run_standoff_TUD(
    h2o_scale=1.5,
    o3_scale=1.5,
    h_sensor=0.0015,   # 1.5 m
    h_ground=0.0,
    range_km=5,      
    sensor_center=0.0,
    sensor_width=10.0, # cm^-1 10 min
    T_surf=10.0,        # 10K min
)

save_tud_npz(res, "TUD_standoff_100m.npz")

res2 = load_tud_npz("TUD_standoff_100m.npz")
plot_TUD(res2, lam_min=8.0, lam_max=13.0)
