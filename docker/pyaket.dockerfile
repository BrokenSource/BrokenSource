# syntax=devthefuture/dockerfile-x@sha256:263815a4cfdbfdd302e6c7f5d4147e43004f456b0566ac300bf8ae468a9458b1
INCLUDE ./docker/include/base.dockerfile
INCLUDE ./docker/include/uv.dockerfile
INCLUDE ./docker/include/rust.dockerfile
INCLUDE ./docker/include/gcc.dockerfile
INCLUDE ./docker/include/code.dockerfile

# ---------------------------------------------------------------------------- #

LABEL org.opencontainers.image.title="Pyaket"
LABEL org.opencontainers.image.description="📦 Easy Python to → Fast Executables"
LABEL org.opencontainers.image.source="https://github.com/BrokenSource/Pyaket"
LABEL org.opencontainers.image.url="https://github.com/orgs/BrokenSource/packages"
LABEL org.opencontainers.image.documentation="https://pyaket.dev/"
LABEL org.opencontainers.image.licenses="AGPL-3.0"
