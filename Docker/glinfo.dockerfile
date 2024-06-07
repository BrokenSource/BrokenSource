FROM broken-base:latest
RUN apt install -y mesa-utils xvfb
CMD echo "-------------------------------------------------------------------------------" && \
    echo ":: (eglinfo) You should see your EGL Device below on Linux, and errors on WSL" && \
    echo "-------------------------------------------------------------------------------" && \
    eglinfo -B | grep -v '^[0-9]' && \
    echo "-------------------------------------------------------------------------------" && \
    echo ":: (glxinfo) You should see a D3D12 adapter below on WSL, and llvmpipe on Linux" && \
    echo "-------------------------------------------------------------------------------" && \
    xvfb-run glxinfo -B | grep -v '^[0-9]' && \
    echo "-------------------------------------------------------------------------------" && \
    echo ":: (filesystem) You _might_ have a 'libEGL_nvidia.so.*' file on /usr/lib:" && \
    echo "-------------------------------------------------------------------------------" && \
    find /usr/lib | grep -i 'libegl' && \
    echo "-------------------------------------------------------------------------------"
