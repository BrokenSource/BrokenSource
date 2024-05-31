---
title: Uninstalling
---

Thanks for using **Broken Source Software**, I hope you find it useful ❤️

- Here's a exhaustive list of places you'll find all Project data:

## ✅ Runtime Data

!!! tip "**Project Workspaces**: Where Cache, Data, etc are stored"
    The main Library uses [**AppDirs**](https://pypi.org/project/appdirs) {>>to decide per-platform directories<<}

    For unification, all project's Workspaces are located at your Platform's **User Data** directory, followed by a **AppAuthor** and **AppName** subdirectories, which will be <kbd>BrokenSource</kbd> and <kbd>ProjectName</kbd> in most cases

    - **Linux**: `~/.local/share/AppAuthor/AppName/*`
    - **Windows**: `%localappdata%\AppAuthor\AppName\*`
    - **MacOS**: `~/Library/Application Support/AppAuthor/AppName/*`

!!! tip "**[**PyTorch**](https://pytorch.org/) Models**: [HuggingFace](https://huggingface.co/), [TorchHub](https://pytorch.org/hub/), [Transformers](https://github.com/huggingface/transformers)"
    You may find cache directories {==**if** the project uses **Neural Networks**==} for the models at your Platform's **Cache** directory (or the one managed by any of those tools), usually found at:

    - **Linux**: `~/.cache/{huggingface,transformers,torch}/*`
    - **Windows**: `%localappdata%\{huggingface,transformers,torch}\*`
    - **MacOS**: `~/Library/Caches/{huggingface,transformers,torch}/*`

## 🐍 Virtual Environment

!!! tip "Where Dependencies are installed"
    Depending on what Package Manager you use {==(⚠️ Rye is used on the **From Source** installation)==}, you'll find the Python **Virtual Environment** in a couple different places:

    === ":simple-python: Pip"
        Manual method, you either **created it yourself** with `python -m venv (path)`, or it's located at the **System Site Packages** for your Platform, usually found at:

        - **Linux**: `~/.local/lib/python*/site-packages/*`
        - **Windows**: `%localappdata%\Python*\site-packages/*`
        - **MacOS**: `~/Library/Python/*`

    === ":simple-poetry: Poetry"
        Poetry, by default, installs venvs at your Platform's Cache directory:

        - **Linux**: `~/.cache/pypoetry/virtualenvs/*`
        - **Windows**: `%localappdata%\pypoetry\virtualenvs\*`
        - **MacOS**: `~/Library/Caches/pypoetry/virtualenvs/*`

    === ":simple-rye: Rye"
        **Rye** creates Virtual Environments on the `.venv` directory on the Monorepo root or your Project's

    === ":simple-pdm: PDM"
        **PDM** creates Virtual Environments on the `.venv` directory on the Monorepo root or your Project's

## 🔮 Package Manager Cache

!!! abstract "Where download cache is located"
    Depending on what Python Package Manager you use, you may find **cache directories** at:

    - **Linux**: `~/.cache/{pip,uv,poetry,pdm}/*`
    - **Windows**: `%localappdata%\{pip,uv,poetry,pdm}\*`
    - **MacOS**: `~/Library/Caches/{pip,uv,poetry,pdm}/*`

## 📦 From Releases

!!! tip "Where the executables manages themselves"
    [**PyApp**](https://github.com/ofek/pyapp) stores cache, installs packages, creates venv on:

    - **Linux**: `~/.local/share/pyapp`
    - **Windows**: `%applocaldata%\pyapp`
    - **MacOS**: `~/Library/Application Support/pyapp`
