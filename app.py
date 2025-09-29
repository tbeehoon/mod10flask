from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from pathlib import Path

app = Flask(__name__)
app.secret_key = "change-me-in-production"  # needed for sessions & flash

DB_PATH = Path("database.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def home():
    # dynamic data passed to Jinja2
    return render_template("index.html", user=session.get("user", "Guest"))

@app.route("/set-user", methods=["POST"])
def set_user():
    session["user"] = request.form.get("username") or "Guest"
    flash("User saved in session.")
    return redirect(url_for("home"))

