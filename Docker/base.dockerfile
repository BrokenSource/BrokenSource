FROM nvidia/opengl:1.2-glvnd-runtime-ubuntu22.04
ARG DEBIAN_FRONTEND=noninteractive
WORKDIR /App

# Base requirements
RUN apt update && apt install -y python3 python3-pip python-is-python3 curl
RUN pip install torch==2.4.1 --index-url https://download.pytorch.org/whl/cpu
RUN pip install transformers

# Fixme: Why BtbN FFmpeg binaries "are faster" than 'apt install ffmpeg'?
ARG FFMPEG_FLAVOR="ffmpeg-master-latest-linux64-gpl"
ARG FFMPEG_URL="https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/${FFMPEG_FLAVOR}.tar.xz"
RUN curl -L ${FFMPEG_URL} | tar -xJ --strip-components=2 --exclude="doc" --exclude="man" -C /usr/local/bin

# ------------------------------------------------------------------------------------------------ #
# Audio

# SoundCard needs libpulse.so and server
RUN apt install -y pulseaudio
RUN adduser root pulse-access

# ------------------------------------------------------------------------------------------------ #
# Broken Source stuff

# Use uv for faster package installation
RUN python -m pip install uv

# Install latest release
RUN python -m uv pip install \
    depthflow \
    pianola \
    shaderflow \
    spectronote

# Signal Python we're Docker
ENV WINDOW_BACKEND="headless"
ENV DOCKER_RUNTIME="1"

# Important: Cache Depth Estimator model
RUN python -m DepthFlow load-model

# Install development version of broken-source
COPY . /App
RUN python -m uv pip install --upgrade .[all] \
    ./Projects/DepthFlow \
    ./Projects/Pianola \
    ./Projects/ShaderFlow \
    ./Projects/SpectroNote \
    --no-deps

# ------------------------------------------------------------------------------------------------ #
# NVIDIA

# Basic required configuration
ENV NVIDIA_DRIVER_CAPABILITIES="all"
ENV NVIDIA_VISIBLE_DEVICES="all"

# Don't use llvmpipe (Software Rendering) on WSL
ENV MESA_D3D12_DEFAULT_ADAPTER_NAME="NVIDIA"
ENV LD_LIBRARY_PATH=/usr/lib/wsl/lib

# ------------------------------------------------------------------------------------------------ #
