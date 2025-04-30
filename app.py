from flask import Flask, request, render_template, redirect, url_for, send_file
from werkzeug.utils import secure_filename
import os
from bot_logic import run_bot

app = Flask(__name__)

# Konfiguration
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['TOKEN'] = os.getenv("ACCESS_TOKEN")  # einzelner URL-Token
app.config['PASSWORD'] = os.getenv("ACCESS_PASSWORD")

# Falls ACCESS_TOKENS nicht gesetzt ist, bleibt Liste leer
raw_tokens = os.getenv("ACCESS_TOKENS", "")
VALID_TOKENS = [token.strip() for token in raw_tokens.split(",") if token.strip()]

# Session-Ersatz (sehr einfach)
AUTHORIZED = set()

@app.route('/')
def startseite():
    token = request.args.get('key', '')
    if token in VALID_TOKENS:
        return render_template('login.html', key=token)
    return "⛔ Zugriff verweigert – kein oder ungültiger Token", 403

@app.route('/login', methods=['POST'])
def login():
    password = request.form.get('password', '')
    key = request.args.get('key', '')
    if password == app.config['PASSWORD']:
        AUTHORIZED.add(key)
        return redirect(url_for('formular', key=key))
    return "⛔ Falsches Passwort", 403

@app.route('/form', methods=['GET', 'POST'])
def formular():
    key = request.args.get('key', '')
    if key not in AUTHORIZED:
        return redirect(url_for('startseite'))

    if request.method == 'POST':
        try:
            artikelnummern = request.form.get('artikelnummern', '')
            if not artikelnummern:
                raise ValueError("Keine Artikelnummern übermittelt.")

            artikel_list = [a.strip() for a in artikelnummern.splitlines() if a.strip()]
            if not artikel_list:
                raise ValueError("Artikelnummern leer oder ungültig.")

            filename = run_bot(artikel_list, output_path="result.xlsx")
            return render_template("index.html", download_link="/download/result.xlsx")
        except Exception as e:
            return f"❌ Fehler bei der Verarbeitung: {str(e)}"

    return render_template("index.html")

@app.route('/download/<path:filename>')
def download(filename):
    path = os.path.join("result.xlsx")
    return send_file(path, as_attachment=True)

@app.route('/logout')
def logout():
    key = request.args.get('key', '')
    AUTHORIZED.discard(key)
    return redirect(url_for('startseite'))

if __name__ == '__main__':
    app.run(debug=True)
