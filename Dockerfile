# 0) Basis-Image
FROM python:3.11-slim

# 1) Metadaten-Labels
LABEL org.opencontainers.image.title="Vertretungsplan App"
LABEL org.opencontainers.image.description="Flask-Service für Schüler-/Lehrer-Vertretungspläne"
LABEL org.opencontainers.image.license="MIT"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.authors="StRo17 <rjggilmour@outlook.de>"

# 2) System-Tools (tzdata, cron, curl für Healthcheck)
ENV TZ=Europe/Berlin
RUN apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y tzdata cron curl \
 && ln -fs /usr/share/zoneinfo/$TZ /etc/localtime \
 && dpkg-reconfigure --frontend noninteractive tzdata \
 && rm -rf /var/lib/apt/lists/*

# 3) App-Verzeichnis
WORKDIR /app

# 4) Quellcode & Abhängigkeiten
COPY app/ /app/
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 5) Cron-Jobs einrichten
COPY webuntis-crontab /etc/cron.d/webuntis-crontab
RUN chmod 0644 /etc/cron.d/webuntis-crontab \
 && crontab /etc/cron.d/webuntis-crontab

# 6) Logs & Startscript
RUN mkdir -p /app/logs \
 && chmod +x /app/start_all.sh

# 7) Default-Command
CMD ["/app/start_all.sh"]

# 8) Healthcheck: prüft, ob der Service antwortet
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:5000/ || exit 1
