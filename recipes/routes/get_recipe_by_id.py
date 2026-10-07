from fastapi import APIRouter, HTTPException

from recipes.db import db, to_dict

router = APIRouter()


@router.get("/recipes/{recipe_id}")
def get_recipe_by_id(recipe_id: int):
    conn = db()
    try:
        row = conn.execute("SELECT * FROM recipes WHERE id = ?", (recipe_id,)).fetchone()
        if row is None:
            raise HTTPException(404, "Recipe not found")
        return to_dict(row)
    finally:
        conn.close()
