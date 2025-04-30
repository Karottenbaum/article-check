from flask import Flask, request, render_template, redirect, url_for, session, send_file
import os
import io
from werkzeug.utils import secure_filename
from bot_logic import run_bot

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "supersecretkey")

app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['TOKEN'] = os.getenv("ACCESS_TOKEN", "")
app.config['PASSWORD'] = os.getenv("ACCESS_PASSWORD", "")


@app.route("/", methods=["GET"])
def landing_page():
    token = request.args.get("key")
    if token != app.config["TOKEN"]:
        return "❌ Ungültiger Token", 403
    session["token_ok"] = True
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if not session.get("token_ok"):
        return redirect(url_for("landing_page"))

    if request.method == "POST":
        password = request.form.get("password")
        if password == app.config["PASSWORD"]:
            session["logged_in"] = True
            return redirect(url_for("form"))
        return render_template("login.html", error="❌ Falsches Passwort")
    
    return render_template("login.html")


@app.route("/form", methods=["GET", "POST"])
def form():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    if request.method == "POST":
        artikelnummern = request.form.get("artikelnummern")
        if not artikelnummern:
            return "❌ Keine Artikelnummern angegeben", 400

        artikel_liste = artikelnummern.strip().splitlines()
        output_path = os.path.join(app.config["UPLOAD_FOLDER"], "result.xlsx")

        try:
            filename = run_bot(artikel_liste, output_path)
            download_url = url_for("download_file", filename=filename)
            return render_template("index.html", download_link=download_url)
        except Exception as e:
            return f"❌ Fehler bei der Verarbeitung: {e}", 500

    return render_template("index.html")


@app.route("/download/<filename>")
def download_file(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), as_attachment=True)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")
