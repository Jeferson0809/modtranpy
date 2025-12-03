

# **pymodtran – Thermal TUD Wrapper for MODTRAN 5**

`pymodtran` is a small Python library that automates the generation of atmospheric thermal components using MODTRAN 5.
It produces the three key outputs used in thermal remote sensing:

* **Transmittance** T(λ)
* **Upwelling radiance** U(λ)
* **Downwelling radiance** D(λ)

The user only provides:

* Surface temperature (`Tsurf`)
* Water vapor scale (`h2o_scale`)
* Ozone scale (`o3_scale`)

---

## 📦 Installation

1. Create any folder on your computer (e.g. `test_modtran/`):
2. Inside that folder, install the library directly from GitHub:

```powershell
pip install git+https://github.com/Jeferson0809/modtranpy.git
```

3. In the same folder, create a Python file (for example test_tud.py):
   
```powershell
from modtran_tud import (
    run_TUD, set_modtran_dir,
    save_tud_npz, load_tud_npz,
    plot_TUD,
)

# Point to your local MODTRAN 5 installation
set_modtran_dir(r"C:\PcModWin5\Bin")

# Run a simulation (Tsurf,h2o_scale,o3_scale)

res = run_TUD(300.0, 1.0, 1.0)

# Save the result as .npz
save_tud_npz(res, "T300_H1p0_O1p0.npz")

# Load the saved result (can be on another machine or in Colab)
res2 = load_tud_npz("T300_H1p0_O1p0.npz")

# Plot the T, U, D curves from the loaded file
plot_TUD(res2)
```
4. Run the script
```powershell
python test_tud.py
```


⚙️ Requirements

● A local licensed installation of MODTRAN 5

● The directory passed to set_modtran_dir() must contain the MODTRAN executable

Example:
C:\PcModWin5\Bin\
