---
title: Get/PyPI
---

!!! success "{++The most reliable++} way to use the Projects • Run the package commands or as a python import."
    **Recommended for**: Basic users, advanced users, developers.

## ⚡️ Installing

!!! abstract ""
    === ":simple-python: Pip"
        ```shell title="Command"
        python -m pip install {package}
        ```

    === ":simple-poetry: Poetry"
        ```shell title="Command"
        python -m poetry add {package}
        ```

    === ":simple-rye: Rye"
        ```shell title="Command"
        rye add {package} --pin equal
        ```

    === ":simple-pdm: PDM"
        ```shell title="Command"
        pdm add {package}
        ```

    ...where **`{package}`** is the **name of the project** you want to install:

    - [`depthflow`](https://pypi.org/project/depthflow/), [`shaderflow`](https://pypi.org/project/shaderflow/), [`broken-source`](https://pypi.org/project/broken-source/), [`pianola`](https://pypi.org/project/pianola/), [`spectronote`](https://pypi.org/project/spectronote/), [`turbopipe`](https://pypi.org/project/turbopipe/)

    <hr>

    ✅ Preferably pin the package version `==x.y.z` on `pyproject.toml` for stability!

??? warning "A **Python 64 bits** interpreter is required"
    **Reason**: Some or many dependencies don't have precompiled wheels or will fail to compile for 32 bits[^1]

    - ✅ Check your installation with: `python -c "import struct; print(struct.calcsize('P') * 8)"`
    - This is specially important on **Windows** as [**python.org**](https://www.python.org/) front page might link to 32 bit versions

    [^1]: Most notably `imgui`, and moderate chance of issues with `torch`, `numpy`, etc.

## ⭐️ Usage

Go to the project tab of your interest above and see the quickstart!

## 🚀 Upgrading

!!! abstract "Simply upgrade the python dependency"
    === ":simple-python: Pip"
        ```shell title="Command"
        python -m pip install --upgrade {package}
        ```

    === ":simple-poetry: Poetry"
        ```shell title="Command"
        python -m poetry update {package}
        ```

    === ":simple-rye: Rye"
        ```shell title="Command"
        rye add {package}
        ```

    === ":simple-pdm: PDM"
        ```shell title="Command"
        pdm update {package}
        ```

## ♻️ Uninstalling

See the <a href="site:/get/uninstalling"><b>Uninstalling</b></a> page
