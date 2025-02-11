"""
# ------------------------------------------------------------------------------------------------ #

(c) 2024, Tremeschin, MIT License

Example file for running the projects / DepthFlow on [Modal](https://modal.com/). Be sure to follow
  their [User Guide](https://modal.com/docs/guide) for the initial setup (cli, tokens, etc)

# ------------------------------------------------------------------------------------------------ #

Warn: You must ask the support team to move your workspace to an older runner of theirs with support
    for `graphics,video` capabilities on NVIDIA CONTAINER TOOLKIT. Failing to do so WILL NOT USE THE
    GPU and rendering speeds will be abyssmal. If you see "llvmpipe" renderer, it's using CPU (bad)

# ------------------------------------------------------------------------------------------------ #
"""

from pathlib import Path

import modal
from dotmap import DotMap
from PIL import Image

image = (
    modal.Image.from_registry("nvidia/opengl:1.2-glvnd-runtime-ubuntu22.04", add_python="3.12")
    .run_commands("python3 -m pip install torch==2.6.0 --index-url https://download.pytorch.org/whl/cu124")
    .apt_install("ffmpeg")
    .pip_install("transformers")
    .pip_install("depthflow")
    .run_commands("depthflow load-estimator")
)

app = modal.App(
    name="depthflow",
    image=image,
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
