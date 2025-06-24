#!/usr/bin/env python3
"""
Klassifiziert alle JSON in data/{original,1_future,2_future,3_future} nach Datum.

original:   delta == 0
1_future:   1 <= delta <= 7
2_future:   8 <= delta <= 14
3_future:  15 <= delta <= 21
delta < 0:  löschen
delta > 21: unbehandelt
"""
import logging
import shutil
from pathlib import Path
from datetime import date

# ──────────────────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

BASE = Path("./data")
DIR_ORIG = BASE / "original"
DIR_F1 = BASE / "1_future"
DIR_F2 = BASE / "2_future"
DIR_F3 = BASE / "3_future"

for d in (DIR_ORIG, DIR_F1, DIR_F2, DIR_F3):
    d.mkdir(parents=True, exist_ok=True)

today = date.today()


def date_from_filename(fname: str) -> date | None:
    """Erwartet <klasse>_YYYY-MM-DD.json"""
    try:
        part = fname.rsplit("_", 1)[1].split(".")[0]
        return date.fromisoformat(part)
    except Exception:
        return None


def relocate(file: Path, target_dir: Path):
    """Verschiebe file nach target_dir"""
    dst = target_dir / file.name
    shutil.move(str(file), str(dst))
    logging.info("→ %s -> %s", file.name, target_dir.name)


# ──────────────────────────────────────────────────────────────────────────────
# Hauptprogramm
# ──────────────────────────────────────────────────────────────────────────────
for folder in (DIR_ORIG, DIR_F1, DIR_F2, DIR_F3):
    for f in folder.glob("*.json"):
        dt = date_from_filename(f.name)
        if dt is None:
            logging.warning("Ungültiges Datum: %s", f.name)
            continue

        delta = (dt - today).days

        # 1) delta < 0: löschen
        if delta < 0:
            f.unlink()
            logging.info("✗ gelöscht (veraltet): %s", f.name)
            continue

        # 2) Richtige Zielordner ermitteln
        if delta == 0:
            target = DIR_ORIG
        elif 1 <= delta <= 7:
            target = DIR_F1
        elif 8 <= delta <= 14:
            target = DIR_F2
        elif 15 <= delta <= 21:
            target = DIR_F3
        else:
            # delta > 21: hier nichts tun
            continue

        # 3) Verschieben, falls nötig
        if f.parent != target:
            relocate(f, target)

logging.info("Shift-Vorgang abgeschlossen.")
