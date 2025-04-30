from flask import Flask, request, render_template, redirect, url_for, session, send_from_directory
from werkzeug.utils import secure_filename
import os

from bot_logic import run_bot  # deine Artikelsuchfunktion

app = Flask(__name__)
app.secret_key = "eine-geheime-session-key"  # bleibt serverseitig

# Konfiguration
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['TOKEN'] = os.getenv("ACCESS_TOKEN", "")
app.config['PASSWORD'] = os.getenv("ACCESS_PASSWORD", "")

# Route: Start mit Token
@app.route('/')
def index():
    token = request.args.get('key')
    if token == app.config['TOKEN']:
        session['token_verified'] = True
        return redirect(url_for('login'))
    return "⛔ Ungültiger Token", 403

# Route: Login-Formular (Passwort)
@app.route('/login', methods=["GET", "POST"])
def login():
    if not session.get('token_verified'):
        return redirect('/')

    if request.method == "POST":
        pw = request.form.get("password", "")
        if pw == app.config['PASSWORD']:
            session['authenticated'] = True
            return redirect('/form')
        return render_template("login.html", error="❌ Falsches Passwort")

    return render_template("login.html")

# Route: Artikel-Formular
@app.route('/form', methods=["GET", "POST"])
def form():
    if not session.get('authenticated'):
        return redirect('/login')

    if request.method == "POST":
        artikelnummern_raw = request.form['artikelnummern']
        artikelnummern = artikelnummern_raw.strip().splitlines()

        # Preisabfrage starten
        filename = run_bot(artikelnummern)  # z.B. 'resultat.xlsx'
        return render_template("index.html", download_link=f"/downloads/{filename}")

    return render_template("index.html")

# Route: Download-Link
@app.route('/downloads/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

# Route: Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)
