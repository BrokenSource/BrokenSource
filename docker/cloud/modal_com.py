"""
# ------------------------------------------------------------------------------------------------ #

(c) 2024, Tremeschin, MIT License

Example file for running the projects / DepthFlow on [Modal](https://modal.com/). Be sure to follow
  their [User Guide](https://modal.com/docs/guide) for the initial setup (cli, tokens, etc)

# ------------------------------------------------------------------------------------------------ #

Warn: The T4 GPU seems to be the only one with OpenGL acceleration enabled on Modal by default,
  and have plenty horsepower for this project. If this/other GPUs doesn't show up as a OpenGL
  renderer ("llvmpipe" instead), you should ask the support team to enable `graphics, video`
  capabilities on your workspace. Failing to do so will render at abysmal speeds.

# ------------------------------------------------------------------------------------------------ #
"""

from io import BytesIO
from pathlib import Path
from uuid import uuid4

import modal
from dotmap import DotMap
from PIL import Image

image = (
    modal.Image.from_registry("nvidia/opengl:1.2-glvnd-runtime-ubuntu22.04", add_python="3.12")
    .run_commands("python3 -m pip install torch==2.6.0 --index-url https://download.pytorch.org/whl/cu124")
    .apt_install("ffmpeg")
    .pip_install("depthflow==0.9.0.dev1")
    .run_commands("depthflow load-estimator")
)

app = modal.App(
    name="depthflow",
    image=image,
)

@app.function(gpu="t4", cpu=4, memory=4096)
def render(data: DotMap) -> bytes:
    from depthflow.Scene import DepthScene
    scene = DepthScene(backend="headless")
    scene.input(image=Image.open(BytesIO(data.image)))

    # Animation
    scene.circle(intensity=0.5)
    # scene.orbital()
    # scene.horizontal()
    # ...

    # Rendering
    scene.ffmpeg.h264_nvenc()
    return scene.main(
        output=f"{uuid4()}.mp4",
        height=data.height,
        ssaa=data.ssaa,
        time=data.time,
    )[0].read_bytes()

@app.local_entrypoint()
def main():
    image = Image.open("./input.jpg")

    # Fixme: Image pickling errors, buffer workaround (slower)
    image.save(buffer := BytesIO(), format="PNG")
    video = render.remote(DotMap(
        image=buffer.getvalue(),
        height=1080,
        ssaa=2,
        time=5,
    ))

    Path("./output.mp4").write_bytes(video)
