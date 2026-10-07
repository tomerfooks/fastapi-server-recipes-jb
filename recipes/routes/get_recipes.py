from fastapi import APIRouter

from recipes.db import db, to_dict

router = APIRouter()

@router.get("/recipes")
def get_recipes():
    conn = db()
    try:
        return [to_dict(r) for r in conn.execute("SELECT * FROM recipes")]
    finally:
        conn.close()
