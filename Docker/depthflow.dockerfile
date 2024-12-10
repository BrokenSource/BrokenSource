FROM broken-base
LABEL org.opencontainers.image.title="DepthFlow"
CMD ["python", "./Docker/Scripts/depthflow.py"]
