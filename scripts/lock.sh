#!/bin/bash
cd "$(dirname "$0")/.."
sed -i 's/"meta/# "meta/' pyproject.toml
uv sync --all-packages
sed -i 's/# "meta/"meta/' pyproject.toml
