# syntax=devthefuture/dockerfile-x@sha256:263815a4cfdbfdd302e6c7f5d4147e43004f456b0566ac300bf8ae468a9458b1
INCLUDE ./docker/include/base.dockerfile
INCLUDE ./docker/include/opengl.dockerfile

# ------------------------------------------------------------------------------------------------ #

LABEL org.opencontainers.image.title="OpenGL Diagnosis"
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt install -y mesa-utils xvfb --no-install-recommends --no-install-suggests
CMD echo "-------------------------------------------------------------------------------" && \
    echo "Make sure you are running docker with '--gpus all' or defining it on compose"    && \
    echo "-------------------------------------------------------------------------------" && \
    echo ":: (eglinfo) You should see your EGL Device below on Linux, and errors on WSL"   && \
    echo "-------------------------------------------------------------------------------" && \
    eglinfo -B | grep -v '^[0-9]'                                                          && \
    echo "-------------------------------------------------------------------------------" && \
    echo ":: (glxinfo) You should see llvmpipe below on Linux, and a D3D12 adapter on WSL" && \
    echo "-------------------------------------------------------------------------------" && \
    xvfb-run glxinfo -B | grep -v '^[0-9]'                                                 && \
    echo "-------------------------------------------------------------------------------" && \
    echo ":: (system) You should have a 'libEGL_nvidia.so.*' file on /usr/lib:"            && \
    echo "-------------------------------------------------------------------------------" && \
    find /usr/lib | grep -i 'libegl'                                                       && \
    echo "-------------------------------------------------------------------------------"
