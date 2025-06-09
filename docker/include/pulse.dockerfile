
# SoundCard needs libpulse.so and server
RUN apt install -y pulseaudio && \
    adduser root pulse-access
