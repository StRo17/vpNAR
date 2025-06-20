# Beispiel-Dockerfile im Ordner tv-keeper
FROM alpine:latest

# Dein Script rein kopieren
COPY keep-tv-on.sh /usr/local/bin/keep-tv-on.sh
RUN chmod +x /usr/local/bin/keep-tv-on.sh

# Default-CMD
CMD ["/usr/local/bin/keep-tv-on.sh"]

# Healthcheck: prüft, ob das Script noch läuft
HEALTHCHECK --interval=1m --timeout=10s --start-period=30s --retries=5 \
  CMD pgrep -f keep-tv-on.sh >/dev/null || exit 1
