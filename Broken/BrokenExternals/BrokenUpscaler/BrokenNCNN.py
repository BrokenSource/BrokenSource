from . import *


@define
class BrokenUpscalerNCNN(BrokenUpscaler, ABC):
    noise_level:  int  = field(default=1, converter=int)
    scale:        int  = field(default=2, converter=int)
    tile_size:    int  = field(default=0, converter=int)
    gpu:          int  = field(default=0, converter=int)
    load_threads: int  = field(default=1, converter=int)
    proc_threads: int  = field(default=2, converter=int)
    save_threads: int  = field(default=2, converter=int)
    cpu:          bool = field(default=0, converter=bool)
    tta:          bool = field(default=0, converter=bool)
    passes:       int  = field(default=1, converter=int)

# -------------------------------------------------------------------------------------------------|

class BrokenWaifu2xModel(BrokenEnum):
    Cunet = "models-cunet"
    Anime = "models-upconv_7_anime_style_art_rgb"
    Photo = "models-upconv_7_photo"

@define
class BrokenWaifu2x(BrokenUpscalerNCNN):
    model: BrokenWaifu2xModel = field(
        default  =BrokenWaifu2xModel.Cunet,
        converter=BrokenWaifu2xModel.get
    )

    @property
    def binary(self) -> str:
        return "waifu2x-ncnn-vulkan"

    def __validate__(self):
        if not all(things := (
            self.noise_level in {-1, 0, 1, 2, 3},
            self.scale in {1, 2, 4, 8, 16, 32},
            (self.tile_size == 0) or (self.tile_size >= 32),
            self.model is not None,
            self.gpu >= 0,
            self.load_threads >= 1,
            self.proc_threads >= 1,
            self.save_threads >= 1,
        )):
            raise ValueError(f"Invalid parameters for {self.__class__.__name__}: {things}")

    def __upscale__(self, input: Path, output: Path):
        shell(
            self.binary,
            "-i", input,
            "-o", output,
            "-n", self.noise_level,
            "-s", self.scale,
            "-t", self.tile_size,
            "-g", self.gpu if not self.cpu else -1,
            "-j", f"{self.load_threads}:{self.proc_threads}:{self.save_threads}",
            "-x"*self.tta,
            # "-m", self.model.value, # Fixme: Doko?
            stderr=subprocess.DEVNULL,
        )

# -------------------------------------------------------------------------------------------------|

class BrokenRealEsrganModel(BrokenEnum):
    AnimeVideoV3 = "realesr-animevideov3"
    X4Plus       = "realesrgan-x4plus"
    X4PlusAnime  = "realesrgan-x4plus-anime"
    X4PlusNet    = "realesrnet-x4plus"

@define
class BrokenRealEsrgan(BrokenUpscalerNCNN):
    model: BrokenRealEsrganModel = field(
        default=  BrokenRealEsrganModel.AnimeVideoV3,
        converter=BrokenRealEsrganModel.get
    )

    @property
    def binary(self) -> str:
        return "realesrgan-ncnn-vulkan"

    def __validate__(self):
        if not all(things := (
            self.passes >= 1,
            self.scale in {2, 3, 4},
            (self.tile_size == 0) or (self.tile_size >= 32),
            self.model is not None,
            self.gpu >= 0,
            self.load_threads >= 1,
            self.proc_threads >= 1,
            self.save_threads >= 1,
        )):
            raise ValueError(f"Invalid parameters for {self.__class__.__name__}: {things}")

    def __upscale__(self, input: Path, output: Path):
        shell(
            self.binary,
            "-i", input,
            "-o", output,
            "-n", self.model.value,
            "-s", self.scale,
            "-t", self.tile_size,
            "-g", self.gpu,
            "-j", f"{self.load_threads}:{self.proc_threads}:{self.save_threads}",
            "-x"*self.tta,
            stderr=subprocess.DEVNULL,
        )

# -------------------------------------------------------------------------------------------------|
