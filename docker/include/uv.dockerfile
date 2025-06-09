
# Install uv, create and activate a virtual environment
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
ENV PATH="/app/.venv/bin:$PATH"
ENV VIRTUAL_ENV="/app/.venv"
ENV UV_LINK_MODE="copy"
ARG PYTHON_VERSION=3.13
RUN --mount=type=bind,source=.python-version,target=.python-version \
    uv venv "$VIRTUAL_ENV"
