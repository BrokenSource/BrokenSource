FROM broken-base
LABEL org.opencontainers.image.title="DepthFlow"

# Have common depth estimators preloaded
RUN depthflow any2 --model small load-estimator \
              any2 --model base  load-estimator

# Have common upscalers preloaded
RUN depthflow upscayl load-upscaler

# Development mode
# COPY . /App
# RUN uv sync --all-packages --inexact

CMD ["uv", "run", "python", "/App/Docker/Scripts/depthflow.py"]
