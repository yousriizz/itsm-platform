import os

import psycopg
from flask import Flask, jsonify, request

app = Flask(__name__)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://itsm:itsm_dev_only@127.0.0.1:5433/itsm",
)

def connect():
    return psycopg.connect(DATABASE_URL)

def init_db():
    with connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                title TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'ouvert'
            )
        """)

@app.post("/tickets")
def create_ticket():
    data = request.get_json(silent=True) or {}
    title = data.get("title")
    if not isinstance(title, str) or not title.strip():
        return jsonify({"error": "Titre requis"}), 400

    with connect() as conn:
        row = conn.execute(
            "INSERT INTO tickets (title) VALUES (%s) RETURNING id, title, status",
            (title.strip(),),
        ).fetchone()
    return jsonify(dict(zip(("id", "title", "status"), row))), 201

@app.get("/tickets")
def list_tickets():
    with connect() as conn:
        rows = conn.execute(
            "SELECT id, title, status FROM tickets ORDER BY id"
        ).fetchall()
    return jsonify([
        dict(zip(("id", "title", "status"), row)) for row in rows
    ])

@app.patch("/tickets/<int:ticket_id>")
def update_ticket(ticket_id):
    data = request.get_json(silent=True) or {}
    status = data.get("status")
    if status not in ("ouvert", "en cours", "résolu"):
        return jsonify({"error": "Statut invalide"}), 400

    with connect() as conn:
        row = conn.execute(
            "UPDATE tickets SET status = %s WHERE id = %s RETURNING id, title, status",
            (status, ticket_id),
        ).fetchone()
    if row is None:
        return jsonify({"error": "Ticket introuvable"}), 404
    return jsonify(dict(zip(("id", "title", "status"), row)))

if __name__ == "__main__":
    init_db()
    app.run()
