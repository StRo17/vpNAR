#!/usr/bin/env python3
"""
Vergleicht ./data/actual/*_<yyyy-mm-dd>.json mit
./data/original/*_<yyyy-mm-dd>.json und schreibt Änderungen nach
data/vertretungen/schueler/schueler_<yyyy-mm-dd>.json
und data/vertretungen/lehrer/lehrer_<yyyy-mm-dd>.json
"""
import json
import logging
from pathlib import Path
from datetime import date

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

BASE = Path("./data")
DIR_ACT = BASE / "actual"
DIR_ORIG = BASE / "original"
DIR_DIFF = BASE / "vertretungen"
today = date.today().strftime("%Y-%m-%d")


def load_json(path: Path):
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def period_key(p) -> tuple:
    return (
        p["start"],
        p["end"],
        "|".join(sorted(p.get("rooms", []))),
        "|".join(sorted(p.get("subjects", []))),
        "|".join(sorted(p.get("teachers", []))),
    )


def diff_lists(orig, act):
    orig_map = {period_key(p): p for p in orig}
    act_map = {period_key(p): p for p in act}
    diffs = []
    # entfallen
    for k, p in orig_map.items():
        if k not in act_map:
            diffs.append({"status": "ENTFÄLLT", **p})
    # neu
    for k, p in act_map.items():
        if k not in orig_map:
            diffs.append({"status": "NEU", **p})
    return diffs


def main():
    # 1) Pro Klasse diff erzeugen
    diffs_by_class = {}
    for act_file in sorted(DIR_ACT.glob(f"*_{today}.json")):
        cls = act_file.stem.split("_")[0]
        orig_file = DIR_ORIG / act_file.name
        orig = load_json(orig_file)
        act = load_json(act_file)
        diffs = diff_lists(orig, act) if orig else []
        diffs_by_class[cls] = diffs
        logging.info("Δ %s → %d", act_file.name, len(diffs))

    # 2) Schueler-Aggregat
    sch_dir = DIR_DIFF / "schueler"
    sch_dir.mkdir(parents=True, exist_ok=True)
    sch_file = sch_dir / f"schueler_{today}.json"
    sch_file.write_text(json.dumps(diffs_by_class, ensure_ascii=False, indent=2), encoding="utf-8")
    logging.info("→ %s", sch_file)

    # 3) Lehrer-Aggregat
    lehrer_list = []
    for cls, periods in diffs_by_class.items():
        for p in periods:
            for t in p.get("teachers", []):
                lehrer_list.append(
                    {
                        "teacher": t,
                        "klasse": cls,
                        "start": p.get("start"),
                        "end": p.get("end"),
                        "rooms": p.get("rooms", []),
                        "subjects": p.get("subjects", []),
                        "status": p.get("status"),
                    }
                )
    # sortieren
    lehrer_list.sort(key=lambda x: x["teacher"])
    l_dir = DIR_DIFF / "lehrer"
    l_dir.mkdir(parents=True, exist_ok=True)
    l_file = l_dir / f"lehrer_{today}.json"
    l_file.write_text(json.dumps(lehrer_list, ensure_ascii=False, indent=2), encoding="utf-8")
    logging.info("→ %s", l_file)


if __name__ == "__main__":
    main()
