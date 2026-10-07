from typing import Literal

from pydantic import BaseModel, Field

class Recipe(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    cook_time_minutes: int | None = Field(default=None, ge=0)
    servings: int | None = Field(default=None, ge=1)
    difficulty: Literal["Easy", "Medium", "Hard"] | None = None
    calories_per_serving: int | None = Field(default=None, ge=0)
    user_id: int | None = Field(default=None, ge=1)
    ingredients: list[str] = []
    instructions: list[str] = []