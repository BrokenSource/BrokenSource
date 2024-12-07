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
# Make OpenGL acceleration with EGL and Vulkan work on NVIDIA

# Basic required configuration
ENV NVIDIA_DRIVER_CAPABILITIES="all"
ENV NVIDIA_VISIBLE_DEVICES="all"

# Don't use llvmpipe (software rendering) on WSL
ENV MESA_D3D12_DEFAULT_ADAPTER_NAME="NVIDIA"
ENV LD_LIBRARY_PATH="/usr/lib/wsl/lib"

# Install libEGL stuff (for non-nvidia glvnd base images)
RUN apt install -y libglvnd0 libglvnd-dev libegl1-mesa-dev && \
    mkdir -p /usr/share/glvnd/egl_vendor.d && \
    echo '{"file_format_version":"1.0.0","ICD":{"library_path":"libEGL_nvidia.so.0"}}' > \
    /usr/share/glvnd/egl_vendor.d/10_nvidia.json

# Similar story with Vulkan
RUN apt install -y libvulkan1 libvulkan-dev && \
    mkdir -p /usr/share/vulkan/icd.d && \
    echo '{"file_format_version":"1.0.0","ICD":{"library_path":"libGLX_nvidia.so.0","api_version":"1.3"}}' > \
    /usr/share/vulkan/icd.d/nvidia_icd.json

# ------------------------------------------------------------------------------------------------ #

# SoundCard needs libpulse.so and server
RUN apt install -y pulseaudio && \
    adduser root pulse-access

# Video encoding and decoding
RUN apt install -y xz-utils curl git
ARG FFMPEG="ffmpeg-master-latest-linux64-gpl"
RUN curl -L "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/${FFMPEG}.tar.xz" | \
    tar -xJ --strip-components=2 --exclude="doc" --exclude="man" -C /usr/local/bin

# Begin with the current git main at workdir
RUN git clone --recurse-submodules --jobs 4 https://github.com/BrokenSource/BrokenSource /App && \
    git submodule foreach --recursive 'git checkout main || true' && \
    git pull --recurse-submodules

# Install uv and create a virtual environment
COPY --from=ghcr.io/astral-sh/uv:0.5.7 /uv /uvx /bin/
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV VIRTUAL_ENV="/App/.venv"
ENV PATH="/App/.venv/bin:$PATH"
RUN uv venv --python 3.12 "$VIRTUAL_ENV"

# Install a PyTorch flavor
ARG TORCH_VERSION="2.5.1"
ARG TORCH_FLAVOR="cpu"
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install torch=="${TORCH_VERSION}+${TORCH_FLAVOR}" \
    --index-url "https://download.pytorch.org/whl/${TORCH_FLAVOR}"
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install transformers

# Note: --inexact to preserve torch
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --all-packages --inexact

# Signal Python we're Docker
ENV WINDOW_BACKEND="headless"

# ------------------------------------------------------------------------------------------------ #
# Image optimizations

# Clean caches, sources, etc.
RUN rm -rf /var/lib/apt/lists/* .git && \
    uv cache clean && \
    apt clean

# ------------------------------------------------------------------------------------------------ #
