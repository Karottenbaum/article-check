from flask import Flask, request, redirect, render_template, session, url_for
import os

app = Flask(__name__)
app.secret_key = os.getenv("SESSION_SECRET", "fallback-secret")  # sicherheitshalber

app.config['TOKEN'] = os.getenv("ACCESS_TOKEN")
app.config['PASSWORD'] = os.getenv("ACCESS_PASSWORD")

@app.route('/')
def entry():
    token = request.args.get("key")
    if token == app.config['TOKEN']:
        session['authenticated'] = True
        return redirect('/login')
    return "Access denied", 403

@app.route('/login', methods=["GET", "POST"])
def login():
    if not session.get('authenticated'):
        return redirect('/')
    if request.method == "POST":
        pw = request.form.get("password")
        if pw == app.config['PASSWORD']:
            session['logged_in'] = True
            return redirect('/index')
        else:
            return render_template("login.html", error="Falsches Passwort")
    return render_template("login.html")

@app.route('/index')
def index():
    if not session.get('logged_in'):
        return redirect('/login')
    return render_template("index.html")
