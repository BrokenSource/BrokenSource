from . import *


class BrokenStableDiffusion:
    def __init__(self, config=BROKEN_DIRECTORIES.CONFIG/"BrokenStableDiffusion.toml"):
        BrokenUtils.need_import("torch", "diffusers", "accelerate", "transformers")
        self.config = BrokenDotmap(config)

    def load_model(self):
        """Initialize the Stable Diffusion models."""
        self.precision = self.config.defaults("variant", "fp16")

        self.pipe = diffusers.StableDiffusionXLPipeline.from_pretrained(
            self.config.defaults("pipe", "stabilityai/stable-diffusion-xl-base-0.9"),
            torch_dtype=torch.float16 if (self.precision == "fp16") else torch.float32,
            variant=self.precision,
            use_auth_token=os.environ.get("HF_TOKEN", None),
            use_safetensors=True,
            resume_download=True,
        )

        self.refiner = diffusers.StableDiffusionXLImg2ImgPipeline.from_pretrained(
            self.config.defaults("refiner", "stabilityai/stable-diffusion-xl-refiner-0.9"),
            torch_dtype=torch.float16 if (self.precision == "fp16") else torch.float32,
            variant=self.precision,
            use_auth_token=os.environ.get("HF_TOKEN", None),
            use_safetensors=True,
            resume_download=True,
        )

        device = self.config.defaults("device", "cuda")
        self.pipe.to(device)
        self.refiner.to(device)

    def optimize(self):

        # Can't optimize for CPU
        if self.config.device == "cpu":
            warning("• Skipping Stable Diffusion optimization for CPU")
            return

        # If torch version < 2.0
        if (torch.__version__ < "2.0.0"):
            log.info("Optimizing PyTorch < 2.0 Reduce-overhead")
            optimize = lambda item: torch.compile(item, mode="reduce-overhead", fullgraph=True)
            self.pipe.unet = optimize(self.pipe.unet)
            self.refiner.unet = optimize(self.refiner.unet)
        else:
            log.info("Optimizing PyTorch >= 2.0 xformers memory efficient attention")
            self.pipe.enable_xformers_memory_efficient_attention()
            self.refiner.enable_xformers_memory_efficient_attention()

    def mse_image(self, A: PilImage, B: PilImage) -> float:
        """
        Calculate the mean squared error between two images.
        """
        return numpy.square(numpy.subtract(A, B)).mean()

    def image_equal(A: PilImage, B: PilImage, factor: float = 0.01) -> bool:
        """Check if two images are close enough using MSE with a factor relative to image sizes."""
        if A.size != B.size:
            return False
        return self.mse_image(A, B) / (A.size[0] * A.size[1]) <= ((3*255**2)*factor)

