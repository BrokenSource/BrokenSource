from . import *


class BrokenStableDiffusion:
    def __init__(self, config=BROKEN_DIRECTORIES.CONFIG/"BrokenStableDiffusion.toml"):
        BrokenNeedImport("torch", "diffusers", "accelerate", "transformers")
        self.config = BrokenDotmap(config)

    def load_model(self):
        self.precision = self.config.defaults("variant", "fp16")

        self.pipe = diffusers.DiffusionPipeline.from_pretrained(
            self.config.defaults("model", "stabilityai/stable-diffusion-xl-base-0.9"),
            torch_dtype=torch.float16 if (self.precision == "fp16") else torch.float32,
            variant=self.precision,
            use_auth_token=os.environ.get("HF_TOKEN", None),
            use_safetensors=True,
            resume_download=True,
        )
        self.pipe.to(self.config.defaults("device", "cuda"))

    def optimize(self):

        # Can't optimize for CPU
        if self.config.device == "cpu":
            warning("• Skipping Stable Diffusion optimization for CPU")
            return

        # If torch version < 2.0
        if (torch.__version__ < "2.0.0"):
            info("Optimizing PyTorch < 2.0 Reduce-overhead")
            self.pipe.unet = torch.compile(
                self.pipe.unet,
                mode="reduce-overhead",
                fullgraph=True
            )
        else:
            info("Optimizing PyTorch >= 2.0 xformers memory efficient attention")
            self.pipe.enable_xformers_memory_efficient_attention()

    def prompt(self,
        prompt: str="Astronaut on a white rocky moon landscape",
        steps: int=50,
    ) -> PilImage:
        return self.pipe(prompt=prompt).images[0]

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

