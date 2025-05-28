#!/bin/bash
cd "$(dirname "$0")/.."

# Sync all but private packages
sed -i 's/"meta/# "meta/g' pyproject.toml
uv sync --all-packages
sed -i 's/# "meta/"meta/g' pyproject.toml

# Stage current lock, do not track changes
git update-index --no-assume-unchanged uv.lock
git add uv.lock
git update-index --assume-unchanged uv.lock

# Sync private packages
uv sync --all-packages
