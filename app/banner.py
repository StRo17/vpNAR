#!/usr/bin/env python3
import os
import json
from flask import Flask, render_template_string, request, redirect, url_for, jsonify

app = Flask(__name__)
BANNER_FILE = os.path.join(os.path.dirname(__file__), 'banner_config.json')

def load_banner_config():
    """Lädt banner.json oder gibt Default zurück."""
    if os.path.exists(BANNER_FILE):
        with open(BANNER_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'mode': 'none', 'text': ''}

def save_banner_config(cfg):
    with open(BANNER_FILE, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Banner-Konfiguration</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 20px; }
    label { margin-right: 20px; }
    textarea { width: 100%; height: 80%; margin-top: 10px; }
    button { margin-top: 5px; padding: 8px 16px; }
  </style>
</head>
<body>
  <h2>Banner konfigurieren</h2>
  <form method="post">
    <label>
      <input type="radio" name="mode" value="none" {% if mode=='none' %}checked{% endif %}>
      Kein Text
    </label>
    <label>
      <input type="radio" name="mode" value="text" {% if mode=='text' %}checked{% endif %}>
      Text
    </label>
    <br>
    <textarea name="text" placeholder="Bannertext hier eingeben...">{{ text }}</textarea>
    <br>
    <button type="submit">Speichern</button>
  </form>
</body>
</html>
"""

@app.route('/', methods=['GET','POST'])
def edit_banner():
    cfg = load_banner_config()
    if request.method == 'POST':
        cfg['mode'] = request.form.get('mode', 'none')
        cfg['text'] = request.form.get('text', '').strip()
        save_banner_config(cfg)
        return redirect(url_for('edit_banner'))
    return render_template_string(
        TEMPLATE,
        mode=cfg['mode'],
        text=cfg['text']
    )

@app.route('/banner.json')
def banner_api():
    """Gibt das ganze JSON zurück, inkl. mode/text."""
    return jsonify(load_banner_config())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5010)
