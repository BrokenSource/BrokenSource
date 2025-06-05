FROM broken-base:shaderflow
LABEL org.opencontainers.image.title="ShaderFlow"
LABEL org.opencontainers.image.description="🔥 Imagine ShaderToy, on a Manim-like architecture. That's ShaderFlow."
CMD ["shaderflow", "basic", "main", "-o", "video.mp4", "-t", "30"]
