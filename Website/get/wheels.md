---
title: Get/PyPI
---

<style>
    /* More well-defined cards */
    .cards > ul > li {
        border: 2px solid var(--md-typeset-table-color) !important;
        padding: 0.5em !important;
    }
</style>

✅ Use the projects as dependencies or command line tools!

!!! abstract ""
    === ":simple-python: PyPI"
        <div align="center">
            <img class="os-logo" src="https://raw.githubusercontent.com/edent/SuperTinyIcons/master/images/svg/python.svg">
            <div>
                <b>Wheels</b> from the Python Package Index (PyPI)
            </div>
        </div>

        :material-arrow-right: Download wheels from all the projects:

        <div class="grid cards" markdown>

        -   [**🌊 DepthFlow**](https://pypi.org/project/depthflow/){:target='_blank'}
        -   [**🔥 ShaderFlow**](https://pypi.org/project/shaderflow/){:target='_blank'}
        -   [**🎹 Pianola**](https://pypi.org/project/pianola/){:target='_blank'}
        -   [**🎧 SpectroNote**](https://pypi.org/project/pianola/){:target='_blank'}
        -   [**🌀 TurboPipe**](https://pypi.org/project/turbopipe){:target='_blank'}
        -   [**❤️‍🩹 Broken**](https://pypi.org/project/broken-source){:target='_blank'}

        </div>

        ✅ Preferably pin the package version `==x.y.z` on `pyproject.toml` for stability!

!!! heart "**Unlimited** power for you now, [**support**](site:/about/sponsors) my work to keep it alive!"

You can now import the projects in your scripts or type their name for a command line:

- Check the project's repository for a <kbd>Examples</kbd> folder with Python scripts
- Run directly e.g. `shaderflow basic main` to open a demo shader scene

:material-arrow-right: See the project's website page for documentation and usage!

## 📦 Directly with uv

> Check their [Tools/uv](https://docs.astral.sh/uv/concepts/tools/) documentation for extra info!

You can run the latest stable release of project with `uvx` like so:

```sh title="Command"
uvx shaderflow basic main
```

Or the latest development version directly from git main:

```sh title="Command"
uvx --from git+https://github.com/BrokenSource/DepthFlow depthflow gradio
```

## ♻️ Uninstalling

Apart from uninstalling the package and/or deleting the virtual environment:

--8<--
include/uninstall/workspace.md
include/uninstall/models.md
include/uninstall/wheels.md
--8<--
