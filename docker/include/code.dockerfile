
ARG REPOSITORY="https://github.com/BrokenSource/BrokenSource"
ARG UV_SYNC="--all-packages"
ARG EDITABLE="0"

# Optimization: Install known locked dependencies first
# RUN --mount=type=cache,target=/root/.cache/uv \
#     --mount=type=bind,source=uv.lock,target=uv.lock \
#     --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
#     uv sync --frozen --no-install-project --inexact --no-dev

# Copy local code
# COPY . /app

# # Sync dependencies
# ENV UV_COMPILE_BYTECODE="0"
# RUN --mount=type=cache,target=/root/.cache/uv \
#     uv sync --inexact --no-dev --all-extras ${UV_SYNC}

# Clone the latest commited code
RUN apt install -y git
RUN git clone --recurse-submodules --jobs 4 "${REPOSITORY}" ./clone && \
    cp -r ./clone/. . && rm -rf ./clone && \
    git submodule foreach --recursive 'git checkout main || true' && \
    git pull --recurse-submodules && rm -rf .git

# Sync dependencies
ENV UV_COMPILE_BYTECODE="1"
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --inexact --no-dev --all-extras ${UV_SYNC}
