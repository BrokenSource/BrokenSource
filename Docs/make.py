import sys
from pathlib import Path

import mkdocs_gen_files

UNWANTED = (
    "Resources",
    "Community",
    "__",
)

# List of all modules to generate docs for on the path "$name/{reference,resources,*}/*"
# Note: The order is important, Broken must be first to not be included on itself
PROJECTS = (
    Path("Broken"),
    Path("Projects/ShaderFlow/ShaderFlow"),
    Path("Projects/DepthFlow/DepthFlow"),
    Path("Projects/Pianola/Pianola"),
    Path("Projects/SpectroNote/SpectroNote"),
)

# Make each project's root findable
sys.path += map(str, PROJECTS)

for ROOT in PROJECTS:
    PROJECT_NAME = ROOT.name

    for python in reversed(list(ROOT.rglob("*.py"))):

        # Skip unwanted files
        if any(ban in str(python) for ban in UNWANTED):
            continue

        # Get the module import statement and url path
        module   = python.relative_to(ROOT).with_suffix("")
        markdown = Path(ROOT.name, "reference", module).with_suffix(".md")
        url_path = str(markdown).lower()

        # Write the virtual markdown file with documentation
        with mkdocs_gen_files.open(url_path, "w") as file:
            file.write('\n'.join((
                f"# {module.name}",
                "",
                "!!! warning",
                "    Better **Docstrings** and **Formatting** are being **worked on** for the **Code References**",
                "",
                f"::: {'.'.join(module.parts)}",
            )))

    # # Virtually copy all of Project's stuff to

    # This project's own paths
    WHAT_WHERE = (
        ((ROOT/"Resources"), "resources"),
        ((ROOT.parent/"Docs"), ""),
    )

    WANT_SUFFIXES = (".md", ".png", ".jpg", ".svg")

    # Rebase "$what/*" to "$name/$where/*" local documentation
    for (what, where) in WHAT_WHERE:
        for real in what.rglob("*"):

            # Skip "bad" files
            if real.is_dir():
                continue
            if real.suffix not in WANT_SUFFIXES:
                continue

            # Avoid writing Broken/Docs to itself
            BASE = PROJECT_NAME.lower().replace("broken", "")
            virtual = Path(BASE, where, str(real.relative_to(what)).lower())

            print(f"• Copying ({real}) -> ({virtual})")

            with mkdocs_gen_files.open(virtual, "wb") as file:
                file.write(real.read_bytes())
