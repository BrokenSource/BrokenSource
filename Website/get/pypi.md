---
title: Get/PyPI
---

!!! success "{++The most reliable++} way to use the Projects • Run the package commands or as a python import."
    **Recommended for**: Basic users, advanced users, developers.

## ⚡️ Installing

!!! abstract ""
    === ":simple-python: Pip"
        Follow their [quick start](https://pip.pypa.io/en/stable/getting-started/){:target='_blank'}, install packages with:

        ```console title=""
        python3 -m pip install {package}
        ```

    === ":simple-astral: uv"
        Follow their [quick start](https://docs.astral.sh/uv/getting-started/){:target='_blank'}, install packages with:

        ```console title=""
        uv add {package}
        ```

    === ":simple-poetry: Poetry"
        Follow their [quick start](https://python-poetry.org/docs/){:target='_blank'}, install packages with:

        ```console title=""
        poetry add {package}
        ```

    === ":simple-rye: Rye"
        Follow their [quick start](https://rye.astral.sh/){:target='_blank'}, install packages with:

        ```console title=""
        rye add {package} --pin equal
        ```

    === ":simple-pdm: PDM"
        Follow their [quick start](https://pdm-project.org/en/latest/){:target='_blank'}, install packages with:

        ```console title=""
        pdm add {package}
        ```

!!! quote ""
    ...where **`{package}`** is the **name of the project** you want to install:

    [`depthflow`](https://pypi.org/project/depthflow/), [`shaderflow`](https://pypi.org/project/shaderflow/), [`broken-source`](https://pypi.org/project/broken-source/), [`pianola`](https://pypi.org/project/pianola/), [`spectronote`](https://pypi.org/project/spectronote/), [`turbopipe`](https://pypi.org/project/turbopipe/)

    <hr>

    ✅ Preferably pin the package version `==x.y.z` on `pyproject.toml` for stability!

??? warning "**Python 64 bits** interpreter is required"
    **Reason**: Some or many dependencies don't have precompiled wheels or will fail to compile for 32 bits

    - ✅ Check your installation with: `python3 -c "import struct; print(struct.calcsize('P') * 8)"`
    - This is specially important on **Windows** as [**python.org**](https://www.python.org/) front page might link to 32 bit versions

## ⭐️ Usage

Go to the project tab of your interest above and see the quickstart!

## 🚀 Upgrading

Simply upgrade the python dependency:

!!! abstract ""
    === ":simple-python: Pip"
        <span/>

        ```console title=""
        python3 -m pip install --upgrade {package}
        ```

    === ":simple-astral: uv"
        <span/>

        ```console title=""
        uv add {package}
        ```

    === ":simple-poetry: Poetry"
        <span/>

        ```console title=""
        poetry update {package}
        ```

    === ":simple-rye: Rye"
        <span/>

        ```console title=""
        rye add {package}
        ```

    === ":simple-pdm: PDM"
        <span/>

        ```console title=""
        pdm update {package}
        ```

## ♻️ Uninstalling

See the <a href="site:/get/uninstalling"><b>Uninstalling</b></a> page
