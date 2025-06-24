FROM python:3.11-slim

ENV TZ=Europe/Berlin
RUN apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y tzdata cron curl \
 && ln -fs /usr/share/zoneinfo/$TZ /etc/localtime \
 && dpkg-reconfigure --frontend noninteractive tzdata \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
# inkl. templates/
COPY ./app/ /app/
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY webuntis-crontab /etc/cron.d/webuntis-crontab
RUN chmod 0644 /etc/cron.d/webuntis-crontab \
 && crontab /etc/cron.d/webuntis-crontab

RUN mkdir -p /app/logs \
 && chmod +x /app/start_all.sh

CMD ["/app/start_all.sh"]

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:5000/ || exit 1