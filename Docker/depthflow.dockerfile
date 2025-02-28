FROM broken-base
LABEL org.opencontainers.image.title="DepthFlow"
CMD ["python", "/App/Docker/Scripts/depthflow.py"]
