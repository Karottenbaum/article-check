from flask import Flask, request, render_template, redirect, url_for, send_file
from werkzeug.utils import secure_filename
import os
import io
from bot_logic import run_bot

app = Flask(__name__)

# Konfiguration für Upload-Ordner und Zugangsdaten (über Render-Umgebungsvariablen)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['TOKEN'] = os.getenv("ACCESS_TOKEN")
app.config['PASSWORD'] = os.getenv("APP_PASSWORD")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        token = request.form.get("token", "")
        password = request.form.get("password", "")
        file = request.files.get("excel_file")

        if token != app.config['TOKEN'] or password != app.config['PASSWORD']:
            return "Zugriff verweigert", 403

        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            result_path = run_bot(file_path)
            return send_file(result_path, as_attachment=True)

    return render_template("index.html")
