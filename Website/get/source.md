---
title: Get/Source
---

!!! quote "**The most flexible** way to use the Projects • Latest features, bugs, fixes, git clone"
    **Recommended for**: Advanced users, Contributors, Developers

## ⚡️ Installing

!!! success "Running any of my Projects takes only two commands"

!!! abstract "1. Select your Platform"
    === ":material-microsoft: Windows"
        <div align="center"><img src="https://raw.githubusercontent.com/edent/SuperTinyIcons/master/images/svg/windows.svg" style="vertical-align: middle; border-radius: 20%" width="80"></div>

        **Open** some folder to download the code on **Windows Explorer**

        - Press ++ctrl+l++ , run `powershell` and execute:

        ```powershell
        # What it does: 'irm' downloads, 'iex' executes, '|' links the two
        irm https://brokensrc.dev/get.ps1 | iex
        ```

        <hr>

        ??? success "Read what `get.ps1` does"
            ```powershell
            {% include-markdown "get.ps1" %}
            ```

        ??? quote "Enable <a href="https://rye.astral.sh/guide/faq/#windows-developer-mode" target="_blank">Developer Mode</a> for a Better Experience"
            To have <a href="https://en.wikipedia.org/wiki/Symbolic_link" target="_blank"><b>Folder Shortcuts</b></a> (Symbolic Links) to the **Project's Workspace** Directory (Data, Downloads, Config, etc) where the Source Code is, please enable <a href="https://rye.astral.sh/guide/faq/#windows-developer-mode" target="_blank"><b>Developer Mode</b></a> on **Windows Settings** per **Rye FAQ**.

            - This will also drastically speed up Virtual Environment creation

    === ":simple-linux: Linux"
        <div align="center"><img src="https://raw.githubusercontent.com/edent/SuperTinyIcons/master/images/svg/linux.svg" style="vertical-align: middle; border-radius: 20%" width="80"></div>

        **Open** a **Terminal** on some directory and run

        ```shell title="Terminal"
        /bin/bash -c "$(curl -sS https://brokensrc.dev/get.sh)"
        ```

        <hr>

        ??? success "Read what `get.sh` does"
            ```powershell
            {% include-markdown "get.sh" %}
            ```

    === ":simple-apple: MacOS"
        <div align="center"><img src="https://raw.githubusercontent.com/edent/SuperTinyIcons/master/images/svg/apple.svg" style="vertical-align: middle; border-radius: 20%;" width="80"></div>

        **Open** a **Terminal** on some directory and run

        ```zsh title="Terminal"
        /bin/bash -c "$(curl -sS https://brokensrc.dev/get.sh)"
        ```

        <hr>

        ??? success "Read what `get.sh` does"
            ```powershell
            {% include-markdown "get.sh" %}
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

<hr>

??? bug "Something Failed?"
    Try following the **Manual Instructions** Tab above, else [**Get in Touch**](../about/contact.md) with me, preferably Discord

    - Please, show some effort or try solving the problem first, often you'll get it :)

<hr>

!!! abstract "2. Run any Project"
    **Now**, simply run `broken` for a full command list, and to check if the setup is ok 🚀

    - Start using projects directly, like `depthflow main`, `shaderflow`, etc
    - Return the **project** you're interested for **further instructions**

<hr>

!!! tip "Next time, to use the projects"
    You just have to **Open a Terminal** on the <kbd>BrokenSource</kbd> directory and [**Source the Virtual Environment**](https://docs.python.org/3/library/venv.html#how-venvs-work)

    - For that, run `Scripts/activate.sh` if on **Linux/MacOS** or `Scripts/activate.ps1` if on **Windows**
    - Or manually with `source .venv/bin/activate` or `.venv\Scripts\Activate.ps1`

<br>

## 🚀 Upgrading

<hr>

### 🌱 Repositories

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

<hr>

### 🌱 Packages

The Python tooling I'm using to orchestrate the [**Monorepo**](https://github.com/BrokenSource/BrokenSource) is [**Rye**](https://rye.astral.sh/)

- You'll probably **only** need to know of a **single command**:

!!! note "Command: [`rye sync`](https://rye.astral.sh/guide/sync)"
    This will **update** the **Virtual Environment** and **install** any new **dependencies**

## ♻️ Uninstalling
See the <a href="site:uninstalling"><b>Uninstalling</b></a> page
