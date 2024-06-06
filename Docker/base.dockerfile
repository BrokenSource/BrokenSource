FROM nvidia/opengl:1.2-glvnd-runtime-ubuntu22.04
ARG DEBIAN_FRONTEND=noninteractive

# Base requirements
RUN apt update && apt install -y python3 python3-pip curl
RUN pip install torch==2.3.0 --index-url https://download.pytorch.org/whl/cpu
RUN pip install transformers

# Get FFmpeg with optimizations
ARG FFMPEG_FLAVOR="ffmpeg-master-latest-linux64-gpl"
ARG FFMPEG_URL="https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/${FFMPEG_FLAVOR}.tar.xz"
RUN curl -L ${FFMPEG_URL} | tar -xJ -C /usr/local/bin
RUN cp /usr/local/bin/${FFMPEG_FLAVOR}/bin/* /usr/local/bin

# Basic required configuration
ENV NVIDIA_VISIBLE_DEVICES="all"
ENV NVIDIA_DRIVER_CAPABILITIES="all"
ENV WINDOW_BACKEND="headless"
ENV DOCKER_RUNTIME="1"

# Gradio apps
ENV GRADIO_SERVER_NAME="0.0.0.0"
EXPOSE 7860

# Stable:
RUN python3 -m pip install broken-source==0.3.2

# BrokenSource monorepo
WORKDIR /app
COPY . /app

# Latest:
RUN python3 -m pip install --upgrade --no-deps .
