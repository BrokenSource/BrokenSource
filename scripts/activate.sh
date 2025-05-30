#!/bin/bash
chmod +x "$BASH_SOURCE"
cd "$(dirname "$0")/.."
./Website/get.sh
