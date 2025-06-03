#!/bin/bash
chmod +x "$BASH_SOURCE"
cd "$(dirname "$0")/.."

# Sync all but private packages
sed -i 's/"meta/# "meta/g' pyproject.toml
uv sync --all-packages --upgrade
# uv export --all-packages --no-dev -o pylock.toml > /dev/null
# uv export --all-packages --no-dev -o requirements.txt --no-annotate --no-hashes > /dev/null
sed -i 's/# "meta/"meta/g' pyproject.toml

# Stage current lock, do not track changes
git update-index --no-assume-unchanged uv.lock
git add uv.lock # pylock.toml requirements.txt
git update-index --assume-unchanged uv.lock

# Sync private packages
uv sync --all-packages
