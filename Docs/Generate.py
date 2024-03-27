from pathlib import Path

import mkdocs_gen_files

nav = mkdocs_gen_files.Nav()
root = Path("Broken")

for path in root.glob("**/*.py"):
    if ("__" in str(path)):
        continue
    markdown = Path("Source", path.relative_to(root)).with_suffix(".md")
    nav[path.parts] = str(markdown)
    with mkdocs_gen_files.open(markdown, "w") as file:
        file.write("::: " + ".".join(path.with_suffix("").parts))

with mkdocs_gen_files.open("Summary.md", "w") as nav_file:
    nav_file.writelines(nav.build_literate_nav())
