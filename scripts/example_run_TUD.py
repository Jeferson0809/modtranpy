from modtran_tud import run_TUD, set_modtran_dir

set_modtran_dir(r"D:\PcModWin5\Bin")  # ajusta si tu MODTRAN está en otra ruta

res = run_TUD(Tsurf=295.0, h2o_scale=1.0, o3_scale=1.0)

print(res.T_surface, res.h2o_scale, res.o3_scale)
print(res.wavelength[:5])
print(res.transmittance[:5])

