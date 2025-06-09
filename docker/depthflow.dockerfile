# syntax=devthefuture/dockerfile-x@sha256:263815a4cfdbfdd302e6c7f5d4147e43004f456b0566ac300bf8ae468a9458b1
INCLUDE ./docker/include/base.dockerfile
INCLUDE ./docker/include/uv.dockerfile
INCLUDE ./docker/include/opengl.dockerfile
INCLUDE ./docker/include/vulkan.dockerfile
INCLUDE ./docker/include/pulse.dockerfile
INCLUDE ./docker/include/ffmpeg.dockerfile
INCLUDE ./docker/include/upscayl.dockerfile
INCLUDE ./docker/include/depthmap.dockerfile
INCLUDE ./docker/include/torch.dockerfile
INCLUDE ./docker/include/code.dockerfile

# ------------------------------------------------------------------------------------------------ #

LABEL org.opencontainers.image.title="DepthFlow"
LABEL org.opencontainers.image.description="🌊 Images to → 3D Parallax effect video. A free and open source ImmersityAI alternative"
CMD ["depthflow", "gradio"]
