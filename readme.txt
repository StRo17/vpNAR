# Grundstruktur
	/data
		/original/2025-07-07.json     # In 21 Tagen (Original)
		/actual/2025-07-07.json       # Aktuell abgerufen
		/vertretungen/2025-07-07.json # Berechnete Unterschiede
		/1_future/2025-07-28.json     # Wird in 7 Tagen „original“
		/2_future/2025-08-04.json     # In 14 Tagen „original“
		/3_future/2025-08-11.json     # In 21 Tagen „original“
	Die Dateien liegen alle direkt im jeweiligen Ordner (original, actual, 3_future, etc.).


# Ordnerrotation (alle 7 Tage automatisch):
	+7 Tage: /1_future → /original
	+14 Tage: /2_future → /1_future
	+21 Tage: /3_future → /2_future


# alles über die Unterrichtseinheiten der Klassen ableiten:
	- klasse['lessons'] enthält Fach, Lehrer, Raum, Uhrzeit.
	- Die Lehrer-ID oder Name reicht aus.

# Schüleransicht:
	Klasse | Stunde | Raum | Fach | Lehrer

# Lehrkraftansicht:
	Lehrer | Stunde | Raum | Klasse | Fach
	

# Grundgedanke:
	Script original_load.py:
		Lädt Pläne für heute + 49 Tage.
		Speichert sie in /3_future/KLASSENNAME/2025-XX-XX.json.
		Kann täglich laufen oder einmal pro Woche.
	Script rotate_futures.py (optional später):
		Macht die Ordnerrotation (löscht original, verschiebt Inhalte).
		Läuft alle 7 Tage automatisch.
	Script actual_load.py:
		Lädt heute+0 Plan in /actual/KLASSENNAME/2025-XX-XX.json.
	Script compare.py:
		Vergleicht original vs. actual für alle heutigen Klassenpläne.
		Gibt JSON-Dateien mit Veränderungen aus.


# Nötig:
	Login zu WebUntis
	Liste aller Klassen
	Für jede Klasse:
		Abruf von getTimetable für heute + 49 Tage
		Speichern der Ergebnisse als JSON