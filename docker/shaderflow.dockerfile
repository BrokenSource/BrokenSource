FROM broken-base
LABEL org.opencontainers.image.title="ShaderFlow"
CMD ["python", "/app/docker/scripts/shader.py"]
