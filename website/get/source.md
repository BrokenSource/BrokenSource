---
icon: material/git
---

!!! abstract ""
    === ":material-microsoft: Windows"
        <div align="center">
            <img class="os-logo" src="https://raw.githubusercontent.com/edent/SuperTinyIcons/master/images/svg/windows.svg">
            <div><b>Open</b> a folder to download the code on <b>Windows Explorer</b></div>
            <div>Press ++ctrl+l++ , run `powershell` and execute:</div>
        </div>
        ```powershell
        irm https://brokensrc.dev/get.ps1 | iex
        ```
        <small><b>How it works:</b> `irm` downloads the script, `iex` executes it directly</small>
        <br>
        <small>:material-arrow-right: Don't want to use it? Follow the [:simple-git: Manual](#manual) tab above!</small>
    === ":simple-linux: Linux"
        <div align="center">
            <img class="os-logo" src="https://raw.githubusercontent.com/edent/SuperTinyIcons/master/images/svg/linux.svg">
            <div><b>Open</b> a <b>Terminal</b> on some directory and run:</div>
            <div><sup></sup></div>
        </div>
        ```shell
        /bin/bash -c "$(curl -sS https://brokensrc.dev/get.sh)"
        ```
        <small><b>How it works:</b> `curl` downloads the script, `bash` executes it directly</small>
        <br>
        <small>:material-arrow-right: Don't want to use it? Follow the [:simple-git: Manual](#manual) tab above!</small>
    === ":simple-apple: MacOS"
        <div align="center">
            <img class="os-logo" src="https://raw.githubusercontent.com/edent/SuperTinyIcons/master/images/svg/apple.svg">
            <div><b>Open</b> a <b>Terminal</b> on some directory and run:</div>
            <div><sup></sup></div>
        </div>
        ```zsh
        /bin/bash -c "$(curl -sS https://brokensrc.dev/get.sh)"
        ```
        <small><b>How it works:</b> `curl` downloads the script, `bash` executes it directly</small>
        <br>
        <small>:material-arrow-right: Don't want to use it? Follow the [:simple-git: Manual](#manual) tab above!</small>
    === ":simple-git: Manual"
        <div align="center"><img class="os-logo" src="https://raw.githubusercontent.com/edent/SuperTinyIcons/master/images/svg/git.svg"></div>

        - **Install** [**git**](https://git-scm.com/downloads) and [**uv**](https://docs.astral.sh/uv/) on your Platform

        ```bash title="Download the code"
        git clone https://github.com/BrokenSource/BrokenSource --recurse-submodules
        ```
        ```bash title="Enter the directory"
        cd BrokenSource
        ```
        ```bash title="Ensure submodules are on main"
        git submodule foreach --recursive 'git checkout main || true'
        ```
        ```bash title="Create venv and install dependencies"
        uv sync --all-packages
        ```
        === "Directly with uv"
            <span/>

            ```bash title="Start using any Project"
            uv run shaderflow
            uv run depthflow
            uv run broken
            ```
        === "Traditional method"
            <span/>

            ```bash title="Activate the venv"
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

## ♻️ Uninstalling

Apart from deleting the `BrokenSource` folder where you cloned the code,

--8<--
include/uninstall/workspace.md
include/uninstall/models.md
include/uninstall/wheels.md
--8<--
