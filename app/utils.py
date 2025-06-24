import os
import json
import logging
from datetime import date

HTML_REFRESH = 60  # Sekündliches Refresh-Intervall

def load_substitution_data(subfolder=None):
    """Lädt Vertretungen (compare.py output) aus data/vertretungen."""
    today = date.today().strftime("%Y-%m-%d")
    base_root = os.path.join(os.path.dirname(__file__), "data", "vertretungen")
    if subfolder == "schueler":
        path = os.path.join(base_root, "schueler", f"schueler_{today}.json")
        try:
            return json.load(open(path, encoding="utf-8"))
        except Exception:
            logging.error("Konnte schueler-Datei nicht laden: %s", path)
        return {}
    if subfolder == "lehrer":
        path = os.path.join(base_root, "lehrer", f"lehrer_{today}.json")
        try:
            return json.load(open(path, encoding="utf-8"))
        except Exception:
            logging.error("Konnte lehrer-Datei nicht laden: %s", path)
        return []
    out = {}
    folder = base_root if subfolder is None else os.path.join(base_root, subfolder)
    if not os.path.isdir(folder):
        logging.warning("Verzeichnis nicht gefunden: %s", folder)
        return out
    for fn in sorted(os.listdir(folder)):
        if fn.endswith(f"_{today}.json"):
            klass = fn.split("_", 1)[0]
            try:
                out[klass] = json.load(open(os.path.join(folder, fn), encoding="utf-8"))
            except Exception:
                out[klass] = []
    return out

def load_banner_json():
    """Lädt Banner-Konfiguration."""
    path = os.path.join(os.path.dirname(__file__), "banner_config.json")
    try:
        return json.load(open(path, encoding="utf-8"))
    except Exception:
        return {"mode": "none", "text": ""}