# 🔥 Source Code

!!! abstract "Select your Platform"
    === "💠 Windows"
        <div align="center">
            <img src="https://raw.githubusercontent.com/edent/SuperTinyIcons/master/images/svg/windows.svg" style="vertical-align: middle;" width="82">
        </div>

        **Open** some folder to download the code on **Windows Explorer**

        - Press <kbd>Ctrl+L</kbd> , run `powershell` and execute:

        ```powershell
        irm https://brokensource.github.io/get.ps1 | iex
        ```
        ??? tip "Enable <a href="https://rye-up.com/guide/faq/#windows-developer-mode">Developer Mode</a> for a Better Experience"
            To have [**Folder Shortcuts**](https://en.wikipedia.org/wiki/Symbolic_link) (Symbolic Links) to the **Project's Workspace** Directory (Data, Downloads, Config, etc) where the Source Code is, please enable [**Developer Mode**](https://rye-up.com/guide/faq/#windows-developer-mode) on **Windows Settings** per **Rye FAQ**

    === "🐧 Linux"
        <div align="center">
            <img src="https://raw.githubusercontent.com/edent/SuperTinyIcons/master/images/svg/linux.svg" style="vertical-align: middle;" width="82">
        </div>

        **Open** a **Terminal** on some directory and run

        ```shell
        /bin/bash -c "$(curl -sS https://brokensource.github.io/get.sh)"
        ```

    === "🍎 MacOS"
        <div align="center">
            <img src="https://raw.githubusercontent.com/edent/SuperTinyIcons/master/images/svg/apple.svg" style="vertical-align: middle;" width="82">
        </div>

        **Open** a **Terminal** on some directory and run

        ```zsh
        /bin/bash -c "$(curl -sS https://brokensource.github.io/get.sh)"
        ```

    === "🧭 Manual"
        <div align="center">
            <img src="https://raw.githubusercontent.com/edent/SuperTinyIcons/master/images/svg/git.svg" style="vertical-align: middle;" width="82">
        </div>

        - **Install** [**Git**](https://git-scm.com/downloads) and [**Rye**](https://rye-up.com) on your Platform

        !!! warning "Windows"
            Prefer using a **PowerShell** than the **Command Prompt** (CMD)

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
        soruce .venv/bin/activate.fish # Fish
        ```
        ```bash title="Start using any Project"
        broken
        shaderflow
        depthflow
        ```

**And done**, now run `broken` for a Command List 🚀

<br>

# 🌾 <b>Using <a href="https://rye-up.com">Rye</a></b>

You'll probably **only** need to know of **two commands**:

- [`rye sync`](https://rye-up.com/guide/sync): This creates the `.venv` and installs dependencies on `pyproject.toml`
- [`rye self update`](https://rye-up.com/guide/installation/#updating-rye): This updates Rye itself to the newest features

!!! success "Single Virtual Environment"
    This saves a lot of **disk space**, **time**, and **micromanagement** in code

!!! success "Managed Python"
    We don't depend anymore on the user's Python installation, which can be problematic on certain platforms


!!! success "Syncing Files on Cloud"
    Rye automatically makes your Cloud Provider [**ignore the `.venv` folder**](https://rye-up.com/guide/config/)

!!! warning "Limitation"
    Rye currently has a limitation that `*.lock` files [**depends on the platform**](https://rye-up.com/guide/sync/#limitations)

    - You might get errors if running `rye sync` with `.lock` files generated on a different platform
