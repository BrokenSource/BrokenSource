#!/bin/bash

# Note: This must be done on the same .sh we'll run Python with soundcard
pulseaudio --verbose --exit-idle-time=-1 --system --disallow-exit -D > /dev/null 2>&1

# Switch case on the first argv
case "$1" in
    "depthflow")
        python /App/Docker/Scripts/depthflow.py
        ;;
    "shaderflow")
        python /App/Docker/Scripts/shaderflow.py
        ;;
    *)
        echo "Unrecognized command: $1"
        ;;
esac
