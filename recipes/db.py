import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "dummyjson.db"

# Columns stored as JSON arrays of strings (see seed.py).
JSON_COLS = ("ingredients", "instructions", "tags", "meal_types")


def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def to_dict(row):
    """sqlite Row -> dict, with the JSON columns decoded back into lists."""
    d = dict(row)
    for c in JSON_COLS:
        if c in d:
            d[c] = json.loads(d[c])
    return d
