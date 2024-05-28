---
title: PyTorch
---

!!! note "Some projects have **Optional** or **Total Dependency** on <a href="https://pytorch.org" target="_blank"><b>PyTorch</b></a>"

## 🔥 From Source

When a project requires PyTorch, a Propmt will pop up to `pip install` a flavor

- Alternatively, when inside the **Virtual Environment**, choose a below and run:

!!! abstract "1. Select your Platform"
    === "✅ Windows"
        <div align="center"><img src="https://raw.githubusercontent.com/edent/SuperTinyIcons/master/images/svg/windows.svg" style="vertical-align: middle; border-radius: 20%" width="120"></div>

        === "⚡️ NVIDIA GPU (CUDA)"
            <hr>
            ```shell title="Command"
            poe cuda
            ```

            !!! note "Have the <a href="https://www.nvidia.com/download/index.aspx" target="_blank">NVIDIA Drivers</a> installed"

        === "⌛️ AMD GPU (ROCm)"
            <hr>
            !!! failure "AMD doesn't support ROCm on Windows yet"
            !!! success "It is supported on Linux, consider trying it there!"

        === "❓ Intel ARC GPU"
            <hr>
            !!! bug "Help needed, I don't have the Hardware to test"

        === "🐢 Any CPU"
            <hr>
            !!! note "Slow option, but works on any System"

            ```shell title="Command"
            poe cpu
            ```

    === "🐧 Linux"
        <div align="center"><img src="https://raw.githubusercontent.com/edent/SuperTinyIcons/master/images/svg/linux.svg" style="vertical-align: middle; border-radius: 20%" width="120"></div>

        === "⚡️ NVIDIA GPU (CUDA)"
            <hr>
            ```shell title="Command"
            poe cuda
            ```

            !!! note "Have the **NVIDIA Proprietary Drivers** packages installed in your Distro"

        === "⚡️ AMD GPU (ROCm)"
            <hr>
            ```shell title="Command"
            poe rocm
            ```

            !!! note "Have the **Mesa Drivers** and **ROCm** packages installed in your Distro"
            !!! warning "Requires **RX 5000 series or Newer**. Might need to set `HSA_OVERRIDE_GFX_VERSION=10.3.0`"
            !!! question "Should work, but I don't have the Hardware to test"

        === "❓ Intel ARC GPU"
            <hr>
            !!! bug "Help needed, I don't have the Hardware to test"

        === "🐢 Any CPU"
            <hr>
            ```shell title="Command"
            poe cpu
            ```

            !!! note "Slow option, but works on any System"

    === "🍎 MacOS"
        <div align="center"><img src="https://raw.githubusercontent.com/edent/SuperTinyIcons/master/images/svg/apple.svg" style="vertical-align: middle; border-radius: 20%" width="120"></div>

        ```shell title="Command"
        poe base
        ```
        !!! question "Should work, but I don't have the Hardware to test"

## 🧀 From PyPI
Specify a [**PyTorch version**](https://pytorch.org/get-started/locally) in `pyproject.toml` on the Python package manager that you use. Or do what I do: use [**poethepoet**](https://github.com/nat-n/poethepoet) for the user's choice (or [automate it](https://github.com/BrokenSource/BrokenSource/blob/Master/Broken/Core/BrokenTorch.py))

- PyTorch is hard to deal with, I can't write exhaustively
