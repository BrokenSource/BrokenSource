
# Add Vulkan ICD loaders and libraries
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt install -y libvulkan1 libvulkan-dev && \
    mkdir -p /usr/share/vulkan/icd.d && \
    echo '{"file_format_version":"1.0.0","ICD":{"library_path":"libGLX_nvidia.so.0","api_version":"1.3"}}' > \
    /usr/share/vulkan/icd.d/nvidia_icd.json
