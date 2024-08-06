---
title: Get/PyPI
---

!!! quote "**The most reliable** way to use the Projects • As a dependency or direct module CLI"
    **Recommended for**: Basic users, Advanced users, Developers

## ⚡️ Installing

!!! success "All Projects have their own independent package"

!!! abstract "Install the Package"
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
        rye add {package}
        ```

    === ":simple-pdm: PDM"
        ```shell title="Command"
        pdm add {package}
        ```

    ...where **`{package}`** is the **name of the project** you want to install:

    - [`depthflow`](https://pypi.org/project/depthflow/), [`shaderflow`](https://pypi.org/project/shaderflow/), [`broken-source`](https://pypi.org/project/broken-source/), [`pianola`](https://pypi.org/project/pianola/), [`spectronote`](https://pypi.org/project/spectronote/), [`turbopipe`](https://pypi.org/project/turbopipe/)

## ⭐️ Usage
After **Installing** the Package, you can simply import it in your Code

```python title="Example with <a href='https://pypi.org/project/depthflow/' target='_blank'><b>DepthFlow</b></a>"
from DepthFlow import DepthScene

depthflow = DepthScene()
depthflow.input(image="./background.png")
depthflow.main(output="./video.mp4", ...)
```

.. or run its command line interface:

```shell title="Terminal"
# You can also use 'depthflow' instead of 'python -m DepthFlow'
python -m DepthFlow input -i ./background.png main -o ./video.mp4
```

- **For more,** go to the project tab of your interest above and see its usage

## 🚀 Upgrading

!!! abstract "Simply **upgrade the dependency** on your Python project"
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

!!! tip "**Consider** staying on a fixed version if you need stability"
    Small or breaking parts of the code can be changed on any new release

    - Define `{package}==X.Y.Z` in `pyproject.toml` to pin it


## ♻️ Uninstalling
See the <a href="site:get/uninstalling"><b>Uninstalling</b></a> page
