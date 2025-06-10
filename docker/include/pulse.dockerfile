
# SoundCard needs libpulse.so and server
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt install -y pulseaudio && adduser root pulse-access
