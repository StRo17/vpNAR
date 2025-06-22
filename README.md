# Vertretungsplan + TV-Keeper

Dieses Repository enthält zwei Dockerized-Services:

1. **vertretungen_app**  
   - Flask-Webservice für Schüler- & Lehrer-Vertretungspläne  
   - Lädt via WebUntis-API aktuelle und zukünftige Stundenpläne  
   - Cron-Jobs für regelmäßige Updates  
   - Banner-Anzeige per JSON-Config

2. **tv-keeper**  
   - Hält per HDMI-CEC den TV wach  
   - Läuft als Side-Car und stellt sicher, dass der Bildschirm nicht in Standby geht

## Voraussetzungen

- Docker & Docker Compose  
- Raspberry Pi mit `/dev/vchiq` für CEC-Zugriff

## Installation

1. Kopiere `.env.example` zu `.env` und fülle die WebUntis-Zugangsdaten aus.
2. Erstelle `banner_config.json` mit gewünschtem Banner-Text/Modus.
3. Starte alle Services:

   ```bash
   docker-compose up --build -d


# MINT-Akademie – Vertretungsplan

## 🚀 Projektstart

```bash
cp .env.example .env
docker-compose up -d --build
