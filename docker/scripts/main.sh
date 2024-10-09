#!/bin/bash

# Note: This must be done on the same .sh we'll run Python with soundcard
pulseaudio --verbose --exit-idle-time=-1 --system --disallow-exit -D > /dev/null 2>&1

# Switch case on the first argv
case "$1" in
    "depthflow")
        python /app/docker/scripts/depthflow.py
        ;;
    "shaderflow")
        python /app/docker/scripts/shaderflow.py
        ;;
    *)
        echo "Unrecognized command: $1"
        ;;
esac
