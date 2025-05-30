#!/bin/bash
chmod +x "$BASH_SOURCE"
cd "$(dirname "$0")/.."
git submodule update --init --recursive --jobs 4
git submodule foreach --recursive 'git checkout main || true'
git pull --recurse-submodules --rebase --jobs 4
