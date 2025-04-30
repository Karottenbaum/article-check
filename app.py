from flask import Flask, render_template, request, redirect, url_for, session, send_file
import os
from dotenv import load_dotenv
from bot_logic import run_bot
from datetime import datetime

app = Flask(__name__)
app.secret_key = "mein-super-geheimer-sessionkey-2025"

# Session-Cookie-Konfiguration
app.config["SESSION_COOKIE_SECURE"] = False
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

# Tokens & Passwort laden
load_dotenv("Passwort.env")
ACCESS_TOKENS = os.getenv("ACCESS_TOKENS", "")
VALID_TOKENS = [token.strip() for token in ACCESS_TOKENS.split(",") if token.strip()]
ACCESS_PASSWORD = os.getenv("ACCESS_PASSWORD", "")

@app.route("/", methods=["GET", "POST"])
def login():
    token = request.args.get("key", "")
    if token not in VALID_TOKENS:
        return render_template("login.html", error="❌ Ungültiger oder fehlender Token.")

    if request.method == "POST":
        entered_password = request.form.get("password", "")
        if entered_password == ACCESS_PASSWORD:
            session["authenticated"] = True
            return redirect(url_for("form"))
        else:
            return render_template("login.html", error="❌ Falsches Passwort.")

    return render_template("login.html")

@app.route("/form", methods=["GET", "POST"])
def form():
    if not session.get("authenticated"):
        return redirect(url_for("login"))

    download_link = None
    if request.method == "POST":
        artikel_text = request.form["artikelnummern"]
        artikelnummern = [line.strip() for line in artikel_text.strip().split("\n") if line.strip()]
        if artikelnummern:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"uploads/result_{timestamp}.xlsx"
            run_bot(artikelnummern, filename)
            download_link = f"/download/{os.path.basename(filename)}"
    return render_template("index.html", download_link=download_link)

@app.route("/download/<filename>")
def download(filename):
    if not session.get("authenticated"):
        return redirect(url_for("login"))
    return send_file(f"uploads/{filename}", as_attachment=True)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    os.makedirs("uploads", exist_ok=True)
    print("🔐 Webportal mit Token + Passwortschutz läuft auf http://127.0.0.1:5000/?key=abc123")
    app.run(debug=True)
