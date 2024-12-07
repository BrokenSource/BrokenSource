FROM broken-base
LABEL org.opencontainers.image.title="ShaderFlow"
CMD ["uv", "run", "python", "/App/Docker/Scripts/shaderflow.py"]
