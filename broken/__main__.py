import sys
from pathlib import Path
from typing import Annotated

from attr import define
from typer import Argument, Option

from broken import (
    BROKEN,
    BrokenPath,
    BrokenTorch,
    Environment,
    PlatformEnum,
    Tools,
    __version__,
    combinations,
    log,
    shell,
)
from broken.core.profiler import profiler
from broken.manager import ProjectManager


@define
class BrokenManager(ProjectManager):
    def __attrs_post_init__(self) -> None:
        self.find_projects(BROKEN.DIRECTORIES.REPO_PROJECTS)
        self.find_projects(BROKEN.DIRECTORIES.REPO_META)

        with self.cli.panel("🚀 Core"):
            self.cli.command(BrokenTorch.install)
            self.cli.command(self.insiders)
            self.cli.command(self.clone)

        with self.cli.panel("📦 Development"):
            self.cli.command(self.docker)
            self.cli.command(self.pypi)
            self.cli.command(self.upgrade)
            self.cli.command(self.clean)
            self.cli.command(self.sync)

        self.cli.command(self.tremeschin, hidden=True)

        self.cli.description = (
            "🚀 Broken Source Software Monorepo development manager script\n\n"
            "• Tip: run \"broken (command) --help\" for options on commands or projects ✨\n\n"
        )

    # ---------------------------------------------------------------------------------------------|
    # Core section

    def clone(self,
        repo:     Annotated[str,  Argument(help="URL of the Git Repository to Clone")],
        path:     Annotated[Path, Option("--path",     "-p", help="Path to clone the repository to")]=BROKEN.DIRECTORIES.REPO_META,
        recurse:  Annotated[bool, Option("--recurse",  "-r", help="Clone all submodules recursively")]=True,
        checkout: Annotated[str,  Option("--checkout", "-c", help="Checkout recursively branch or tag")]="main",
    ) -> Path:
        """🔗 Clone a project in the Meta directory"""
        from urllib.parse import urlparse

        # If the path isn't a repo, use the repository name
        if (path.exists()) and (not (Path(path)/".git").exists()):
            log.minor(f"Path {path} isn't a repository, appending the url name")
            path = (path/Path(urlparse(str(repo).removesuffix(".git")).path).stem)

        # Only attempt cloning if non-existent
        if (not path.exists()):
            with BrokenPath.pushd(path.parent, echo=False):
                shell("git", "clone", ("--recurse-submodules"*recurse), repo, path)

        # Not having .git is a failed clone
        if not (path/".git").exists():
            log.error(f"Invalid repository at ({path}), perhaps try removing it")
            exit(1)

        with BrokenPath.pushd(path, echo=False):
            shell("git", "submodule", "foreach", "--recursive", f"git checkout {checkout} || true")

        return path

    def insiders(self):
        """💎 Clone the Insiders repository (WIP, No content)"""
        self.clone("https://github.com/BrokenSource/Insiders", BROKEN.DIRECTORIES.INSIDERS)
        shell(Tools.uv, "sync", "--all-packages")

    def tremeschin(self):
        Tremeschin = (BROKEN.DIRECTORIES.REPO_META/"Tremeschin")
        self.clone("https://github.com/Tremeschin/Personal", Tremeschin)
        self.clone("https://github.com/Tremeschin/Private",  Tremeschin/"private")

    # ---------------------------------------------------------------------------------------------|
    # Core section

    def pypi(self,
        publish: Annotated[bool, Option("--publish", "-p", help="Publish the wheel to PyPI")]=False,
        output:  Annotated[Path, Option("--output",  "-o", help="Output directory for wheels")]=BROKEN.DIRECTORIES.BUILD_WHEELS,
        all:     Annotated[bool, Option("--all",     "-a", help="Build all projects")]=True,
    ) -> Path:
        """🧀 Build all project wheels and publish to PyPI"""
        BrokenPath.recreate(output)
        shell("uv", "build", "--wheel", ("--all"*all), "--out-dir", output)
        shell("uv", "publish", f"{output}/*.whl", skip=(not publish))
        return Path(output)

    def docker(self,
        push:  Annotated[bool, Option("--push",  "-p", help="Push built images to GHCR")]=False,
        clean: Annotated[bool, Option("--clean", "-c", help="Remove local images after pushing")]=False,
    ) -> None:
        """🐳 Build and push docker images for all projects"""
        from broken.core.pytorch import BrokenTorch

        for build in combinations(
            base_image=["ubuntu:24.04"],
            torch=BrokenTorch.docker(),
        ):
            # Warn: Must use same env vars as in docker-compose.yml
            Environment.set("BASE_IMAGE",    build.base_image)
            Environment.set("TORCH_VERSION", build.torch.number)
            Environment.set("TORCH_FLAVOR",  build.torch.flavor)
            shell("docker", "compose", "build")

            # Assumes all dockerfiles were built by docker compose, fails ok otherwise
            for dockerfile in BROKEN.DIRECTORIES.REPO_DOCKER.glob("*.dockerfile"):
                image:  str = dockerfile.stem
                latest: str = f"{image}:latest"
                flavor: str = build.torch.flavor

                # Tag a latest and versioned flavored images, optional push
                for tag in (f"latest-{flavor}", f"{__version__}-{flavor}"):
                    final: str = f"ghcr.io/brokensource/{image}:{tag}"
                    shell("docker", "tag",  latest, final)
                    shell("docker", "push", final,  skip=(not push))
                    shell("docker", "rmi",  final,  skip=(not clean))

                # No need for generic latest image
                shell("docker", "rmi", latest)

    def upgrade(self) -> None:
        """📦 Temporary solution to bump pyproject versions"""
        for project in self.projects:
            project.update()

    def clean(self) -> None:
        """🧹 Remove pycaches, common blob directories"""
        root = BROKEN.DIRECTORIES.REPOSITORY

        for path in root.rglob("__pycache__"):
            BrokenPath.remove(path)

        # Fixed known blob directories
        BrokenPath.remove(BROKEN.DIRECTORIES.REPO_RELEASES, confirm=True)
        BrokenPath.remove(BROKEN.DIRECTORIES.REPO_BUILD, confirm=True)
        BrokenPath.remove(root/".cache", confirm=True)

    def sync(self) -> None:
        """♻️  Synchronize common resources files across all projects"""
        root = (BROKEN.DIRECTORIES.REPOSITORY)
        dot_github = (root/".github")

        for project in self.projects:
            if (project.path/".github"/".nosync").exists():
                continue
            for file in BrokenPath.files(dot_github.rglob("*")):
                if (target := (project.path/file.relative_to(root))).exists():
                    BrokenPath.copy(file, target)

    def workflow_pyaket(self) -> None:
        for project in self.projects:
            for platform in PlatformEnum.all_host():
                project.compile(
                    platform=platform,
                    tarball=True
                )

# ------------------------------------------------------------------------------------------------ #

@profiler("broken")
def main():
    manager = BrokenManager()
    manager.cli(*sys.argv[1:])

if __name__ == "__main__":
    main()
