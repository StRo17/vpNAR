# Basis-Image (klein, mit bash)
FROM debian:stable-slim

LABEL org.opencontainers.image.title="TV Keeper"
LABEL org.opencontainers.image.description="Hält den TV per HDMI-CEC wach"
LABEL org.opencontainers.image.license="MIT"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.authors="StRo17 <rjggilmour@outlook.de>"

# CEC-Tools & curl
RUN apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    cec-utils curl bash \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /tv-keeper

# Hier: einfach aus dem build-context kopieren (der ist bereits ./tv-keeper)
COPY keep-tv-on.sh ./

RUN chmod +x keep-tv-on.sh

ENTRYPOINT ["./keep-tv-on.sh"]

# Healthcheck: sendet per CEC 'on 0' und schlägt fehl, wenn der TV noch aus ist
HEALTHCHECK --interval=1m --timeout=10s --start-period=30s --retries=3 \
  CMD echo "on 0" | cec-client -s -d 1 >/dev/null || exit 1
