#!/usr/bin/env python3
import os
import json
from flask import Flask, render_template_string, request

app = Flask(__name__)

# ──────────────────────────────────────────────────────────────────────────────
# 1) Funktion zum Laden aller aktuellen Plandaten
# ──────────────────────────────────────────────────────────────────────────────
def load_all_data():
    directory = os.path.join(os.path.dirname(__file__), 'data', 'actual')
    if not os.path.isdir(directory):
        return {}
    files = [f for f in os.listdir(directory) if f.endswith('.json')]

    new_data = {}
    for file in files:
        file_path = os.path.join(directory, file)
        try:
            raw = json.load(open(file_path, 'r', encoding='utf-8'))
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            raw = []

        class_name = file.split('_', 1)[0]
        new_data[class_name] = []
        for entry in raw:
            new_data[class_name].append({
                'Start':   entry.get('start', ''),
                'End':     entry.get('end',   ''),
                'Subject': entry.get('subjects', [''])[0],
                'Room':    entry.get('rooms',    [''])[0],
                'Teacher': entry.get('teachers', [''])[0]
            })
    return new_data

# ──────────────────────────────────────────────────────────────────────────────
# 2) Originales HTML-Template
# ──────────────────────────────────────────────────────────────────────────────
html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Stundenplan</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            font-family: Arial, sans-serif;
            width: 95vw;
            height: 95vh;
            overflow: hidden;
        }
        .banner, .fallback-title {
            text-align: center;
            font-size: 2.5vw;
            font-weight: bold;
            padding: 10px;
        }
        .banner {
            background-color: yellow;
            display: none;
        }
        .fallback-title {
            display: none;
        }
        table {
            width: 95%;
            height: 75%;
            border-collapse: collapse;
            font-size: 1.3vw;
            margin: 0 auto;
        }
        th, td {
            border: 1px solid #333;
            padding: 8px;
            text-align: center;
        }
        th {
            background-color: #0074D9;
            color: white;
        }
    </style>
    <script>
        const groups = {{ groups | safe }};
        const currentGroup = "{{ current_group }}";
        let currentIndex = groups.indexOf(currentGroup);

        function rotate() {
            currentIndex = (currentIndex + 1) % groups.length;
            const nextGroup = groups[currentIndex];
            window.location.href = "/?group=" + encodeURIComponent(nextGroup);
        }

        // alle 10 Sekunden wechseln
        setInterval(rotate, 10000);
    </script>
</head>
<body>
    <div id="banner" class="banner"></div>
    <div id="fallback" class="fallback-title">Stundenplan für: {{ current_group }}</div>

    <table>
        <tr>
            <th>Zeit</th>
            {% for class_name in class_names %}
            <th>{{ class_name }}</th>
            {% endfor %}
        </tr>
        {% for time_slot in time_slots %}
        <tr>
            <td>{{ time_slot }}</td>
            {% for class_name in class_names %}
            <td>
                {% for entry in class_data.get(class_name, []) %}
                    {% if entry['Start'] + ' - ' + entry['End'] == time_slot %}
                        {{ entry['Subject'] }} ({{ entry['Room'] }})<br>
                    {% endif %}
                {% endfor %}
            </td>
            {% endfor %}
        </tr>
        {% endfor %}
    </table>
</body>
</html>
"""

# ──────────────────────────────────────────────────────────────────────────────
# 3) Helfer zum Gruppieren der Klassen
# ──────────────────────────────────────────────────────────────────────────────
def get_class_groups(data):
    groups = {
        "5": [], "6": [], "7": [], "8": [], "9": [], "10": [],
        "IFS": [], "EF": [], "Q1": [], "Q2": []
    }
    for class_name in data.keys():
        if class_name.startswith("05"):
            groups["5"].append(class_name)
        elif class_name.startswith("06"):
            groups["6"].append(class_name)
        elif class_name.startswith("07"):
            groups["7"].append(class_name)
        elif class_name.startswith("08"):
            groups["8"].append(class_name)
        elif class_name.startswith("09"):
            groups["9"].append(class_name)
        elif class_name.startswith("10"):
            groups["10"].append(class_name)
        elif "IFS" in class_name:
            groups["IFS"].append(class_name)
        elif class_name.startswith("EF"):
            groups["EF"].append(class_name)
        elif class_name.startswith("Q1"):
            groups["Q1"].append(class_name)
        elif class_name.startswith("Q2"):
            groups["Q2"].append(class_name)
    # Entferne leere Gruppen
    return {k: v for k, v in groups.items() if v}

# ──────────────────────────────────────────────────────────────────────────────
# 4) Haupt-Route
# ──────────────────────────────────────────────────────────────────────────────
@app.route('/')
def show_timetable():
    # 1) Daten frisch laden
    class_data = load_all_data()

    # 2) Gruppen bestimmen und aktuelle Gruppe wählen
    group = request.args.get("group")
    groups = get_class_groups(class_data)
    group_keys = list(groups.keys())
    if not group_keys:
        return "Keine Gruppen gefunden."
    if group not in group_keys:
        group = group_keys[0]

    # 3) Header-Spalten (Klassen) und Zeitslots
    class_names = groups[group]
    time_slots = sorted({
        f"{e['Start']} - {e['End']}"
        for periods in class_data.values()
        for e in periods
    })

    # 4) Rendern
    return render_template_string(
        html_template,
        class_data=class_data,
        class_names=class_names,
        time_slots=time_slots,
        current_group=group,
        groups=json.dumps(group_keys)
    )

# ──────────────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=False)
