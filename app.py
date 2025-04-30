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

# Sicherstellen, dass der Upload-Ordner existiert
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

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
        artikel_raw = request.form.get('artikelnummern')
        print("[DEBUG] Rohdaten aus Textfeld:", artikel_raw)

        if not artikel_raw:
            return "⚠️ Keine Artikelnummern übermittelt."

        try:
            artikelnummern = [zeile.strip() for zeile in artikel_raw.splitlines() if zeile.strip()]
            print("[DEBUG] Verarbeitete Artikelnummern:", artikelnummern)

            if not artikelnummern:
                return "⚠️ Keine gültigen Artikelnummern eingegeben."

            output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'result.xlsx')
            print("[DEBUG] Schreibe nach:", output_path)

            run_bot(artikelnummern, output_path)

            if not os.path.exists(output_path):
                return "❌ Datei wurde nicht erstellt."

            return render_template("index.html", download_link="/download", key=key)

        except Exception as e:
            return f"❌ Fehler bei der Verarbeitung: {e}"

    return render_template("index.html", key=key)

@app.route('/download')
def download():
    pfad = os.path.join(app.config['UPLOAD_FOLDER'], 'result.xlsx')
    if not os.path.exists(pfad):
        return "❌ Datei nicht gefunden.", 404
    return send_file(pfad, as_attachment=True)

@app.route('/logout')
def logout():
    key = request.args.get('key', '')
    AUTHORIZED.discard(key)
    return redirect('/')
