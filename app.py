from flask import Flask, request, render_template, redirect, url_for, send_file
import os
from werkzeug.utils import secure_filename
from bot_logic import run_bot

app = Flask(__name__)

# Zugriffskontrolle
app.config['TOKEN'] = os.getenv('ACCESS_TOKEN', '')
app.config['PASSWORD'] = os.getenv('ACCESS_PASSWORD', '')
app.config['UPLOAD_FOLDER'] = 'uploads'

AUTHORIZED = set()

@app.route('/')
def home():
    key = request.args.get('key', '')
    if key == app.config['TOKEN']:
        return redirect(url_for('login', key=key))
    return "⛔ Kein gültiger Zugriffstoken.", 403

@app.route('/login', methods=['GET', 'POST'])
def login():
    key = request.args.get('key', '')
    if request.method == 'POST':
        password = request.form.get('password', '')
        if password == app.config['PASSWORD']:
            AUTHORIZED.add(key)
            return redirect(url_for('formular', key=key))
        return "⛔ Falsches Passwort", 403
    return render_template("login.html", key=key)

@app.route('/form', methods=['GET', 'POST'])
def formular():
    key = request.args.get('key', '')
    if key not in AUTHORIZED:
        return "⛔ Nicht autorisiert", 403

    if request.method == 'POST':
        artikel_raw = request.form.get('artikelnummern', '')
        try:
            artikelnummern = [zeile.strip() for zeile in artikel_raw.splitlines() if zeile.strip()]
            if not artikelnummern:
                return "⚠️ Keine Artikelnummern eingegeben."

            output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'result.xlsx')
            run_bot(artikelnummern, output_path)
            return render_template("index.html", download_link="/download")
        except Exception as e:
            return f"❌ Fehler bei der Verarbeitung: {e}"
    return render_template("index.html")

@app.route('/download')
def download():
    pfad = os.path.join(app.config['UPLOAD_FOLDER'], 'result.xlsx')
    return send_file(pfad, as_attachment=True)

@app.route('/logout')
def logout():
    key = request.args.get('key', '')
    AUTHORIZED.discard(key)
    return redirect('/')
