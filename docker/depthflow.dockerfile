FROM broken-base
LABEL org.opencontainers.image.title="DepthFlow"
CMD ["python", "/app/docker/scripts/depth.py"]
