# 0) Basis-Image
FROM python:3.11-slim

# 1) System-Tools (tzdata, cron, curl für Healthcheck)
ENV TZ=Europe/Berlin
RUN apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y tzdata cron curl \
 && ln -fs /usr/share/zoneinfo/$TZ /etc/localtime \
 && dpkg-reconfigure --frontend noninteractive tzdata \
 && rm -rf /var/lib/apt/lists/*

# 2) App-Verzeichnis
WORKDIR /app

# 3) Quellcode & Dependencies
COPY app/ /app/
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 4) Cron-Jobs
COPY webuntis-crontab /etc/cron.d/webuntis-crontab
RUN chmod 0644 /etc/cron.d/webuntis-crontab \
 && crontab /etc/cron.d/webuntis-crontab

# 5) Logs & Startscript
RUN mkdir -p /app/logs \
 && chmod +x /app/start_all.sh

# 6) Container-Start
CMD ["/app/start_all.sh"]

# 7) Healthcheck: prüft alle 30s, ob der Web-Service auf Port 5000 antwortet
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:5000/ || exit 1
