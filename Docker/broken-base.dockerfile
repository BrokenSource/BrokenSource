# ------------------------------------------------------------------------------------------------ #
# (c) MIT License, Tremeschin
# Dockerfile v2024.12.4
# ------------------------------------------------------------------------------------------------ #
# General metadata and configuration

FROM ubuntu:24.04
LABEL org.opencontainers.image.title="BrokenBase"
LABEL org.opencontainers.image.description="Batteries-included image for all Broken Source projects"
LABEL org.opencontainers.image.source="https://github.com/BrokenSource/BrokenSource"
LABEL org.opencontainers.image.authors="Tremeschin"
LABEL org.opencontainers.image.licenses="MIT"
ENV DEBIAN_FRONTEND="noninteractive"
RUN apt update
WORKDIR /App

# ------------------------------------------------------------------------------------------------ #
# Make Vulkan and OpenGL EGL acceleration work on NVIDIA (the unveiled magic of nvidia/glvnd)

# Nvidia container toolkit configuration
ENV NVIDIA_DRIVER_CAPABILITIES="all"
ENV NVIDIA_VISIBLE_DEVICES="all"

# Don't use llvmpipe (software rendering) on WSL
ENV MESA_D3D12_DEFAULT_ADAPTER_NAME="NVIDIA"
ENV LD_LIBRARY_PATH="/usr/lib/wsl/lib"

# (ShaderFlow) Don't use glfw
ENV WINDOW_BACKEND="headless"

# Add libEGL ICD loader and libraries
RUN apt install -y libglvnd0 libglvnd-dev libegl1-mesa-dev && \
    mkdir -p /usr/share/glvnd/egl_vendor.d && \
    echo '{"file_format_version":"1.0.0","ICD":{"library_path":"libEGL_nvidia.so.0"}}' > \
    /usr/share/glvnd/egl_vendor.d/10_nvidia.json

# Add Vulkan ICD and libraries
RUN apt install -y libvulkan1 libvulkan-dev && \
    mkdir -p /usr/share/vulkan/icd.d && \
    echo '{"file_format_version":"1.0.0","ICD":{"library_path":"libGLX_nvidia.so.0","api_version":"1.3"}}' > \
    /usr/share/vulkan/icd.d/nvidia_icd.json

# ------------------------------------------------------------------------------------------------ #

# (ShaderFlow) SoundCard needs libpulse.so and server
RUN apt install -y pulseaudio && \
    adduser root pulse-access

# Video encoding and decoding
RUN apt install -y xz-utils curl git
ARG FFMPEG="ffmpeg-master-latest-linux64-gpl"
RUN curl -L "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/${FFMPEG}.tar.xz" | \
    tar -xJ --strip-components=2 --exclude="doc" --exclude="man" -C /usr/local/bin

# Upscayl upscaler, strip electron part of the package
RUN curl -L "https://github.com/upscayl/upscayl/releases/download/v2.11.5/upscayl-2.11.5-linux.deb" \
    -o /tmp/upscayl.deb && apt install -y /tmp/upscayl.deb && rm /tmp/upscayl.deb && mkdir -p /opt/upscayl && \
    mv /opt/Upscayl/resources/models /opt/upscayl/models && \
    mv /opt/Upscayl/resources/bin /opt/upscayl/bin && \
    rm -rf /opt/Upscayl

# Install uv and create a virtual environment
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
ENV UV_COMPILE_BYTECODE="1"
ENV UV_LINK_MODE="copy"
ENV VIRTUAL_ENV="/App/.venv"
ENV PATH="/App/.venv/bin:$PATH"
RUN uv venv --python 3.12 "$VIRTUAL_ENV"

# Cache depth estimator models
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install huggingface-hub && \
    huggingface-cli download "depth-anything/Depth-Anything-V2-small" && \
    huggingface-cli download "depth-anything/Depth-Anything-V2-base"

# Install a PyTorch flavor
ARG TORCH_VERSION="2.5.1"
ARG TORCH_FLAVOR="cpu"
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install torch=="${TORCH_VERSION}+${TORCH_FLAVOR}" \
    --index-url "https://download.pytorch.org/whl/${TORCH_FLAVOR}"
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install transformers

# Install project dependencies (assumes uv sync was run before)
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --inexact

# Development mode
COPY . /App

# Note: --inexact to preserve torch
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --all-packages --inexact

# ------------------------------------------------------------------------------------------------ #
