# 🔦 PyTorch

!!! note "Some projects have **Optional** or **Total Dependency** on <a href="https://pytorch.org" target="_blank"><b>PyTorch</b></a>"

When inside the **Virtual Environment**, choose a version below and and run the **Command**

!!! abstract "1. Select your Platform"
    === "✅ Windows"
        <div align="center"><img src="https://raw.githubusercontent.com/edent/SuperTinyIcons/master/images/svg/windows.svg" style="vertical-align: middle; border-radius: 20%" width="120"></div>

        === "⚡️ NVIDIA GPU (CUDA)"
            !!! note "Have the <a href="https://www.nvidia.com/download/index.aspx" target="_blank">NVIDIA Drivers</a> installed"

            ```shell title="Command"
            poe cuda
            ```

        === "⌛️ AMD GPU (ROCm)"
            !!! failure "AMD doesn't support ROCm on Windows yet"
            !!! success "It is supported on Linux, consider trying it there!"

        === "❓ Intel ARC GPU"
            !!! bug "Help needed, I don't have the Hardware to test"

        === "🐢 Any CPU"
            !!! note "Slow option, but works on any System"

            ```shell title="Command"
            poe cpu
            ```

    === "🐧 Linux"
        <div align="center"><img src="https://raw.githubusercontent.com/edent/SuperTinyIcons/master/images/svg/linux.svg" style="vertical-align: middle; border-radius: 20%" width="120"></div>

        === "⚡️ NVIDIA GPU (CUDA)"
            !!! note "Have the **NVIDIA Proprietary Drivers** packages installed in your Distro"

            ```shell title="Command"
            poe cuda
            ```

        === "⚡️ AMD GPU (ROCm)"
            !!! note "Have the **Mesa Drivers** and **ROCm** packages installed in your Distro"

            ```shell title="Command"
            poe rocm
            ```

            !!! warning "Requires RX 5000 series or Newer. Might need to set `HSA_OVERRIDE_GFX_VERSION`"
            !!! question "Should work, but I don't have the Hardware to test"

        === "❓ Intel ARC GPU"
            !!! bug "Help needed, I don't have the Hardware to test"

        === "🐢 Any CPU"
            !!! note "Slow option, but works on any System"

            ```shell title="Command"
            poe cpu
            ```

    === "🍎 MacOS"
        <div align="center"><img src="https://raw.githubusercontent.com/edent/SuperTinyIcons/master/images/svg/apple.svg" style="vertical-align: middle; border-radius: 20%" width="120"></div>

        ```shell title="Command"
        poe base
        ```
        !!! question "Should work, but I don't have the Hardware to test"
