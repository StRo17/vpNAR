# nur für lokalen Test - auf Pi Linux dann automatisieren über cron, systemd
import time
import subprocess

while True:
    print("📥 Lade aktuelle Pläne...")
    subprocess.run(['python', 'actual_load.py'])
    print("⏳ Warte 180 Sekunden...\n")
    time.sleep(180)  # 3 Minuten
