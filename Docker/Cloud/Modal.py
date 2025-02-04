"""
# ------------------------------------------------------------------------------------------------ #

(c) 2024, Tremeschin, MIT License

Example file for running the projects / DepthFlow on [Modal](https://modal.com/). Be sure to follow
  their [User Guide](https://modal.com/docs/guide) for the initial setup (cli, tokens, etc)

# ------------------------------------------------------------------------------------------------ #

NOTE: The 'modal' Python package isn't included on the Projects, you should manage it yourself

WARN: You must ask the support team to enable a Workspace configuration for GPU OpenGL acceleration
    to work - that is, enable `graphics,video` capabilities on NVIDIA CONTAINER TOOLKIT, as they are
    selective to enable it. Failing to do so WILL NOT USE THE GPU and render at abyssmal speeds

WARN: NVENC is disabled by default for security reasons, but you could try asking for enabling it.
    Otherwise, throw a couple more cores and use CPU video encoding, which gives better quality
    and smaller files sizes compared to GPU encoding. Prefer the NVIDIA L4 GPU for NVENC usage
    as it has the newest NVENC generation, is cheap, and have plenty horsepower for shaders

ShaderFlow will tell which OpenGL rendered is being used, "llvmpipe" is CPU (bad)

# ------------------------------------------------------------------------------------------------ #
"""

from pathlib import Path

import modal
from dotmap import DotMap
from PIL import Image

image = (
    modal.Image.from_registry("nvidia/opengl:1.2-glvnd-runtime-ubuntu22.04", add_python="3.11")
    .run_commands("python3 -m pip install torch==2.6.0 --index-url https://download.pytorch.org/whl/cu124")
    .apt_install("mesa-utils")
    .apt_install("ffmpeg")
    .pip_install("transformers")
    .pip_install("depthflow")

    # Download depth estimator model once
    .run_commands("depthflow load-estimator")
)

app = modal.App(
    "depthflow",
    image=image
)

@app.function(gpu="l4", cpu=4)
def run(data: DotMap) -> bytes:
    from DepthFlow import DepthScene
    scene = DepthScene(backend="headless")
    scene.input(image=data.image)
    # scene.ffmpeg.h264_nvenc()
    return scene.main(
        render=True,
        height=720,
        time=5,
    )[0].read_bytes()

@app.local_entrypoint()
def main():
    data = DotMap(
        image=Image.open("./input.jpg")
    )
    video = run.remote(data)
    Path("./output.mp4").write_bytes(video)
