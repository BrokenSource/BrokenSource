#!/bin/bash
cd "$(dirname "$0")"/..
git submodule update --init --recursive --jobs 4
git submodule foreach --recursive 'git checkout main || true'
git pull --recurse-submodules --jobs 4
