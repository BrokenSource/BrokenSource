"""
|--------------------------------------------------------------------------------------------------|

(c) 2024, Tremeschin, MIT License

Example file for running the projects / DepthFlow on [Modal](https://modal.com/). Be sure to follow
  their [User Guide](https://modal.com/docs/guide) for the initial setup (cli, tokens, etc)

 (❤️) Consider [Supporting](https://brokensrc.dev/about/sponsors) my work, if this helped you (❤️)

|--------------------------------------------------------------------------------------------------|

WARN: You must ask the support team to enable a Workspace runtime configuration for GPU acceleration
    to work - that is, enable `graphics,video` capabilities on NVIDIA CONTAINER TOOLKIT, as they are
    selective to enable it. Failing to do so WILL NOT USE THE GPU and render at abyssmal speeds

WARN: NVENC is disabled by default for security reasons, you must also ask the support team for it.
    Otherwise, throw a couple more cores and use CPU video encoding (non-nvenc codecs)

WARN: Avoid A100, H100 GPUs as they are tensor core only, without graphics API support (OpenGL)

ShaderFlow will tell which GPU is being used (v0.4.1+), "llvmpipe" is CPU (bad), any other is good

|--------------------------------------------------------------------------------------------------|

NOTE: The `modal` Python package isn't included on the Projects, you should manage it yourself
NOTE: The NVENC encoder is recommended for better resources utilization and overall speeds, as
    throwing many cores doesn't change the memory bandwidth, often a bottleneck for video encoding
NOTE: CPU encoding *is* better for quality, if you prioritize quality over costs, use it
NOTE: The NVIDIA L4 GPU has the newest NVENC, is cheap, and have plenty horsepower for shaders
NOTE: Experimentally, 4 CPUs gives the best encoding speeds, as often some cores are busy with
    memory transfers (raw frames from/to CPU, CPU, FFmpeg), running ShaderFlow backend and FFmpeg

|--------------------------------------------------------------------------------------------------|
"""

from pathlib import Path

import modal

image = (
    modal.Image.from_registry("nvidia/opengl:1.2-glvnd-runtime-ubuntu22.04", add_python="3.10")
    .run_commands("python3 -m pip install torch==2.3.0 --index-url https://download.pytorch.org/whl/cu118")
    .apt_install("mesa-utils")
    .pip_install("transformers")
    .pip_install("depthflow")
)

app = modal.App(
    "depthflow",
    image=image
)

@app.function(gpu="l4", cpu=4)
def run() -> bytes:
    from DepthFlow import DepthScene
    scene = DepthScene(backend="headless")
    video = Path("/tmp/video.mp4")
    scene.main(output=video, vcodec="h264", time=30)
    return video.read_bytes()

@app.local_entrypoint()
def main():
    video = run.remote()
    Path("./output.mp4").write_bytes(video)
