from flask import Flask, request, render_template, redirect, url_for, send_file
import os
from bot_logic import run_bot
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['TOKEN'] = os.getenv("ACCESS_TOKEN")
app.config['PASSWORD'] = os.getenv("APP_PASSWORD")

@app.route('/')
def index():
    token = request.args.get('key')
    if token != app.config['TOKEN']:
        return "⛔ Zugriff verweigert", 403
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    token = request.args.get('key')
    if token != app.config['TOKEN']:
        return "⛔ Zugriff verweigert", 403

    error = None
    if request.method == 'POST':
        password = request.form.get('password')
        if password == app.config['PASSWORD']:
            return redirect(url_for('upload', key=token))
        else:
            error = '❌ Falsches Passwort'
    return render_template('login.html', error=error)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    token = request.args.get('key')
    if token != app.config['TOKEN']:
        return "⛔ Zugriff verweigert", 403

    if request.method == 'POST':
        file = request.files.get('file')
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            output_path = run_bot(filepath)

            return send_file(output_path, as_attachment=True)
    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)
