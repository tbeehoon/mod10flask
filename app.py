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

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out.")
    return redirect(url_for("home"))

def init_db():
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )
        """)

# Initialize database when app starts
init_db()

@app.route("/items")
def list_items():
    with get_db() as db:
        items = db.execute("SELECT id, name FROM items ORDER BY id DESC").fetchall()
    return render_template("items.html", items=items)

@app.route("/items", methods=["POST"])
def create_item():
    name = (request.form.get("name") or "").strip()
    if name:
        with get_db() as db:
            db.execute("INSERT INTO items (name) VALUES (?)", (name,))
        flash("Item created.")
    return redirect(url_for("list_items"))

@app.route("/items/<int:item_id>/edit")
def edit_item(item_id):
    with get_db() as db:
        item = db.execute("SELECT id, name FROM items WHERE id=?", (item_id,)).fetchone()
    if not item:
        flash("Item not found.")
        return redirect(url_for("list_items"))
    return render_template("edit.html", item=item)

@app.route("/items/<int:item_id>/edit", methods=["POST"])
def update_item(item_id):
    name = (request.form.get("name") or "").strip()
    if name:
        with get_db() as db:
            db.execute("UPDATE items SET name=? WHERE id=?", (name, item_id))
        flash("Item updated.")
    else:
        flash("Name cannot be empty.")
    return redirect(url_for("list_items"))

@app.route("/items/<int:item_id>/delete", methods=["POST"])
def delete_item(item_id):
    with get_db() as db:
        db.execute("DELETE FROM items WHERE id=?", (item_id,))
    flash("Item deleted.")
    return redirect(url_for("list_items"))


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)