from pathlib import Path

import mkdocs_gen_files

nav = mkdocs_gen_files.Nav()

TABS = (
    Path("Broken"),
    Path("Projects/ShaderFlow"),
    Path("Projects/DepthFlow"),
    Path("Projects/Pianola"),
    Path("Projects/SpectroNote"),
)

for path in TABS:
    name = path.name

    for python in path.glob("**/*.py"):
        if ("__" in str(python)):
            continue
        if ("Resources" in str(python)):
            continue

        relative = python.relative_to(path)
        markdown = Path(name, relative).with_suffix(".md")
        nav[python.parts] = str(markdown)

        with mkdocs_gen_files.open(markdown, "w") as file:
            file.write("::: " + ".".join(python.with_suffix("").parts))

with mkdocs_gen_files.open("Summary.md", "w") as nav_file:
    nav_file.writelines(nav.build_literate_nav())
