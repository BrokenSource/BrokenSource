FROM broken-base
LABEL org.opencontainers.image.title="ShaderFlow"
CMD ["python", "./Docker/Scripts/shaderflow.py"]
