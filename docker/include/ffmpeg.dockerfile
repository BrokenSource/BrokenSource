
# FFmpeg for video/audio processing
RUN apt install -y curl tar xz-utils
ARG FFMPEG="ffmpeg-master-latest-linux64-gpl"
RUN curl -L "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/${FFMPEG}.tar.xz" | \
    tar -xJ --strip-components=2 --exclude="doc" --exclude="man" -C /usr/local/bin

# Can also get from apt, but bigger images
# RUN apt install -y ffmpeg
