#!/usr/bin/env bash
# start_all.sh – Startscript für Vertretungsplan-Projekt

# 0) Fehler sofort anzeigen, wenn ein Befehl fehlschlägt
set -e

# 1) Starte den Cron-Dienst für zeitgesteuerte Tasks
echo "[START] Starte cron-Dienst..."
cron

# 2) Starte die Schüler-Ansicht (Student-Frontend, Port aus config.py)
echo "[START] Starte Schüleransicht..."
python3 show.py &

# 3) Starte die Lehrer-Ansicht (Teacher-Frontend, ebenfalls in show.py enthalten)
# (Bereits durch show.py auf anderem Port gestartet)

# 4) Starte die Klassenrotation (klassengruppierte Ansicht)
echo "[START] Starte Klassenrotation..."
python3 class_show.py &

# 5) Starte das Banner-Konfigurationsinterface
echo "[START] Starte Bannereditor..."
python3 banner.py &

# 6) Warte auf alle Kindprozesse, damit der Container nicht beendet wird
wait
