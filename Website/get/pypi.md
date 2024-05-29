---
title: PyPI
---

!!! quote "**The most reliable** way to use the Projects • As a dependency or direct module CLI"
    **Recommended for**: Basic users, Advanced users, Developers

## ⚡️ Installing

!!! success "All Projects are contained on this single dependency"

!!! abstract "Install the Package"
    === ":simple-python: Pip"
        ```shell title="Command"
        python -m pip install broken-source
        ```

    === ":simple-poetry: Poetry"
        ```shell title="Command"
        python -m poetry add broken-source
        ```

    === ":simple-rye: Rye"
        ```shell title="Command"
        rye add broken-source
        ```

    === ":simple-pdm: PDM"
        ```shell title="Command"
        pdm add broken-source
        ```

!!! info annotate "Some Projects or Optionals require specifying a <a href="https://pytorch.org/get-started/locally/" target="_blank"><b>PyTorch</b></a> flavor (1)"

1.  - No sense to me to force any of CUDA, CPU or ROCm
    - It's a large dependency and not always needed

## ⭐️ Usage
After **Installing** the Package, you can simply import it in your Code

```python
from DepthFlow import DepthFlowScene

depthflow = DepthFlowScene()
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
        python -m pip install --upgrade broken-source
        ```

    === ":simple-poetry: Poetry"
        ```shell title="Command"
        python -m poetry update broken-source
        ```

    === ":simple-rye: Rye"
        ```shell title="Command"
        rye add broken-source
        ```

    === ":simple-pdm: PDM"
        ```shell title="Command"
        pdm update broken-source
        ```

!!! tip "**Consider** staying on a fixed version if you need stability"
    Small or breaking parts of the code can be changed on any new release

    - Define `broken-source==X.Y.Z` in `pyproject.toml` to pin it


## ♻️ Uninstalling

!!! abstract "Simply **uninstall the package** on your Python Package Manager of choice"
    === ":simple-python: Pip"
        ```shell title="Command"
        python -m pip uninstall broken-source
        ```

    === ":simple-poetry: Poetry"
        ```shell title="Command"
        python -m poetry remove broken-source
        ```

    === ":simple-rye: Rye"
        ```shell title="Command"
        rye remove broken-source
        ```

    === ":simple-pdm: PDM"
        ```shell title="Command"
        pdm remove broken-source
        ```
