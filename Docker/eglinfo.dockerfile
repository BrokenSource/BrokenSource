FROM broken-base:latest
RUN apt install -y mesa-utils

# Your GPU must show up for Hardware Acceleration. 'llvmpipe' is software rendering
# Note: On Windows, you might encountry a Mesa D3D12 adapter, which is right
# You should see a "libEGL_nvidia.so.*" file on the /usr/lib path
CMD eglinfo -B | grep -v '^[0-9]' && \
    find /usr/lib | grep "libEGL"
