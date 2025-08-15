---
icon: material/language-python
---

!!! abstract ""
    === ":simple-astral: Directly"
        <div align="center">
          <img class="os-logo" src="https://raw.githubusercontent.com/edent/SuperTinyIcons/master/images/svg/python.svg">
          <div>
          </div>
        </div>
        <br>
        1. Open a Terminal and install [astral-sh/uv](https://docs.astral.sh/uv/) - a fast python and project manager:
        === ":material-microsoft: Windows"
            Using [WinGet](https://docs.microsoft.com/en-us/windows/package-manager/winget/), Microsoft's official package manager:
            ```sh title=""
            winget install --id=astral-sh.uv -e
            ```
        === ":simple-linux: Linux"
            Install from your **distro package manager**, or universally:
            ```sh title=""
            curl -LsSf https://astral.sh/uv/install.sh | sh
            ```
        === ":simple-apple: MacOS"
            Using [Homebrew](https://brew.sh/), a popular package manager for MacOS:
            ```sh title=""
            brew install uv
            ```
        <hr>
        2. Run any [project](https://pypi.org/user/Tremeschin/) simply with:
        ```sh title=""
        uvx (project) (args)
        ```
        :material-arrow-right: For example `uvx depthflow gradio`
    === ":simple-python: Package"
        <div align="center">
          <img class="os-logo" src="https://raw.githubusercontent.com/edent/SuperTinyIcons/master/images/svg/python.svg">
          <div>
          </div>
        </div>
        <br>
        Add any [project](https://pypi.org/user/Tremeschin/) to your `pyproject.toml` or install inside a venv, write and run any scripts.

        - Check the examples tabs at the top or the repository for usage!

!!! note "Preferably pin the package version `==x.y.z` anywhere for stability!"

## ♻️ Uninstalling

Apart from uninstalling the package and/or deleting the virtual environment:

--8<--
include/uninstall/workspace.md
include/uninstall/models.md
include/uninstall/wheels.md
--8<--
