FROM broken-base:depthflow
LABEL org.opencontainers.image.title="DepthFlow"
LABEL org.opencontainers.image.description="🌊 Images to → 3D Parallax effect video. A free and open source ImmersityAI alternative"
CMD ["depthflow", "gradio"]
