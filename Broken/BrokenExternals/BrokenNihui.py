from . import *


class BrokenNihuiBase(BrokenExternalABC):
    def install(self, directories: BrokenDirectories):
        json = BROKEN_REQUESTS_CACHE.get(f"https://api.github.com/repos/nihui/{self.binary_name}/releases/latest").json()
        platform = BrokenPlatform.Name.replace("linux", "ubuntu")
        for asset in json.get("assets"):
            if platform in asset.get("name"):
                url = asset.get("browser_download_url")
                break
        BrokenDownloads.download_extract_zip(url, directories.EXTERNALS)


# FIXME: Do we generalize what an upscaler should do somewhere else? and maybe implement self._upscale for the true function
class BrokenNihuiUpscaler:
    def upscale(self, image: Union[PilImage, PathLike, URL], output: Path=None) -> PilImage:
        """Upscale an image"""
        raise NotImplementedError


# FIXME: Do we limit what the classes accepts as inputs parameters somehow?
class BrokenWaifu2x(BrokenNihuiBase):
    @property
    def binary_name(self) -> str: return "waifu2x-ncnn-vulkan"

class BrokenRealsr(BrokenNihuiBase):
    @property
    def binary_name(self) -> str: return "realsr-ncnn-vulkan"

class BrokenSRMD(BrokenNihuiBase):
    @property
    def binary_name(self) -> str: return "srmd-ncnn-vulkan"

