# 🔥 From Source

!!! quote "**The most flexible** way to use the Projects | Latest features, editable, git clone repositories locally"

## ⚡️ Installing

!!! success "**Running** any of my Projects takes only **two commands**, anywhere"

!!! abstract "1. Select your Platform"
    === "✅ Windows"
        <div align="center">
            <img src="https://raw.githubusercontent.com/edent/SuperTinyIcons/master/images/svg/windows.svg" style="vertical-align: middle;  border-radius: 20%;" width="120">
        </div>

        **Open** some folder to download the code on **Windows Explorer**

        - Press ++ctrl+l++ , run `powershell` and execute:

        ```powershell
        irm https://brokensource.github.io/get.ps1 | iex
        ```

        ??? tip "Enable <a href="https://rye-up.com/guide/faq/#windows-developer-mode" target="_blank">Developer Mode</a> for a Better Experience"
            To have <a href="https://en.wikipedia.org/wiki/Symbolic_link" target="_blank"><b>Folder Shortcuts</b></a> (Symbolic Links) to the **Project's Workspace** Directory where the Source Code is (Data, Downloads, Config, etc), please enable <a href="https://rye-up.com/guide/faq/#windows-developer-mode" target="_blank"><b>Developer Mode</b></a> on **Windows Settings** per **Rye FAQ**

        ??? question "What is `irm` and `iex`?"
            - `irm` is an alias for `Invoke-RestMethod` to download the script
            - `iex` is an alias for `Invoke-Expression` to run the script
            - The pipe symbol `|` sends the first command's output to the second

    === "🐧 Linux"
        <div align="center">
            <img src="https://raw.githubusercontent.com/edent/SuperTinyIcons/master/images/svg/linux.svg" style="vertical-align: middle; border-radius: 20%;" width="120">
        </div>

        **Open** a **Terminal** on some directory and run

        ```shell
        /bin/bash -c "$(curl -sS https://brokensource.github.io/get.sh)"
        ```

    === "🍎 MacOS"
        <div align="center">
            <img src="https://raw.githubusercontent.com/edent/SuperTinyIcons/master/images/svg/apple.svg" style="vertical-align: middle; border-radius: 20%;" width="120">
        </div>

        **Open** a **Terminal** on some directory and run

        ```zsh
        /bin/bash -c "$(curl -sS https://brokensource.github.io/get.sh)"
        ```

    === "🧭 Manual"
        <div align="center">
            <img src="https://raw.githubusercontent.com/edent/SuperTinyIcons/master/images/svg/git.svg" style="vertical-align: middle; border-radius: 20%;" width="120">
        </div>

        - **Install** [**Git**](https://git-scm.com/downloads) and [**Rye**](https://rye-up.com) on your Platform

        ```bash title="Clone the Monorepo and all Submodules"
        git clone https://github.com/BrokenSource/BrokenSource --recurse-submodules --jobs 4
        ```
        ```bash title="Enter the Monorepo directory"
        cd BrokenSource
        ```
        ```bash title="Checkout all Submodules to the Master branch"
        git submodule foreach --recursive 'git checkout Master || true'
        ```
        ```bash title="Create the main Virtual Environment and Install Dependencies"
        rye sync
        ```
        ```bash title="Activate the main Virtual Environment"
        # Windows:
        .venv\Scripts\Activate.ps1 # PowerShell
        .venv\Scripts\Activate.bat # CMD

        # Linux and MacOS:
        source .venv/bin/activate # Bash
        source .venv/bin/activate.fish # Fish
        ```
        ```bash title="Start using any Project"
        broken
        shaderflow
        depthflow
        ```

<hr>

!!! abstract "2. Run any Project"
    **Now** simply run `broken` for a full Command List 🚀

    - Return the Project you want to run for extras

??? bug "Something Failed?"
    Try following the **Manual Instructions** Tab above, else [**Get in Touch**](contact.md) with us

<hr>

!!! tip "3. Next time, to use the Projects.."
    You just have to **Open a Terminal** on the <kbd>BrokenSource</kbd> Folder and [**Source the Virtual Environment**](https://docs.python.org/3/library/venv.html#how-venvs-work)

    - **Windows**:
        - +PowerShell: `.venv\Scripts\Activate.ps1`
        - +CMD: `.venv\Scripts\Activate.bat`
    - **Linux/MacOS**: `source .venv/bin/activate` or `source .venv/bin/activate.fish`

## 🌾 Using <a href="https://rye-up.com" target="_blank">Rye</a>

The Python Tooling I chose to Orchestrate the [**Monorepo**](https://github.com/BrokenSource/BrokenSource) is [**Rye**](https://rye-up.com)

- You'll probably **only** need to know a **single command**:

!!! note "Command: [`rye sync`](https://rye-up.com/guide/sync)"
    This creates the `.venv` and installs dependencies on `pyproject.toml`

    - It is automatically run, once, on the **Install Scripts** above before activating the venv

    - Run this on **dependencies updates** or not-my-code **Import Errors**

??? quote "Advantages of Rye on Monorepos"
    There are many Python toolings solutions out there, to name a few:

    - [Poetry](https://python-poetry.org), [Conda](https://conda.io/projects/conda/en/latest/user-guide/getting-started.html), [Pipenv](https://pipenv.pypa.io/en/latest), [PDM](https://pdm-project.org/en/latest), [pip-tools](https://pip-tools.readthedocs.io/en/stable), [pip](https://pip.pypa.io/en/stable/) itself.

    I was a Poetry hermit for a long time, until it became too inconvenient in a Monorepo environment. I partially blame Python itself for the Path Dependencies mess. Rye is no solution for that, but it does some other things in a smarter ways.

    - **Single Virtual Environment**:
        This saves a lot of **disk space**, **time**, and **micromanagement** in code

    - **Managed Python**:
        Doesn't depend on the user's Python installation, which can be problematic

    - **Syncing Files on Cloud**:
        Rye automatically makes your Cloud Provider [**ignore the `.venv` folder**](https://rye-up.com/guide/config/)

    !!! warning "Limitation"
        Rye currently has a limitation that `*.lock` files [**depends on the platform**](https://rye-up.com/guide/sync/#limitations)

        - You might get errors if running `rye sync` with `.lock` files generated on a different platform


## 🚀 Upgrading

## ♻️ Uninstalling
