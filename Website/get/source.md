---
title: Get/Source
---

!!! success "{++The most flexible++} way to use the Projects • Latest features, bugs, fixes, highly configurable."
    **Recommended for**: Basic++ users, contributors, developers.

## ⚡️ Installing

!!! abstract ""
    === ":material-microsoft: Windows"
        <div align="center">
            <img src="https://raw.githubusercontent.com/edent/SuperTinyIcons/master/images/svg/windows.svg" style="vertical-align: middle; border-radius: 20%" width="80">
            <div><b>Open</b> a folder to download the code on <b>Windows Explorer</b>,</div>
            <div>Press ++ctrl+l++ , run `powershell` and execute:</div>
        </div>
        ```powershell
        # How it works: 'irm' downloads, 'iex' executes, '|' links the two
        irm https://brokensrc.dev/get.ps1 | iex
        ```
    === ":simple-linux: Linux"
        <div align="center">
            <img src="https://raw.githubusercontent.com/edent/SuperTinyIcons/master/images/svg/linux.svg" style="vertical-align: middle; border-radius: 20%" width="80">
            <div><b>Open</b> a <b>Terminal</b> on some directory and run:</div>
            <div><sup></sup></div>
        </div>
        ```shell title="Terminal"
        # Curl downloads the script, sends to bash for executing it
        /bin/bash -c "$(curl -sS https://brokensrc.dev/get.sh)"
        ```
    === ":simple-apple: MacOS"
        <div align="center">
            <img src="https://raw.githubusercontent.com/edent/SuperTinyIcons/master/images/svg/apple.svg" style="vertical-align: middle; border-radius: 20%;" width="80">
            <div><b>Open</b> a <b>Terminal</b> on some directory and run:</div>
            <div><sup></sup></div>
        </div>
        ```zsh title="Terminal"
        # Curl downloads the script, sends to bash for executing it
        /bin/bash -c "$(curl -sS https://brokensrc.dev/get.sh)"
        ```
    === ":simple-git: Manual"
        <div align="center"><img src="https://raw.githubusercontent.com/edent/SuperTinyIcons/master/images/svg/git.svg" style="vertical-align: middle; border-radius: 20%" width="80"></div>

        - **Install** [**Git**](https://git-scm.com/downloads) and [**Rye**](https://rye.astral.sh/) on your Platform

        ```bash title="Clone the Monorepo and all Submodules"
        git clone https://github.com/BrokenSource/BrokenSource --recurse-submodules --jobs 4
        ```
        ```bash title="Enter the Monorepo directory"
        cd BrokenSource
        ```
        ```bash title="Checkout all Submodules to the main branch"
        git submodule foreach --recursive 'git checkout main || true'
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

??? success "Read what the install scripts does [`get.sh`](https://github.com/BrokenSource/BrokenSource/blob/main/Website/get.sh), [`get.ps1`](https://github.com/BrokenSource/BrokenSource/blob/main/Website/get.ps1)"
    The content below is a **verbatim copy** of the current live script on this website
    === "(Windows) • get.ps1"
        ```powershell title=""
        {% include-markdown "get.ps1" %}
        ```
    === "(Linux and macOS) • get.sh"
        ```powershell title=""
        {% include-markdown "get.sh" %}
        ```

## ⭐️ Usage

Go to the project tab of your interest above and see the quickstart!

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

The Python tooling I'm using to orchestrate the [**Monorepo**](https://github.com/BrokenSource/BrokenSource) is [**Rye**](https://rye.astral.sh/)

- You'll probably **only** need to know of a **single command**:

!!! note "Command: [`rye sync`](https://rye.astral.sh/guide/sync)"
    This will **update** the **Virtual Environment** and **install** any new **dependencies**

After that, just activate the venv and you're good to go!

## ♻️ Uninstalling

See the <a href="site:get/uninstalling"><b>uninstalling</b></a> page
