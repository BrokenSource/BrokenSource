from . import *

# FIXME: File partially ported and tested from old Protostar
# Needs testing and simplification

class BrokenZip(PathLike):
    """Portable Path-Like directory that is a .zip file

    Z = ZipDir(Path)
    (Z/"Dir1"/"Dir2"/"File.txt").write_text("Hello from ZipDir Class!!")
    content = (Z/"Directory"/"Hello.txt").read_text()
    """
    def __init__(self, path: Path, empty=False, _write_path=None):
        assert str(path).endswith(".zip")
        self.file_path = Path(path)
        self.write_path = _write_path or Path("/")

        if _write_path is None:
            info(f"New ZipDir at [{self.file_path}]")

        if empty and self.file_path.exists():
            info(f"Reset ZipDir at [{self.file_path}]")
            self.file_path.write_text("")

        # Open ZipFile
        self.zip_file = ZipFile(self.file_path, "a",
            compression=zipfile.ZIP_LZMA,
            compresslevel=9
        )

    # # Recursivity

    def _recurse(self, other):
        return BrokenZip(self.file_path, _write_path=self.write_path/other)

    def __floordiv__(self, Other): return self._recurse(Other)
    def __truediv__ (self, Other): return self._recurse(Other)

    # # pathlib.Path compatibility (well, the ones I needed)

    def __fspath__(self): return str(self.write_path)
    def write_text (self, data): return self.write(data)
    def write_bytes(self, data): return self.write(data)
    def read_text (self): return self.read_text()
    def read_bytes(self): return self.read_bytes()

    @property
    def suffix(self): return self.write_path.suffix

    def exists(self) -> bool:
        with ZipFile(self.file_path) as zip_file:
            return self.path_exists(zip_file)

    # Within an open ZipFile, does WritePath exist in the files?
    def path_exists(self, zip_file) -> bool:
        return str(self.write_path) in [F.filename for F in zip_file.filelist]

    # # Actual implementations on top of zipfile.ZipFile

    def remove(self):
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # Code Adapted From:
        # https://github.com/python/cpython/blob/659eb048cc9cac73c46349eb29845bc5cd630f09/Lib/zipfile.py#L1717
        want_remove = self.zip_file.getinfo(str(self.write_path))
        entry_offset = 0
        FileList = sorted(self.zip_file.filelist, key=operator.attrgetter('header_offset'))
        for i, file_info in enumerate(FileList):
            if file_info.header_offset < want_remove.header_offset: continue
            if i == (len(FileList) - 1):
                entry_size = self.zip_file.start_dir - file_info.header_offset
            else:
                entry_size = FileList[i+1].header_offset - file_info.header_offset
            if want_remove == file_info:
                entry_offset = entry_size
                continue
            self.zip_file.fp.seek(file_info.header_offset)
            entry_data = self.zip_file.fp.read(entry_size)
            file_info.header_offset -= entry_offset
            self.zip_file.fp.seek(file_info.header_offset)
            self.zip_file.fp.write(entry_data)
            self.zip_file.fp.flush()
        self.zip_file.start_dir -= entry_offset
        self.zip_file.filelist.remove(want_remove)
        del self.zip_file.NameToInfo[want_remove.filename]
        self.zip_file._didModify = True
        self.zip_file.fp.seek(self.zip_file.start_dir)
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def write(self, data: str):
        if self.path_exists(self.zip_file):
            self.remove()
        self.zip_file.writestr(str(self.write_path), data)

    def read_bytes(self):
        with self.zip_file.open(str(self.write_path)) as file:
            return file.read()

    def read_text(self):
        return self.read_bytes().decode("utf-8")
