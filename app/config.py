import os

# app/config.py

# Debug
DEBUG_MODE = True

# Cron-Intervalle (Sekunden)
RELOAD_INTERVAL = 7.15 * 60  # substitution load
AUTO_RELOAD_PLAN = 3 * 60  # actual_load etc.

# Verzeichnisse und Pfade
SUBSTITUTION_DIR = os.path.join(os.path.dirname(__file__), "data", "vertretungen")
BANNER_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "banner_config.json")

# Web‐Server-Ports
PORT_STUDENT = 5000
PORT_TEACHER = 5001
PORT_ROTATOR = 5003
PORT_BANNER = 5010

# HTML Meta-Refresh (per Template genutzt)
HTML_REFRESH_INTERVAL = 60
