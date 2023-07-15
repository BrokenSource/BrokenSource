from . import *


class BrokenDownloads:

    @contextmanager
    def download(
        url: str,
        cache=True,
        redownload=False,
        delete=False,
        output_directory: PathLike=BROKEN_DIRECTORIES.DOWNLOADS,
        file_name: str=None,
    ) -> Path:
        """Downloads a file from a url, saves to Broken directories"""
        if cache: requests = BROKEN_REQUESTS_CACHE

        # Remove url query strings
        url = url.split("?")[0]

        # Auto name the download file -> get the file name as if the url was a path
        download_file = output_directory / (file_name or Path(url).name)

        # Get steam information
        download_size = int(requests.get(url, stream=True).headers.get("content-length", 0))

        info(f"• Downloading file [{download_file.name}]")
        info(f"├─ URL:    [{url}]")
        info(f"├─ File:   [{download_file}]")
        info(f"├─ Size:   [{download_size/1e6:.2f} MB]")

        # Don't check for sizes or files if redownload is requested
        if redownload:
            pass

        # If a file exists it must be the same size as the download
        elif download_file.exists():
            current_size = download_file.stat().st_size

            # Redownload if not same size
            if current_size != download_size:
                warning(f"├─ Status: [Invalid size ({current_size/1e6:.2f} MB != {download_size/1e6:.2f} MB)]")
                remove_path(download_file)
            else:
                success(f"└─ Status: [Download exists and is ok]")
                yield download_file
                return

        # Download the file
        info(f"└─ Status: [Downloading]")
        with halo.Halo(f"Downloading [{download_file.name}]"):
            download_file.write_bytes(requests.get(url).content)

        yield download_file

        # Delete the file if requested
        if delete:
            remove_path(download_file)

    def extract_archive(archive: PathLike, destination: PathLike=BROKEN_DIRECTORIES.EXTERNALS, echo=True) -> Path:
        """Extracts the contents of a compressed archive to a destination directory."""
        archive, destination = Path(archive), Path(destination)

        # Define destination directory automatically and add archive's stem (file name without extension)
        destination = destination/archive.stem

        # Information on operation
        info(f"• Extracting Archive [{archive.name}]", echo=echo)
        info(f"├─ Archive:     [{archive}]", echo=echo)
        info(f"├─ Destination: [{destination}]", echo=echo)

        # Already extracted
        if destination.exists():
            success(f"└─ Status:      [Already extracted]", echo=echo)
            return destination

        # Extract
        info(f"└─ Status:      [Extracting]", echo=echo)
        shutil.unpack_archive(archive, destination)
        return destination

    def download_extract_zip_to_externals(url: str, destination: PathLike=BROKEN_DIRECTORIES.EXTERNALS) -> Path:
        """Download and extract a zip file"""
        with BrokenDownloads.download(url) as zip_file:
            return extract_archive(zip_file, destination)