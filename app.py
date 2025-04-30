from flask import Flask, request, render_template, redirect, url_for, send_file, abort
from werkzeug.utils import secure_filename
from bot_logic import run_bot
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['TOKEN'] = os.getenv("ACCESS_TOKEN")
app.config['PASSWORD'] = os.getenv("ACCESS_PASSWORD")

# Zugangsschutz: Nur mit gültigem Token oder Passwort
@app.before_request
def restrict_access():
    token = request.args.get("key", "")
    password = request.args.get("pw", "")
    valid_token = app.config.get("TOKEN", "")
    valid_password = app.config.get("PASSWORD", "")

    if token != valid_token and password != valid_password:
        abort(403)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files.get("file")
        if not file:
            return "Kein File hochgeladen", 400

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        output_path = run_bot(filepath)
        return send_file(output_path, as_attachment=True)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
