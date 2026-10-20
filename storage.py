import sqlite3
import json
from pathlib import Path

DB_PATH = Path(__file__).parent / "portal.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def initialize_db():
    with get_connection() as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS saved_searches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                provider TEXT NOT NULL,
                query TEXT NOT NULL,
                results_json TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)


def save_search(provider, query, results):
    with get_connection() as con:
        con.execute(
            """
            INSERT INTO saved_searches
                (provider, query, results_json)
            VALUES (?, ?, ?)
            """,
            (provider, query, json.dumps(results)),
        )


def get_saved_searches():
    with get_connection() as con:
        rows = con.execute("""
            SELECT id, provider, query, created_at
            FROM saved_searches
            ORDER BY id DESC
        """).fetchall()

    return [
        {
            "id": row[0],
            "provider": row[1],
            "query": row[2],
            "created_at": row[3],
        }
        for row in rows
    ]


def load_search(search_id):
    with get_connection() as con:
        row = con.execute(
            """
            SELECT results_json
            FROM saved_searches
            WHERE id = ?
            """,
            (search_id,),
        ).fetchone()

    return json.loads(row[0]) if row else []


def delete_search(search_id):
    with get_connection() as con:
        con.execute(
            "DELETE FROM saved_searches WHERE id = ?",
            (search_id,),
        )
