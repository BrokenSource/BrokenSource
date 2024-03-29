import sys
from pathlib import Path

import mkdocs_gen_files

TABS = (
    Path("Broken"),
    Path("Projects/ShaderFlow/ShaderFlow"),
    Path("Projects/DepthFlow/DepthFlow"),
    Path("Projects/Pianola/Pianola"),
    Path("Projects/SpectroNote/SpectroNote"),
)

# Add each Tab to sys path
for tab in TABS:
    sys.path.append(str(tab))

# Ignore directories
UNWANTED = (
    "Resources",
    "Community",
    "__",
)

nav = mkdocs_gen_files.Nav()

for root in TABS:
    for python in root.rglob("*.py"):
        if any(ban in str(python) for ban in UNWANTED):
            continue

        relative = python.relative_to(root)
        markdown = Path(root.name, relative).with_suffix(".md")
        nav[relative.parts] = str(markdown)

        with mkdocs_gen_files.open(markdown, "w") as file:
            file.write("::: " + ".".join(markdown.with_suffix("").parts))

with mkdocs_gen_files.open("Summary.md", "w") as nav_file:
    nav_file.writelines(nav.build_literate_nav())
