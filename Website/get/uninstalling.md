---
title: Uninstalling
---

Thanks for using **Broken Source Software**, I hope you find it useful ❤️

- The code and data is pretty easy to remove, check out:

<hr>

!!! tip "**Project Workspaces**: Where Cache, Data, etc are stored"
    The main Library uses [**AppDirs**](https://pypi.org/project/appdirs) to decide per-platform directories

    For unification, all project's Workspaces are located at the User Data directory, followed by a **AppAuthor** and **AppName** subdirectories, which will be <kbd>BrokenSource</kbd> and <kbd>ProjectName</kbd> in most cases

    - **Linux**: `~/.local/share/AppAuthor/AppName/*`
    - **Windows**: `%localappdata%\AppAuthor\AppName\*`
    - **MacOS**: `~/Library/Application Support/AppAuthor/AppName/*`

<hr>

!!! tip "**Python Virtual Environment**: Where Dependencies are stored"
    **Rye** creates Virtual Environments on the `.venv` directory on the Monorepo root. You might have installed the wheel as a [**PyPI dependency**](https://pypi.org/project/broken-source/), either unninstall it from your Python package manager or delete the venv

    The download cache if you chose `uv` instead of `pip-tools` is located at:

    - **Linux**: `~/.cache/uv/*`
    - **Windows**: `%localappdata%\uv\*`
    - **MacOS**: `~/Library/Caches/uv/*`

<hr>

!!! tip "**Releases Virtual Environment**: Where Releases install themselves"
    I use [**PyApp**](https://github.com/ofek/pyapp) to make the releases. It **installs itself** on:

    - **Linux**: `~/.local/share/pyapp`
    - **Windows**: `%applocaldata%\pyapp`
    - **MacOS**: `~/Library/Application Support/pyapp`
