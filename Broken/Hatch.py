import os
import runpy
from pathlib import Path

from hatchling.metadata.plugin.interface import MetadataHookInterface


class BrokenHook(MetadataHookInterface):
    def update(self, metadata: dict) -> None:
        monorepo = Path(__file__).parent.parent

        # Get the version from the main package
        context = runpy.run_path(monorepo/"Broken"/"Version.py")
        version = metadata["version"] = context["__version__"]

        # Replaces all list items inline
        def patch(items: list[str]) -> None:
            for (x, item) in enumerate(items):
                item = item.replace("0.0.0", version)
                item = item.replace(" ", "")

                # Replace git+ dependencies
                if ((git := "@git+") in item):
                    package = item.split(git)[0]
                    item = f"{package}=={version}"

                # Pin versions on release binaries
                if (os.environ.get("PYAPP_RELEASE", "0") == "1"):
                    item = item.replace("~=", "==")
                    item = item.replace(">=", "==")

                items[x] = item

        # Patch all normal and optional dependencies
        list(map(patch, metadata.get("optional-dependencies", {}).values()))
        patch(metadata.get("dependencies", {}))
