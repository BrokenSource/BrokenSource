
# Build essential and MinGW toolchain
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt install -y build-essential gcc-mingw-w64-x86-64
