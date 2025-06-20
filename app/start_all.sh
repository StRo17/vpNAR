#!/usr/bin/env bash
# ~/Vertretungen/app/start_all.sh

# 1) Cron-Daemon im Hintergrund starten ;-)
cron

# 2) Show-Services starten (Student & Lehrer)
python3 show.py &        # Port 5000/5001

# 3) Stundenplan-Rotator starten
python3 class_show.py &  # Port 5003

# Banner starten (im Hintergrund)
python3 /app/banner.py & # Port 5051

# 5) Auf alle Kindprozesse warten, damit der Container aktiv bleibt
wait
