

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

## **📂 Installation**

Clone the repository:

```bash
git clone https://github.com/USERNAME/modtranpy.git
cd modtranpy
```

Install in development mode:

```bash
pip install -e .
```

---

## **⚙️ Requirements**

This package requires a working, licensed local installation of **MODTRAN 5**.

Example location:

```
C:\PcModWin5\Bin
```

You must provide this folder when running simulations.

---

## **🚀 Quick Start**

### **1. Set the MODTRAN folder**

```python
from modtran_tud import set_modtran_dir, run_TUD, plot_TUD

set_modtran_dir(r"D:\PcModWin5\Bin")
```

### **2. Run a simulation**

```python
res = run_TUD(
    Tsurf=295,
    h2o_scale=1.0,
    o3_scale=1.0
)
```

### **3. Plot the results**

```python
plot_TUD(res)
```

---

## **💾 Saving & Loading Results (.npz)**

### Save:

```python
from modtran_tud.io_utils import save_tud_npz

save_tud_npz("tud_output.npz", res)
```

### Load:

```python
from modtran_tud.io_utils import load_tud_npz

res2 = load_tud_npz("tud_output.npz")
```

---

## **📁 Project Structure**

```
modtran_tud/
    __init__.py
    rtm_simple.py
    plotting.py
    io_utils.py
    templates/
        tape5_template_up
        tape5_template_down
```

(No compiled folders such as `.egg-info` are necessary in the repository.)

---

## **📜 License**

This repository only contains Python code written by the author.
Users must provide their own MODTRAN installation under the terms of its license.

