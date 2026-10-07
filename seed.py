"""Build a 2-table SQLite DB (users, recipes) from dummyjson and load all the data.

Lists that used to be child tables (ingredients, instructions, tags, meal types)
are stored as JSON arrays in TEXT columns.
"""

import json
import sqlite3
import urllib.request
from pathlib import Path

DB_PATH = Path(__file__).parent / "dummyjson.db"
API = "https://dummyjson.com"

SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id          INTEGER PRIMARY KEY,
    first_name  TEXT NOT NULL,
    last_name   TEXT NOT NULL,
    age         INTEGER,
    gender      TEXT,
    email       TEXT NOT NULL UNIQUE,
    username    TEXT NOT NULL UNIQUE,
    role        TEXT,
    city        TEXT,
    country     TEXT
);

CREATE TABLE IF NOT EXISTS recipes (
    id                      INTEGER PRIMARY KEY,
    name                    TEXT NOT NULL,
    prep_time_minutes       INTEGER,
    cook_time_minutes       INTEGER,
    servings                INTEGER,
    difficulty              TEXT,
    cuisine                 TEXT,
    calories_per_serving    INTEGER,
    image                   TEXT,
    rating                  REAL,
    review_count            INTEGER,
    user_id                 INTEGER REFERENCES users(id),
    ingredients             TEXT NOT NULL DEFAULT '[]',  -- JSON array of strings
    instructions            TEXT NOT NULL DEFAULT '[]',  -- JSON array of strings
    tags                    TEXT NOT NULL DEFAULT '[]',  -- JSON array of strings
    meal_types              TEXT NOT NULL DEFAULT '[]'   -- JSON array of strings
);

CREATE INDEX IF NOT EXISTS idx_recipes_user ON recipes(user_id);
"""

USER_COLS = ["id", "first_name", "last_name", "age", "gender", "email",
             "username", "role", "city", "country"]
RECIPE_COLS = ["id", "name", "prep_time_minutes", "cook_time_minutes", "servings",
               "difficulty", "cuisine", "calories_per_serving", "image", "rating",
               "review_count", "user_id", "ingredients", "instructions", "tags",
               "meal_types"]


def fetch_all(resource):
    """Page through /<resource> and return every item."""
    items, skip = [], 0
    while True:
        url = f"{API}/{resource}?limit=100&skip={skip}"
        # dummyjson rejects the default urllib user-agent with a 403.
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            page = json.load(resp)
        items.extend(page[resource])
        skip += 100
        if skip >= page["total"]:
            return items


def user_row(u):
    addr = u.get("address") or {}
    return (
        u["id"], u["firstName"], u["lastName"], u.get("age"), u.get("gender"),
        u["email"], u["username"], u.get("role"), addr.get("city"), addr.get("country"),
    )


def recipe_row(r):
    return (
        r["id"], r["name"], r.get("prepTimeMinutes"), r.get("cookTimeMinutes"),
        r.get("servings"), r.get("difficulty"), r.get("cuisine"),
        r.get("caloriesPerServing"), r.get("image"), r.get("rating"),
        r.get("reviewCount"), r.get("userId"),
        json.dumps(r.get("ingredients") or []),
        json.dumps(r.get("instructions") or []),
        json.dumps(r.get("tags") or []),
        json.dumps(r.get("mealType") or []),
    )


def load(db_path=DB_PATH):
    users = fetch_all("users")
    recipes = fetch_all("recipes")

    # Recipes may reference a userId the API never returns; keep the FK satisfiable.
    known = {u["id"] for u in users}
    for r in recipes:
        if r.get("userId") not in known:
            r["userId"] = None

    conn = sqlite3.connect(db_path)
    conn.executescript(SCHEMA)
    with conn:
        conn.executemany(
            f"INSERT OR REPLACE INTO users ({','.join(USER_COLS)}) "
            f"VALUES ({','.join('?' * len(USER_COLS))})",
            [user_row(u) for u in users],
        )
        conn.executemany(
            f"INSERT OR REPLACE INTO recipes ({','.join(RECIPE_COLS)}) "
            f"VALUES ({','.join('?' * len(RECIPE_COLS))})",
            [recipe_row(r) for r in recipes],
        )
    conn.close()
    return len(users), len(recipes)


def demo():
    n_users, n_recipes = load()
    conn = sqlite3.connect(DB_PATH)
    count = lambda t: conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
    assert count("users") == n_users, count("users")
    assert count("recipes") == n_recipes, count("recipes")
    # Exactly two tables.
    tables = [r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")]
    assert sorted(tables) == ["recipes", "users"], tables
    # JSON columns round-trip to real lists.
    ing, ins = conn.execute("SELECT ingredients, instructions FROM recipes WHERE id=1").fetchone()
    assert isinstance(json.loads(ing), list) and json.loads(ing), ing
    assert isinstance(json.loads(ins), list) and json.loads(ins), ins
    # Join across the FK works.
    joined = conn.execute(
        "SELECT COUNT(*) FROM recipes r JOIN users u ON u.id = r.user_id").fetchone()[0]
    assert joined > 0, joined
    print(f"{DB_PATH}: {n_users} users, {n_recipes} recipes, "
          f"{joined} recipes joined to a user, tables={sorted(tables)}")
    conn.close()


if __name__ == "__main__":
    demo()
