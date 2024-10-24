---
title: Get/Uninstalling
---

Thanks for using **Broken Source Software**, I hope you found it useful ❤️

- Here's a exhaustive list of places you'll find all Project data:

## ✅ Runtime Data

!!! tip "**Project Workspaces**: Where Cache, Data, etc are stored"
    The main Library uses [**AppDirs**](https://pypi.org/project/appdirs) {>>to decide per-platform directories<<}

    For unification, all project's Workspaces are located at your Platform's **User Data** or **Documents** directory, followed by a {++**AppAuthor**++} and {++**AppName**++}, which will be <kbd>BrokenSource</kbd> and <kbd>ProjectName</kbd> in most cases

    - **Linux**: `~/.local/share/BrokenSource/AppName/*`
    - **Windows**: `Documents\BrokenSource\AppName\*`
    - **MacOS**: `~/Library/Application Support/BrokenSource/AppName/*`

## 📦 Releases installation

!!! tip "Where the executables manages themselves"
    [**PyApp**](https://github.com/ofek/pyapp) stores cache, installs packages, creates venv on:

    - **Linux**: `~/.local/share/pyapp`
    - **Windows**: `%applocaldata%\pyapp`
    - **MacOS**: `~/Library/Application Support/pyapp`

## 🐍 Python stuff

!!! tip "Where Dependencies are installed"
    Depending on what **Python Manager** you used, {==(⚠️ uv is used on the **From Source** installation)==}, you'll find the Python **Virtual Environment** in a couple different places:

    === ":simple-python: Pip"
        Manual method, you either **created it yourself** with `python -m venv (path)` or it's located at the **System Site Packages** for your Platform. It's a **BAD IDEA** to remove the later, so do a `pip uninstall {packages}`

    === ":simple-poetry: Poetry"
        Poetry, by default, installs venvs at your Platform's Cache directory:

        - **Linux**: `~/.cache/pypoetry/virtualenvs/*`
        - **Windows**: `%localappdata%\pypoetry\virtualenvs\*`
        - **MacOS**: `~/Library/Caches/pypoetry/virtualenvs/*`

    === ":simple-astral: uv"
        **uv** creates Virtual Environments on the `.venv` directory on the repository root

    === ":simple-rye: Rye"
        **Rye** creates Virtual Environments on the `.venv` directory on the repository root

    === ":simple-pdm: PDM"
        **PDM** creates Virtual Environments on the `.venv` directory on the repository root


!!! tip "**[**PyTorch**](https://pytorch.org/) Models**: [HuggingFace](https://huggingface.co/), [TorchHub](https://pytorch.org/hub/), [Transformers](https://github.com/huggingface/transformers)"
    You may find cache directories, {==**if** the project uses **PyTorch**==}, for **Neural Network** models at your Platform's **Cache** directory (or the one managed by any of those tools), usually found at:

    - **Linux**: `~/.cache/{huggingface,transformers,torch}/*`
    - **Windows**: `%localappdata%\{huggingface,transformers,torch}\*`
    - **MacOS**: `~/Library/Caches/{huggingface,transformers,torch}/*`
