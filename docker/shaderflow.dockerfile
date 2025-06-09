# syntax=devthefuture/dockerfile-x@sha256:263815a4cfdbfdd302e6c7f5d4147e43004f456b0566ac300bf8ae468a9458b1
INCLUDE ./docker/include/base.dockerfile
INCLUDE ./docker/include/uv.dockerfile
INCLUDE ./docker/include/opengl.dockerfile
INCLUDE ./docker/include/pulse.dockerfile
INCLUDE ./docker/include/ffmpeg.dockerfile
INCLUDE ./docker/include/code.dockerfile

# ------------------------------------------------------------------------------------------------ #

LABEL org.opencontainers.image.title="ShaderFlow"
LABEL org.opencontainers.image.description="🔥 Imagine ShaderToy, on a Manim-like architecture. That's ShaderFlow."
CMD ["shaderflow", "basic", "main", "-o", "video.mp4", "-t", "30"]
