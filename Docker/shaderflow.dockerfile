FROM broken-base
LABEL org.opencontainers.image.title="ShaderFlow"
CMD ["python", "/App/Docker/Scripts/shaderflow.py"]
