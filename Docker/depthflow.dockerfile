FROM broken-base

# Have common depth estimators preloaded
RUN depthflow any2 --model small load-estimator && \
    depthflow any2 --model base  load-estimator

# Have common upscalers preloaded
RUN depthflow upscayl load-upscaler && \
    depthflow realesr load-upscaler && \
    depthflow waifu2x load-upscaler

# Entry point
CMD uv run python /App/Docker/Scripts/depthflow.py
