import contextlib
import ctypes
import functools
import itertools
import os
import shutil
from collections.abc import Generator, Iterable
from enum import Enum
from pathlib import Path
from typing import Any, Optional, Union

import click
from loguru import logger

import broken
import broken.project
from broken.enumx import BrokenEnum
from broken.envy import Environment
from broken.system import BrokenPlatform
from broken.types import FileExtensions
from broken.utils import StaticClass, denum, flatten, shell


class ShutilFormat(BrokenEnum):
    Zip   = "zip"
    Tar   = "tar"
    TarGz = "tar.gz"
    TarBz = "tar.bz2"
    TarXz = "tar.xz"


class BrokenPath(StaticClass):

    def get(
        *parts: Any,
        absolute: bool=True,
        exists: bool=False,
        raises: bool=False,
    ) -> Optional[Path]:

        # Return None if all parts are falsy
        if not (parts := list(filter(None, parts))):
            return None

        # Create instance as normal
        path = Path(*map(str, parts))

        # Note that we do not want to .resolve() as having symlink paths _can_ be wanted
        path = (path.expanduser().absolute() if absolute else path)

        # Handle existence requirements
        if (raises and not path.exists()):
            raise FileNotFoundError(f"Path ({path}) doesn't exist")
        if (exists and not path.exists()):
            return None

        return path

    def copy(src: Path, dst: Path, *, echo=True) -> Path:
        src, dst = BrokenPath.get(src), BrokenPath.get(dst)
        BrokenPath.mkdir(dst.parent)
        if src.is_dir():
            logger.info(f"Copy ({src})\n   → ({dst})", echo=echo)
            shutil.copytree(src, dst)
        else:
            logger.info(f"Copy ({src})\n   → ({dst})", echo=echo)
            shutil.copy2(src, dst)
        return dst

    def move(src: Path, dst: Path, *, echo=True) -> Path:
        src, dst = BrokenPath.get(src), BrokenPath.get(dst)
        logger.info(f"Moving ({src})\n     → ({dst})", echo=echo)
        shutil.move(src, dst)
        return dst

    def remove(path: Path, *, confirm=False, echo=True) -> Path:

        # Already removed or doesn't exist
        if not (path := BrokenPath.get(path)).exists():
            return path

        logger.info(f"Removing Path ({path})", echo=echo)

        # Safety: Must not be common
        if path in (Path.cwd(), Path.home()):
            logger.error(f"Avoided catastrophic failure by not removing ({path})")
            exit(1)

        # Symlinks are safe to remove
        if path.is_symlink():
            path.unlink()
            return path

        from rich.prompt import Prompt

        # Confirm removal: directory contains data
        if confirm and Prompt.ask(
            prompt=f"• Confirm removing path ({path})",
            choices=["y", "n"], default="n",
        ) == "n":
            return path

        # Remove the path
        if path.is_dir():
            shutil.rmtree(path, ignore_errors=True)
        else:
            path.unlink()

        return path

    def mkdir(path: Path, parent: bool=False, *, echo=True) -> Path:
        """Creates a directory and its parents, fail safe™"""
        path = BrokenPath.get(path)
        make = (path.parent if parent else path)
        if make.exists():
            return path
        logger.info(f"Creating directory {make}", echo=echo)
        make.mkdir(parents=True, exist_ok=True)
        return path

    def recreate(path: Path, *, echo=True) -> Path:
        """Delete and re-create a directory"""
        return BrokenPath.mkdir(BrokenPath.remove(path, echo=echo), echo=echo)

    @contextlib.contextmanager
    def pushd(path: Path, *, echo: bool=True) -> Generator[Path, None, None]:
        """Change directory, then change back when done"""
        path = BrokenPath.get(path)
        cwd = os.getcwd()
        logger.minor(f"Enter directory ({path})", echo=echo)
        os.chdir(path)
        yield path
        logger.minor(f"Leave directory ({path})", echo=echo)
        os.chdir(cwd)

    def symlink(virtual: Path, real: Path, *, echo: bool=True) -> Path:
        """Symlink 'virtual' file to -> 'real' true path"""
        logger.info(f"Symlinking ({virtual})\n→ ({real})", echo=echo)

        # Return if already symlinked
        if (BrokenPath.get(virtual) == BrokenPath.get(real)):
            return virtual

        # Make Virtual's parent directory
        BrokenPath.mkdir(virtual.parent)

        # Remove old symlink if it points to a non existing directory
        if virtual.is_symlink() and (not virtual.resolve().exists()):
            virtual.unlink()

        # Virtual doesn't exist, ok to create
        elif not virtual.exists():
            pass

        # File exists and is a symlink - safe to remove
        elif virtual.is_symlink():
            virtual.unlink()

        # Virtual is a directory and not empty
        elif virtual.is_dir() and (not os.listdir(virtual)):
            BrokenPath.remove(virtual, echo=False)

        else:
            if click.confirm('\n'.join((
                f"Path ({virtual}) exists, but Broken wants to create a symlink to ({real})",
                "• Confirm removing the 'virtual' path and continuing? (It might contain data or be a important symlink)"
            ))):
                BrokenPath.remove(virtual, echo=False)
            else:
                return

        try:
            virtual.symlink_to(real)
        except Exception as error:
            if BrokenPlatform.OnWindows:
                logger.minor("Failed to create Symlink. Consider enabling 'Developer Mode' on Windows (https://rye.astral.sh/guide/faq/#windows-developer-mode)")
            else:
                raise error

        return virtual

    def make_executable(path: Path, *, echo=True) -> Path:
        """Make a file executable"""
        if BrokenPlatform.OnUnix:
            shell("chmod", "+x", path, echo=echo)
        return path

    def zip(path: Path, output: Path=None, *, format: ShutilFormat="zip", echo: bool=True, **options) -> Path:
        format = ShutilFormat.get(format).value
        output = BrokenPath.get(output or path).with_suffix(f".{format}")
        path   = BrokenPath.get(path)
        logger.info(f"Zipping ({path})\n→ ({output})", echo=echo)
        BrokenPath.remove(output, echo=echo)
        shutil.make_archive(
            base_name=output.with_suffix(""),
            format=format,
            root_dir=path,
            **options
        )
        return output

    def gzip(path: Path, output: Path=None, *, remove: bool=False, echo: bool=True) -> Path:
        output = BrokenPath.get(output or path).with_suffix(".tar.gz")
        path   = BrokenPath.get(path)

        import tarfile

        logger.info(f"Compressing ({path}) → ({output})", echo=echo)

        with tarfile.open(output, "w:gz") as tar:
            if path.is_dir():
                for file in path.rglob("*"):
                    tar.add(file, arcname=file.relative_to(path))
            else:
                tar.add(path, arcname=path.name)
        if remove:
            BrokenPath.remove(path, echo=echo)

        return output

    def merge_zips(*zips: Path, output: Path, echo: bool=True) -> Path:
        """Merge multiple ZIP files into a single one"""
        import zipfile
        with zipfile.ZipFile(output, "w") as archive:
            for path in flatten(zips):
                with zipfile.ZipFile(path, "r") as other:
                    for file in other.filelist:
                        archive.writestr(file, other.read(file))
        return output

    def stem(path: Path) -> str:
        """
        Get the "true stem" of a path, as pathlib's only gets the last dot one
        • "/path/with/many.ext.ens.ions" -> "many" instead of "many.ext.ens"
        """
        stem = Path(Path(path).stem)
        while (stem := Path(stem).with_suffix("")).suffix:
            continue
        return str(stem)

    def extract(
        path: Path,
        output: Path=None,
        *,
        overwrite: bool=False,
        echo: bool=True
    ) -> Path:
        path, output = BrokenPath.get(path), BrokenPath.get(output)

        # Extract to the same directory by default
        if (output is None):
            output = path.parent

        # Add stem to the output as some archives might be flat
        output /= BrokenPath.stem(path)

        # Re-extract on order
        if overwrite:
            BrokenPath.remove(output)

        # A file to skip if it exists, created after successful extraction
        if (extract_flag := (output/"BrokenPath.extract.ok")).exists():
            logger.minor(f"Already extracted ({output})", echo=echo)
        else:
            # Show progress as this might take a while on slower IOs
            logger.info(f"Extracting ({path})\n→ ({output})", echo=echo)
            shutil.unpack_archive(path, output)
            extract_flag.touch()

        return output

    def url_filename(url: str) -> Path:
        return Path(url.split("#")[0].split("?")[0].split("/")[-1])

    def download(
        url: str,
        output: Path=None,
        *,
        size_check: bool=True,
        chunk: int=1024,
        echo: bool=True
    ) -> Optional[Path]:
        """
        Note: If the output is a directory, the url's file name will be appended to it
        Note: The output will default to Broken Project's Download directory
        """
        import validators

        # Link must be valid
        if not validators.url(url):
            import click
            if not click.confirm(logger.error(f"The following string doesn't look like a valid download URL on validator's eyes\n• ({url})\nContinue normally?")):
                return None

        # Default to Broken's Download directory
        if (output is None):
            output = broken.project.BROKEN.DIRECTORIES.DOWNLOADS

        # Append url's file name to the output path
        if (output := BrokenPath.get(output)).is_dir():
            output /= BrokenPath.url_filename(url)

        logger.info(f"Downloading\n• URL:  ({url})\n• Path: ({output})", echo=echo)

        # Without size check, the existence of the file is enough
        if (not size_check) and output.exists():
            logger.minor("• File exists and Size check was skipped", echo=echo)
            return None

        try:
            import requests
            response = requests.get(url, stream=True, headers={"Accept-Encoding": None})
        except requests.exceptions.RequestException as error:
            logger.error(f"• Failed to download: {error}", echo=echo)
            # Note: Return output as it might be downloaded but we're without internet
            return output

        # Note: The length header is not always present, if that, just check for existence
        if not (expected_size := int(response.headers.get('content-length', 0))):
            logger.minor("The Download doesn't advertise a size, just checking for existence", echo=echo)
            if output.exists():
                return output

        # The file might already be (partially) downloaded
        if (expected_size and size_check) and output.exists():
            if (output.stat().st_size == expected_size):
                return output
            if (len(output.read_bytes()) == expected_size):
                return output
            logger.warn("• Wrong Download size", echo=echo)

        BrokenPath.mkdir(output.parent)
        import tqdm

        # It is binary prefix, right? kibi, mebi, gibi, etc. as we're dealing with raw bytes
        with open(output, "wb") as file, tqdm.tqdm(
            desc=f"Downloading ({output.name})",
            total=expected_size, unit="iB", unit_scale=True, unit_divisor=1024,
            mininterval=1/30, maxinterval=0.5, leave=False
        ) as progress:
            for data in response.iter_content(chunk_size=chunk):
                progress.update(file.write(data))

        # Url was invalid or something
        if (response.status_code != 200):
            logger.error(f"Failed to Download File at ({url}):", echo=echo)
            logger.error(f"• HTTP Error: {response.status_code}", echo=echo)
            return

        # Wrong downloaded and expected size
        elif (expected_size and size_check) and (output.stat().st_size != expected_size):
            logger.error(f"File ({output}) was not downloaded correctly ({output.stat().st_size} != {expected_size})", echo=echo)
            return

        logger.ok(f"Downloaded file ({output}) from ({url})", echo=echo)
        return output

    def redirect(url: str) -> str:
        import requests
        return requests.head(url, allow_redirects=True).url

    def get_external(
        url: str, *,
        subdir: str="",
        redirect: bool=False,
        echo: bool=True
    ) -> Path:
        url  = BrokenPath.redirect(url) if redirect else url
        file = BrokenPath.url_filename(denum(url))

        # Is this file a .zip, .tar, etc..?
        ARCHIVE = any((str(file).endswith(ext) for ext in ShutilFormat.values()))

        # File is some known type, move to their own external directory
        if bool(subdir):
            directory = broken.project.BROKEN.DIRECTORIES.EXTERNALS/subdir
        elif ARCHIVE:
            directory = broken.project.BROKEN.DIRECTORIES.EXTERNAL_ARCHIVES
        elif (file.suffix in FileExtensions.Audio):
            directory = broken.project.BROKEN.DIRECTORIES.EXTERNAL_AUDIO
        elif (file.suffix in FileExtensions.Image):
            directory = broken.project.BROKEN.DIRECTORIES.EXTERNAL_IMAGES
        elif (file.suffix in FileExtensions.Font):
            directory = broken.project.BROKEN.DIRECTORIES.EXTERNAL_FONTS
        elif (file.suffix in FileExtensions.Soundfont):
            directory = broken.project.BROKEN.DIRECTORIES.EXTERNAL_SOUNDFONTS
        elif (file.suffix in FileExtensions.Midi):
            directory = broken.project.BROKEN.DIRECTORIES.EXTERNAL_MIDIS
        else:
            directory = broken.project.BROKEN.DIRECTORIES.EXTERNALS

        # Download to target directory, avoiding a move/copy, be known on future calls
        directory = (directory/subdir/file.name)

        # Finally download the file
        file = BrokenPath.download(denum(url), directory, echo=echo)

        # Maybe extract the downloaded file
        if ARCHIVE:
            file = BrokenPath.extract(file, echo=echo)

        for item in file.rglob("*"):
            if item.is_dir():
                Environment.add_to_path(item)

        return file

    def which(name: str) -> Optional[Path]:
        BrokenPath.update_externals_path()
        return BrokenPath.get(shutil.which(name))

    def update_externals_path(path: Path=None, *, echo: bool=True) -> Optional[Path]:
        for item in (path := (path or broken.project.BROKEN.DIRECTORIES.EXTERNALS)).rglob("*"):
            if item.is_dir(): Environment.add_to_path(item)
        return path

    @staticmethod
    def directories(path: Union[Path, Iterable]) -> Iterable[Path]:
        if isinstance(path, Path):
            path = Path(path).glob("*")
        for item in map(Path, path):
            if item.is_dir():
                yield item

    @staticmethod
    def files(path: Union[Path, Iterable]) -> Iterable[Path]:
        if isinstance(path, Path):
            path = Path(path).glob("*")
        for item in map(Path, path):
            if item.is_file():
                yield item

    @staticmethod
    def delete_old_files(path: Path, maximum: int=20) -> None:
        files = list(os.scandir(path))

        if (overflow := (len(files) - maximum)) > 0:
            files = sorted(files, key=os.path.getmtime)

            for file in itertools.islice(files, overflow):
                os.unlink(file.path)

    # # Specific / "Utils"

    def explore(path: Path):
        """Opens a path in the file explorer"""
        path = Path(path)
        if path.is_file():
            path = path.parent
        if BrokenPlatform.OnWindows:
            os.startfile(str(path))
        elif BrokenPlatform.OnLinux:
            shell("xdg-open", path, Popen=True)
        elif BrokenPlatform.OnMacOS:
            shell("open", path, Popen=True)

    class Windows:
        class Magic:
            # https://learn.microsoft.com/en-us/previous-versions/windows/embedded/aa453707(v=msdn.10)
            Documents: int = 0x05
            Music:     int = 0x0D
            Video:     int = 0x0E
            Desktop:   int = 0x10
            Roaming:   int = 0x1A
            Local:     int = 0x1C
            Pictures:  int = 0x27
            Home:      int = 0x28

        class Type(Enum):
            Current = 0
            Default = 1

        @staticmethod
        def get(csidl: int, *, type: Type=Type.Current) -> Path:
            if (os.name != "nt"):
                raise RuntimeError("BrokenPath.Windows only obviously works on Windows")
            buffer = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
            ctypes.windll.shell32.SHGetFolderPathW(None, csidl, None, type.value, buffer)
            return Path(buffer.value)

        @functools.lru_cache
        def Documents(*, type: Type=Type.Current) -> Path:
            return BrokenPath.Windows.get(BrokenPath.Windows.Magic.Documents, type=type)

        @functools.lru_cache
        def Music(*, type: Type=Type.Current) -> Path:
            return BrokenPath.Windows.get(BrokenPath.Windows.Magic.Music, type=type)

        @functools.lru_cache
        def Video(*, type: Type=Type.Current) -> Path:
            return BrokenPath.Windows.get(BrokenPath.Windows.Magic.Video, type=type)

        @functools.lru_cache
        def Desktop(*, type: Type=Type.Current) -> Path:
            return BrokenPath.Windows.get(BrokenPath.Windows.Magic.Desktop, type=type)

        @functools.lru_cache
        def Roaming(*, type: Type=Type.Current) -> Path:
            return BrokenPath.Windows.get(BrokenPath.Windows.Magic.Roaming, type=type)

        @functools.lru_cache
        def Local(*, type: Type=Type.Current) -> Path:
            return BrokenPath.Windows.get(BrokenPath.Windows.Magic.Local, type=type)

        @functools.lru_cache
        def Pictures(*, type: Type=Type.Current) -> Path:
            return BrokenPath.Windows.get(BrokenPath.Windows.Magic.Pictures, type=type)

