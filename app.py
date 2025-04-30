from flask import Flask, request, render_template, redirect, url_for, send_file
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['TOKEN'] = os.getenv("ACCESS_TOKEN")
app.config['PASSWORD'] = os.getenv("ACCESS_PASSWORD")

# Zwischenspeicher für gültige Sessions
authorized_sessions = set()

@app.route("/", methods=["GET"])
def token_check():
    token = request.args.get("key")
    if token and token == app.config['TOKEN']:
        session_id = request.remote_addr
        authorized_sessions.add(session_id)
        return redirect(url_for("login"))
    return "Unauthorized", 403

@app.route("/login", methods=["GET", "POST"])
def login():
    session_id = request.remote_addr
    if session_id not in authorized_sessions:
        return "Unauthorized", 403

    if request.method == "POST":
        password = request.form.get("password")
        if password == app.config['PASSWORD']:
            return redirect(url_for("index"))
        return render_template("login.html", error="Falsches Passwort")
    
    return render_template("login.html")

@app.route("/index", methods=["GET"])
def index():
    session_id = request.remote_addr
    if session_id not in authorized_sessions:
        return redirect(url_for("login"))
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
