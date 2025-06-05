# ------------------------------------------------------------------------------------------------ #
# (c) MIT License (dockerfile), Tremeschin
# ------------------------------------------------------------------------------------------------ #

ARG FEATURE_OPENGL="0"
ARG FEATURE_VULKAN="0"
ARG FEATURE_PULSE="0"
ARG FEATURE_FFMPEG="0"
ARG FEATURE_UPSCAYL="0"
ARG FEATURE_DEPTHMAP="0"
ARG FEATURE_TORCH="0"
ARG FEATURE_MONOREPO="1"
ARG EDITABLE="0"

# ------------------------------------------------------------------------------------------------ #

ARG BASE_IMAGE="ubuntu:24.04"
FROM ${BASE_IMAGE} AS initial
LABEL org.opencontainers.image.title="BrokenBase"
LABEL org.opencontainers.image.description="Batteries-included image for all Broken Source projects"
LABEL org.opencontainers.image.source="https://github.com/BrokenSource/BrokenSource"
LABEL org.opencontainers.image.url="https://github.com/orgs/BrokenSource/packages"
LABEL org.opencontainers.image.documentation="https://brokensrc.dev/"
LABEL org.opencontainers.image.authors="Tremeschin"
LABEL org.opencontainers.image.licenses="MIT"
ENV DEBIAN_FRONTEND="noninteractive"
RUN apt update
WORKDIR "/app"

# ------------------------------------------------------------------------------------------------ #

# Install uv, create and activate a virtual environment
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
ENV PATH="/app/.venv/bin:$PATH"
ENV VIRTUAL_ENV="/app/.venv"
ENV UV_COMPILE_BYTECODE="1"
ENV UV_LINK_MODE="copy"
RUN uv venv "$VIRTUAL_ENV" --python 3.13

# ------------------------------------------------------------------------------------------------ #
# Make Vulkan and OpenGL EGL acceleration work on NVIDIA (the unveiled magic of nvidia/glvnd)

FROM initial AS opengl-0
FROM initial AS opengl-1

# Nvidia container toolkit configuration
ENV NVIDIA_DRIVER_CAPABILITIES="all"
ENV NVIDIA_VISIBLE_DEVICES="all"

# Don't use llvmpipe (software rendering) on WSL
ENV MESA_D3D12_DEFAULT_ADAPTER_NAME="NVIDIA"
ENV LD_LIBRARY_PATH="/usr/lib/wsl/lib"

# (ShaderFlow) Don't use glfw
ENV WINDOW_BACKEND="headless"

# Add libEGL ICD loaders and libraries
RUN apt install -y libglvnd0 libglvnd-dev libegl1-mesa-dev && \
    mkdir -p /usr/share/glvnd/egl_vendor.d && \
    echo '{"file_format_version":"1.0.0","ICD":{"library_path":"libEGL_nvidia.so.0"}}' > \
    /usr/share/glvnd/egl_vendor.d/10_nvidia.json

# ------------------------------------------------------------------------------------------------ #

FROM opengl-${FEATURE_OPENGL} AS vulkan-0
FROM opengl-${FEATURE_OPENGL} AS vulkan-1

# Add Vulkan ICD loaders and libraries
RUN apt install -y libvulkan1 libvulkan-dev && \
    mkdir -p /usr/share/vulkan/icd.d && \
    echo '{"file_format_version":"1.0.0","ICD":{"library_path":"libGLX_nvidia.so.0","api_version":"1.3"}}' > \
    /usr/share/vulkan/icd.d/nvidia_icd.json

# ------------------------------------------------------------------------------------------------ #

FROM vulkan-${FEATURE_VULKAN} AS pulse-0
FROM vulkan-${FEATURE_VULKAN} AS pulse-1

# (ShaderFlow) SoundCard needs libpulse.so and server
RUN apt install -y pulseaudio && \
    adduser root pulse-access

# ------------------------------------------------------------------------------------------------ #

FROM pulse-${FEATURE_PULSE} AS ffmpeg-0
FROM pulse-${FEATURE_PULSE} AS ffmpeg-1

RUN apt install -y ffmpeg

# ------------------------------------------------------------------------------------------------ #

FROM ffmpeg-${FEATURE_FFMPEG} AS upscayl-0
FROM ffmpeg-${FEATURE_FFMPEG} AS upscayl-1

# Strip electron part of the package
RUN apt install -y curl
RUN curl -L "https://github.com/upscayl/upscayl/releases/download/v2.15.0/upscayl-2.15.0-linux.deb" \
    -o /tmp/upscayl.deb && apt install -y /tmp/upscayl.deb && rm /tmp/upscayl.deb && mkdir -p /opt/upscayl && \
    mv /opt/Upscayl/resources/models /opt/upscayl/models && \
    mv /opt/Upscayl/resources/bin /opt/upscayl/bin && \
    rm -rf /opt/Upscayl

# ------------------------------------------------------------------------------------------------ #

FROM upscayl-${FEATURE_UPSCAYL} AS depthmap-0
FROM upscayl-${FEATURE_UPSCAYL} AS depthmap-1

# Cache depth estimator models
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install huggingface-hub && \
    huggingface-cli download "depth-anything/Depth-Anything-V2-small-hf"

# ------------------------------------------------------------------------------------------------ #

FROM depthmap-${FEATURE_DEPTHMAP} AS torch-0
FROM depthmap-${FEATURE_DEPTHMAP} AS torch-1

# Install a PyTorch flavor
ARG TORCH_VERSION="2.7.0"
ARG TORCH_FLAVOR="cpu"
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install torch=="${TORCH_VERSION}+${TORCH_FLAVOR}" \
    --index-url "https://download.pytorch.org/whl/${TORCH_FLAVOR}"

# ------------------------------------------------------------------------------------------------ #

FROM torch-${FEATURE_TORCH} AS monorepo-0
FROM torch-${FEATURE_TORCH} AS monorepo-1

# Install locked dependencies
RUN apt install -y git
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --inexact --no-dev

# ------------------------------------------------------------------------------------------------ #

# Clone the latest commited code
FROM monorepo-${FEATURE_MONOREPO} AS development-0
    ARG REPOSITORY="https://github.com/BrokenSource/BrokenSource"
    RUN git clone --recurse-submodules --jobs 4 "${REPOSITORY}" ./clone && \
        cp -r ./clone/. . && rm -rf ./clone && \
        git submodule foreach --recursive 'git checkout main || true' && \
        git pull --recurse-submodules && rm -rf .git
    RUN --mount=type=cache,target=/root/.cache/uv \
        uv sync --all-packages --inexact --no-dev

# Copy the current editable code
FROM monorepo-${FEATURE_MONOREPO} AS development-1
    COPY . /app
    RUN --mount=type=cache,target=/root/.cache/uv \
        uv sync --all-packages --inexact

# ------------------------------------------------------------------------------------------------ #

FROM development-${EDITABLE} AS final

