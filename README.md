# Vertretungsplan + TV-Keeper

Dieses Repository enthält zwei Docker-Services:

1. **vertretungen_app**  
   - Stellt Vertretungspläne via Flask auf Ports 5000 (Schüler) & 5001 (Lehrer) bereit.  
   - Lädt alle 7–8 Min. die aktuellen Daten neu, führt Cron-Jobs aus.  
   - **Healthcheck**: HTTP-GET auf `http://localhost:5000/`.

2. **tv-keeper**  
   - Hält per CEC-Script einen an HDMI angeschlossenen TV wach.  
   - Läuft privilegiert auf dem Raspberry Pi (Device `/dev/vchiq`).  
   - **Healthcheck**: Check, ob `keep-tv-on.sh`-Prozess aktiv ist.

---

## Starten
```bash
docker-compose up --build -d

## Restart
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
