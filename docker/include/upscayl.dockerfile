
# Strip electron part of the package
RUN apt install -y curl
RUN curl -L "https://github.com/upscayl/upscayl/releases/download/v2.15.0/upscayl-2.15.0-linux.deb" \
    -o /tmp/upscayl.deb && apt install -y /tmp/upscayl.deb && rm /tmp/upscayl.deb && mkdir -p /opt/upscayl && \
    mv /opt/Upscayl/resources/models /opt/upscayl/models && \
    mv /opt/Upscayl/resources/bin /opt/upscayl/bin && \
    rm -rf /opt/Upscayl
