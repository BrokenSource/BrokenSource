FROM nvidia/opengl:1.2-glvnd-runtime-ubuntu22.04
ARG DEBIAN_FRONTEND=noninteractive
WORKDIR /app

# Base requirements
RUN apt update && apt install -y python3 python3-pip python-is-python3 curl
RUN pip install torch==2.3.0 --index-url https://download.pytorch.org/whl/cpu
RUN pip install transformers

# Get FFmpeg with optimizations
ARG FFMPEG_FLAVOR="ffmpeg-master-latest-linux64-gpl"
ARG FFMPEG_URL="https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/${FFMPEG_FLAVOR}.tar.xz"
RUN curl -L ${FFMPEG_URL} | tar -xJ -C /usr/local/bin
RUN cp /usr/local/bin/${FFMPEG_FLAVOR}/bin/* /usr/local/bin

# Importing SoundCard needs libpulse.so
RUN apt install -y pulseaudio

# Install a release version of `broken-source` wheel
RUN python3 -m pip install broken-source==0.3.3.dev0

# Basic required configuration
ENV NVIDIA_DRIVER_CAPABILITIES="all"
ENV NVIDIA_VISIBLE_DEVICES="all"
ENV WINDOW_BACKEND="headless"

# Don't use llvmpipe (Software Rendering) on WSL
ENV MESA_D3D12_DEFAULT_ADAPTER_NAME="NVIDIA"
ENV LD_LIBRARY_PATH=/usr/lib/wsl/lib

# Signal Python we're Docker
ENV DOCKER_RUNTIME="1"

# Gradio apps
ENV GRADIO_SERVER_NAME="0.0.0.0"
EXPOSE 7860

# Install development version of broken-source
COPY . /app
RUN python3 -m pip install --upgrade --no-deps .
