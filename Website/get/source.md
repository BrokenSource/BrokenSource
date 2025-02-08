---
title: Get/Source
---

!!! success "{++The most flexible++} way to use the Projects • Latest features, bugs, fixes, highly configurable."
    **Recommended for**: Basic++ users, contributors, developers.

## ⚡️ Installing

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
        <small>:material-arrow-right: Don't want to use it? Follow the [:simple-git: Manual](#installing-manual) tab above!</small>
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
        <small>:material-arrow-right: Don't want to use it? Follow the [:simple-git: Manual](#installing-manual) tab above!</small>
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
        <small>:material-arrow-right: Don't want to use it? Follow the [:simple-git: Manual](#installing-manual) tab above!</small>
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

??? success "See what [`get.sh`](https://github.com/BrokenSource/BrokenSource/blob/main/Website/get.sh) and [`get.ps1`](https://github.com/BrokenSource/BrokenSource/blob/main/Website/get.ps1) does"
    The content below is a **verbatim copy** of the current live script on this website
    === "(Windows) • get.ps1"
        <span/>
        ```powershell title="PowerShell script"
        {% include-markdown "get.ps1" %}
        ```
    === "(Linux and macOS) • get.sh"
        <span/>
        ```powershell title="Bash script"
        {% include-markdown "get.sh" %}
        ```

## ⭐️ Usage

Go to the project tab of your interest above and see the quickstart!

- You can also run the projects with: `uv run 'project'` directly

!!! tip "Next time, to use the projects"
    You just have to **Open a Terminal** on the <kbd>BrokenSource</kbd> directory and [**source the virtual environment**](https://docs.python.org/3/library/venv.html#how-venvs-work)

    - For that, run `Scripts/activate.sh` if on **Linux/MacOS** or `Scripts/activate.ps1` if on **Windows**
    - Or manually with :simple-linux: `source .venv/bin/activate` or :material-microsoft: `.venv\Scripts\Activate.ps1`

## 🚀 Upgrading

### Repositories

The installation script should've **initialized** and set all [**submodules**](https://git-scm.com/book/en/v2/Git-Tools-Submodules) to the **main branch**:

```bash title="Command"
git submodule foreach --recursive 'git checkout main || true'
```

After that, you can [**pull**](https://git-scm.com/docs/git-pull) the latest changes of all [**repositories**](https://git-scm.com/book/en/v2/Git-Basics-Getting-a-Git-Repository) with:

```bash title="Command"
git pull --recurse-submodules --jobs=4
```

!!! tip "If you have any local changes"
    - **Keep them**: Add [**`--rebase`**](https://git-scm.com/docs/git-rebase) to the command above
    - **Delete them**: Add `--force` to the command above

### Packages

The Python tooling I'm using to orchestrate the [**Monorepo**](https://github.com/BrokenSource/BrokenSource) is [**uv**](https://docs.astral.sh/uv/)

- You'll probably **only** need to know of a **single command**:

!!! note "Command: [`uv sync --all-packages`](https://docs.astral.sh/uv/)"
    This will update the venv and install any new dependencies

After that, just activate the venv and you're good to go!

## ♻️ Uninstalling

See the <a href="site:/get/uninstalling"><b>uninstalling</b></a> page
