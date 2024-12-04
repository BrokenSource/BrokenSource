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
# Make OpenGL acceleration with EGL work on NVIDIA

# Basic required configuration
ENV NVIDIA_DRIVER_CAPABILITIES="all"
ENV NVIDIA_VISIBLE_DEVICES="all"

# Don't use llvmpipe (software rendering) on WSL
ENV MESA_D3D12_DEFAULT_ADAPTER_NAME="NVIDIA"
ENV LD_LIBRARY_PATH="/usr/lib/wsl/lib"

# Install libEGL stuff (for non-nvidia glvnd base images)
RUN apt install -y libegl1-mesa-dev libglvnd-dev libglvnd0 && \
    mkdir -p /usr/share/glvnd/egl_vendor.d && \
    echo '{"file_format_version":"1.0.0","ICD":{"library_path":"/usr/lib/x86_64-linux-gnu/libEGL_nvidia.so.0"}}' > \
    /usr/share/glvnd/egl_vendor.d/10_nvidia.json

# ------------------------------------------------------------------------------------------------ #
# Base requirements

# Video encoding and decoding
RUN apt install -y xz-utils curl
ARG FFMPEG_FLAVOR="ffmpeg-master-latest-linux64-gpl"
ARG FFMPEG_URL="https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/${FFMPEG_FLAVOR}.tar.xz"
RUN curl -L ${FFMPEG_URL} | tar -xJ --strip-components=2 --exclude="doc" --exclude="man" -C /usr/local/bin

# SoundCard needs libpulse.so and server
RUN apt install -y pulseaudio
RUN adduser root pulse-access

# Install uv and create a virtual environment
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
ENV UV_COMPILE_BYTECODE="1"
ENV VIRTUAL_ENV="/App/.venv"
ENV PATH="/App/.venv/bin:$PATH"
RUN uv venv --python 3.12 "$VIRTUAL_ENV"

# Install a PyTorch flavor
ARG TORCH_VERSION="2.5.1"
ARG TORCH_FLAVOR="cpu"
RUN uv pip install torch=="${TORCH_VERSION}+${TORCH_FLAVOR}" \
    --index-url "https://download.pytorch.org/whl/${TORCH_FLAVOR}"
RUN uv pip install transformers

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

# Signal Python we're Docker
ENV WINDOW_BACKEND="headless"

# ------------------------------------------------------------------------------------------------ #
# Image optimizations

# Clean apt caches and sources
RUN apt clean && rm -rf /var/lib/apt/lists/*

# Don't need the cache anymore
RUN uv cache clean

# ------------------------------------------------------------------------------------------------ #
