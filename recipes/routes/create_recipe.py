from fastapi import APIRouter

from recipes.db import db, to_dict

router = APIRouter()


@app.post("/recipes", status_code=201)
def create_recipe(recipe: Recipe):
    data = recipe.model_dump()
    for c in ("ingredients", "instructions"):
        data[c] = json.dumps(data[c])
    conn = db()
    try:
        with conn:  # commits on success, rolls back on exception
            cur = conn.execute(
                f"INSERT INTO recipes ({', '.join(data)}) "
                f"VALUES ({', '.join('?' * len(data))})",
                list(data.values()),
            )
    except sqlite3.IntegrityError as e:
        raise HTTPException(400, str(e))
    finally:
        conn.close()
    return {"id": cur.lastrowid, **recipe.model_dump()}
