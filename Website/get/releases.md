---
title: Releases
---

!!! quote "**The most convenient** way to use the Projects • Double-click and run, hopefully"
    **Recommended for**: Basic Users

## ⚡️ Installing

!!! success "I make self-installing executables using [**PyApp**](https://github.com/ofek/pyapp) for your convenience!"

!!! abstract "1. Select your Platform"
    === "✅ Windows"
        <div align="center"><img src="https://raw.githubusercontent.com/edent/SuperTinyIcons/master/images/svg/windows.svg" style="vertical-align: middle;  border-radius: 20%;" width="80"></div>
        !!! quote "2. Select the Project"
            === "🌊 DepthFlow"
                - [**Download**](https://github.com/BrokenSource/DepthFlow/releases/download/latest/depthflow-cpu-windows-amd64-latest.exe) (CPU)
                - [**Download**](https://github.com/BrokenSource/DepthFlow/releases/download/latest/depthflow-cuda-windows-amd64-latest.exe) (CUDA)
            === "🎹 Pianola"
                - [**Download**](https://github.com/BrokenSource/Pianola/releases/download/latest/pianola-windows-amd64-latest.exe)
            === "🌵 ShaderFlow"
                - [**Download**](https://github.com/BrokenSource/ShaderFlow/releases/download/latest/shaderflow-windows-amd64-latest.exe)
            === "🎧 SpectroNote"
                - [**Download**](https://github.com/BrokenSource/SpectroNote/releases/download/latest/spectronote-windows-amd64-latest.exe)

    === "🐧 Linux"
        <div align="center"><img src="https://raw.githubusercontent.com/edent/SuperTinyIcons/master/images/svg/linux.svg" style="vertical-align: middle; border-radius: 20%;" width="80"></div>

        !!! quote "2. Select the Project"
            === "🌊 DepthFlow"
                - [**Download**](https://github.com/BrokenSource/DepthFlow/releases/download/latest/depthflow-cpu-linux-amd64-latest.bin) (CPU)
                - [**Download**](https://github.com/BrokenSource/DepthFlow/releases/download/latest/depthflow-cuda-linux-amd64-latest.bin) (CUDA)
                - [**Download**](https://github.com/BrokenSource/DepthFlow/releases/download/latest/depthflow-rocm-linux-amd64-latest.bin) (ROCm)
            === "🎹 Pianola"
                - [**Download**](https://github.com/BrokenSource/Pianola/releases/download/latest/pianola-linux-amd64-latest.bin)
            === "🌵 ShaderFlow"
                - [**Download**](https://github.com/BrokenSource/ShaderFlow/releases/download/latest/shaderflow-linux-amd64-latest.bin)
            === "🎧 SpectroNote"
                - [**Download**](https://github.com/BrokenSource/SpectroNote/releases/download/latest/spectronote-linux-amd64-latest.bin)

    === "🍎 MacOS"
        <div align="center"><img src="https://raw.githubusercontent.com/edent/SuperTinyIcons/master/images/svg/apple.svg" style="vertical-align: middle; border-radius: 20%;" width="80"></div>

        !!! quote "2. Select the Project"
            === "🌊 DepthFlow"
                !!! bug "Help needed, I don't have the Hardware to compile or test"
            === "🎹 Pianola"
                !!! bug "Help needed, I don't have the Hardware to compile or test"
            === "🌵 ShaderFlow"
                !!! bug "Help needed, I don't have the Hardware to compile or test"
            === "🎧 SpectroNote"
                !!! bug "Help needed, I don't have the Hardware to compile or test"

## ⭐️ Usage
Simply **double click** and run the executable on your platform

- Preferably **Open it on a Terminal**, for example:

```shell title="Terminal"
./shaderflow-linux-amd64-0.3.1.bin default -o ./video.mp4
```

!!! warning "Not all projects have a default "visible" behavior"
    Projects like [**ShaderFlow**](https://brokensrc.dev/shaderflow) **requires** a Scene name to be sent as a argument:

    - When no arguments are sent, the behavior is to list all Scenes and quit
    - The immediate interpretation is that it crashed, when it ran fine

    <hr>

    Projects like [**DepthFlow**](https://brokensrc.dev/depthflow) have a default configuration and implicitly call the Scene's `main`

    - To select your own image, run as CLI, e.g. `depthflow input -i ./image.png main -o ./video.mp4`

    - Downloading the models on the first execution takes a while, progress is seen running on Terminal

!!! warning "Customization options are limited at the moment. Prefer [**From Source**](source.md) or [**From PyPI**](pypi.md)"


## 🚀 Upgrading
Download a newer release from **GitHub** or from your **Package Manager**

## ♻️ Uninstalling
See the <a href="../uninstalling" target="_blank"><b>Uninstalling</b></a> page