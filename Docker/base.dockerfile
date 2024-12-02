# ------------------------------------------------------------------------------------------------ #
# (c) MIT License, Tremeschin
# Dockerfile v2024.12.1
# ------------------------------------------------------------------------------------------------ #
# General metadata and configuration

FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt update
WORKDIR /App

# ------------------------------------------------------------------------------------------------ #
# Make OpenGL acceleration with EGL work on NVIDIA

# Basic required configuration
ENV NVIDIA_DRIVER_CAPABILITIES="all"
ENV NVIDIA_VISIBLE_DEVICES="all"

# Don't use llvmpipe (Software Rendering) on WSL
ENV MESA_D3D12_DEFAULT_ADAPTER_NAME="NVIDIA"
ENV LD_LIBRARY_PATH=/usr/lib/wsl/lib

# Install libEGL stuff (for non-nvidia glvnd base images)
RUN apt install -y libegl1-mesa-dev libglvnd-dev libglvnd0
RUN mkdir -p /usr/share/glvnd/egl_vendor.d
RUN echo '{"file_format_version":"1.0.0","ICD":{"library_path":"/usr/lib/x86_64-linux-gnu/libEGL_nvidia.so.0"}}' > \
    /usr/share/glvnd/egl_vendor.d/10_nvidia.json

# ------------------------------------------------------------------------------------------------ #
# Base requirements

# Install uv and create a virtual environment
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
ENV UV_COMPILE_BYTECODE=1
RUN uv venv --python 3.12
ENV VIRTUAL_ENV=/App/.venv
ENV PATH="/App/.venv/bin:$PATH"

# Install a PyTorch flavor
ARG TORCH_VERSION="2.5.1"
ARG TORCH_FLAVOR="cpu"
RUN uv pip install torch==${TORCH_VERSION}+${TORCH_FLAVOR} \
    --index-url https://download.pytorch.org/whl/${TORCH_FLAVOR}
RUN uv pip install transformers

# Video encoding and decoding
RUN apt install -y ffmpeg

# SoundCard needs libpulse.so and server
RUN apt install -y pulseaudio
RUN adduser root pulse-access

# ------------------------------------------------------------------------------------------------ #
# Broken Source stuff

# Install latest release
RUN uv pip install \
    depthflow \
    pianola \
    shaderflow \
    spectronote

# Install development version of broken-source
# Note: --inexact to preserve torch
COPY . /App
RUN uv sync --all-packages --inexact

# Don't need the cache anymore
RUN uv cache clean

# Signal Python we're Docker
ENV WINDOW_BACKEND="headless"
ENV DOCKER_RUNTIME="1"

# ------------------------------------------------------------------------------------------------ #
