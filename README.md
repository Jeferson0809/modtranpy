# pymodtran – MODTRAN TUD Wrapper

`pymodtran` is a lightweight Python wrapper for **MODTRAN 5**, designed to
compute the thermal atmospheric components:

- **T** – Atmospheric transmittance  
- **U** – Upwelling radiance  
- **D** – Downwelling radiance  

given only three input parameters:

- Surface temperature (`Tsurf`)
- Water vapor scaling factor (`h2o_scale`)
- Ozone scaling factor (`o3_scale`)



---

## Features

- High-level function `run_TUD(Tsurf, h2o_scale, o3_scale)`
- Automatic handling of internal TAPE5 templates (up/down)
- TAPE6 parsing and extraction of T, U, D
- Runtime MODTRAN configuration via `set_modtran_dir(...)`
- Convenience plot `plot_TUD(result)` (3×1 T/U/D figure)
- Save and load simulations as `.npz` (`save_tud_npz`, `load_tud_npz`)

---

## Requirements

This wrapper **does not include MODTRAN**.  
You must provide your own licensed MODTRAN 5 installation.

Typical installation path:

```text
C:\PcModWin5\Bin\
The MODTRAN executable is expected to be located in this directory, e.g.:

text
Copiar código
Mod5.2.1.0.exe
The TAPE5 templates used by the wrapper:

tape5_template_up

tape5_template_down

are bundled inside the package under:

text
Copiar código
modtran_tud/templates/
Installation
Option 1 – Install directly from GitHub (recommended)
bash
Copiar código
pip install git+https://github.com/Jeferson0809/modtranpy.git
Option 2 – Clone and install locally
bash
Copiar código
git clone https://github.com/Jeferson0809/modtranpy.git
cd modtranpy
pip install .
Option 3 – Using uv for development
If you use uv:

bash
Copiar código
git clone https://github.com/Jeferson0809/modtranpy.git
cd modtranpy
uv sync
uv run python scripts/example_run_TUD.py
Quickstart
python
Copiar código
from modtran_tud import (
    run_TUD,
    set_modtran_dir,
    plot_TUD,
)

# 1. Point to your MODTRAN installation
set_modtran_dir(r"C:\PcModWin5\Bin")

# 2. Run a TUD simulation
res = run_TUD(
    Tsurf=295.0,   # surface temperature [K]
    h2o_scale=1.0, # water vapour scaling
    o3_scale=1.0   # ozone scaling
)

# 3. Inspect some values
print("Parameters:", res.T_surface, res.h2o_scale, res.o3_scale)
print("First 5 wavelengths [µm]:", res.wavelength[:5])
print("First 5 transmittance values:", res.transmittance[:5])

# 4. Plot T, U, D (3×1 figure)
plot_TUD(res)
Saving and loading TUD as .npz
You can save and reload simulations using NumPy’s compressed .npz format.
This is useful to:

reuse simulations without rerunning MODTRAN,

move results to another machine or to Google Colab,

build datasets of T/U/D.

python
Copiar código
from modtran_tud import (
    run_TUD,
    set_modtran_dir,
    save_tud_npz,
    load_tud_npz,
)

set_modtran_dir(r"C:\PcModWin5\Bin")

# Run one simulation
res = run_TUD(295.0, 1.0, 1.0)

# Save to disk
save_tud_npz(res, "T295_H1p0_O1p0.npz")

# Later (or on another machine / in Colab)
res_loaded = load_tud_npz("T295_H1p0_O1p0.npz")
You can then plot res_loaded exactly like the original result:

python
Copiar código
from modtran_tud import plot_TUD

plot_TUD(res_loaded)
Package structure
text
Copiar código
modtranpy/
  modtran_tud/
    __init__.py          # Public API: run_TUD, TUDResult, set_modtran_dir, plot_TUD, NPZ helpers
    rtm_simple.py        # MODTRAN interface (TAPE5 creation, MODTRAN run, TAPE6 parsing)
    plotting.py          # Plot utilities for T/U/D
    io_utils.py          # Save/load TUD as .npz
    templates/
      tape5_template_up
      tape5_template_down
  scripts/
    example_run_TUD.py
  pyproject.toml
  .gitignore
  README.md
Notes
MODTRAN is proprietary and cannot be redistributed in this repository.

Always call set_modtran_dir(...) before run_TUD(...).

The wrapper is focused on thermal atmospheric simulations (T, U, D) but can
be extended to other MODTRAN configurations if needed.

sql
Copiar código

Pega eso en tu `README.md`, haz:

```bash
git add README.md
git commit -m "Update README with installation and NPZ usage"
git push
