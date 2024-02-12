from . import *


@define
class BrokenUpscalerNCNN(BrokenUpscaler, ABC):
    noise_level:  int  = field(default=1, converter=int)
    tile_size:    int  = field(default=0, converter=int)
    gpu:          int  = field(default=0, converter=int)
    load_threads: int  = field(default=1, converter=int)
    proc_threads: int  = field(default=1, converter=int)
    save_threads: int  = field(default=1, converter=int)
    cpu:          bool = field(default=0, converter=bool)
    tta:          bool = field(default=0, converter=bool)

    def preexec_fn(self):
        import os
        import random
        import resource

        # Make the process only use one random core
        core = random.choice(range(os.cpu_count()))
        os.sched_setaffinity(0, {core})
        resource.setrlimit(resource.RLIMIT_CPU, (1, 1))

    @property
    def n(self) -> int:
        return self.noise_level
    @n.setter
    def n(self, value: int):
        self.noise_level = value

    @property
    def t(self) -> int:
        return self.tile_size
    @t.setter
    def t(self, value: int):
        self.tile_size = value

    @property
    def g(self) -> int:
        return self.gpu
    @g.setter
    def g(self, value: int):
        self.gpu = value

    @property
    def j(self) -> str:
        return f"{self.load_threads}:{self.proc_threads}:{self.save_threads}"
    @j.setter
    def j(self, value: str):
        self.load_threads, self.proc_threads, self.save_threads = map(int, value.split(":"))

    @property
    def c(self) -> bool:
        return self.cpu
    @c.setter
    def c(self, value: bool):
        self.cpu = value

    @property
    def x(self) -> bool:
        return self.tta
    @x.setter
    def x(self, value: bool):
        self.tta = value

    @property
    def p(self) -> int:
        return self.passes
    @p.setter
    def p(self, value: int):
        self.passes = value

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

    def __upscale__(self, input: Path, output: Path, *, echo: bool=True):
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
            preexec_fn=self.preexec_fn,
            echo=echo,
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

    def __upscale__(self, input: Path, output: Path, *, echo: bool=True):
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
            preexec_fn=self.preexec_fn,
            echo=echo,
        )

# -------------------------------------------------------------------------------------------------|
