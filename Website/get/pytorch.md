---
title: Get/PyTorch
---

!!! note "Some projects have **Optional** or **Total Dependency** on <a href="https://pytorch.org" target="_blank"><b>PyTorch</b></a>"

## 🔥 From Source

When a project requires **PyTorch**, {==a Prompt will pop up to install a flavor automatically==}

- Alternatively, when inside the **Virtual Environment**, choose one below and run:

!!! abstract "1. Select your Platform"
    === ":simple-windows: Windows"
        <div align="center"><img src="https://raw.githubusercontent.com/edent/SuperTinyIcons/master/images/svg/windows.svg" style="vertical-align: middle; border-radius: 20%" width="120"></div>
        === ":simple-nvidia: NVIDIA (CUDA)"
            ```shell title="Command"
            poe cuda
            ```
            !!! note "Have the <a href="https://www.nvidia.com/download/index.aspx" target="_blank">NVIDIA Drivers</a> installed"
        === ":simple-amd: Radeon (ROCm)"
            !!! failure "AMD doesn't support ROCm on Windows yet"
            !!! success "It is supported on Linux, consider trying it there!"
            !!! success "Please use **CPU** installation for now"
        === ":simple-intel: Arc (OneAPI)"
            !!! bug "Help needed, I don't have the Hardware to test"
            !!! success "Please use **CPU** installation for now"
        === ":octicons-cpu-16: Any (CPU)"
            ```shell title="Command"
            poe cpu
            ```
            !!! note "Slow option, but works on any System"
    === ":simple-linux: Linux"
        <div align="center"><img src="https://raw.githubusercontent.com/edent/SuperTinyIcons/master/images/svg/linux.svg" style="vertical-align: middle; border-radius: 20%" width="120"></div>
        === ":simple-nvidia: NVIDIA (CUDA)"
            ```shell title="Command"
            poe cuda
            ```
            !!! note "Have the **NVIDIA Proprietary Drivers** packages installed in your Distro"
        === ":simple-amd: Radeon (ROCm)"
            ```shell title="Command"
            poe rocm
            ```
            !!! note "Have the **Mesa Drivers** and **ROCm** packages installed in your Distro"
            !!! warning "Requires **RX 5000 series or Newer**. Set `HSA_OVERRIDE_GFX_VERSION=10.3.0` for (>= RX 5000)"
        === ":simple-intel: Arc (OneAPI)"
            !!! bug "Help needed, I don't have the Hardware to test"
            !!! success "Please use **CPU** installation for now"
        === ":octicons-cpu-16: Any (CPU)"
            ```shell title="Command"
            poe cpu
            ```
            !!! note "Slow option, but works on any System"
    === ":simple-apple: MacOS"
        <div align="center"><img src="https://raw.githubusercontent.com/edent/SuperTinyIcons/master/images/svg/apple.svg" style="vertical-align: middle; border-radius: 20%" width="120"></div>
        ```shell title="Command"
        poe base
        ```
        !!! question "Should work, but I don't have the Hardware to test"

## 🧀 From PyPI
Specify a [**PyTorch version**](https://pytorch.org/get-started/locally) in `pyproject.toml` on the Python package manager that you use. Or do what I do: use [**poethepoet**](https://github.com/nat-n/poethepoet) for the user's choice (or [automate it](https://github.com/BrokenSource/BrokenSource/blob/Master/Broken/Core/BrokenTorch.py))

- PyTorch is hard to deal with, I can't write exhaustively
