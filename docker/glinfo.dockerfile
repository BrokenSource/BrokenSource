FROM broken-base:glinfo
LABEL org.opencontainers.image.title="OpenGL Diagnosis"
RUN apt install -y mesa-utils xvfb
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
