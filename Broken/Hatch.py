import os
from pathlib import Path

from hatchling.metadata.plugin.interface import MetadataHookInterface


class BrokenHook(MetadataHookInterface):
    def update(self, metadata: dict) -> None:
        if (monorepo := os.environ.get("MONOREPO_ROOT")):
            monorepo = Path(monorepo)

            # Get the version from the main package
            exec((monorepo/"Broken"/"Version.py").read_text(), (ctx := {}))
            version = metadata["version"] = ctx["__version__"]

            # Replaces all list items inline
            def patch(items: list[str]) -> None:
                for (x, item) in enumerate(items):
                    item = item.replace("0.0.0", version)

                    # Pin versions on release binaries
                    if (os.environ.get("PYAPP_RELEASE", "0") == "1"):
                        item = item.replace("~=", "==")
                        item = item.replace(">=", "==")

                    items[x] = item

            # Patch all normal and optional dependencies
            list(map(patch, metadata.get("optional-dependencies", {}).values()))
            patch(metadata.get("dependencies", {}))
