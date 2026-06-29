from pydantic import BaseModel, field_validator
from typing import Literal

# Valid categories — inke ilawa kuch accept nahi hoga
VALID_CATEGORIES = {"cuisines", "meal_types", "textures", "dietary", "meal_times"}


class DropdownAddRequest(BaseModel):
    category: str
    value: str

    @field_validator("category")
    @classmethod
    def category_must_be_valid(cls, v: str) -> str:
        if v not in VALID_CATEGORIES:
            raise ValueError(
                f"Invalid category '{v}'. "
                f"Allowed: {sorted(VALID_CATEGORIES)}"
            )
        return v

    @field_validator("value")
    @classmethod
    def value_must_not_be_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Value empty nahi ho sakti")
        return v


class DropdownsResponse(BaseModel):
    cuisines: list[str]
    meal_types: list[str]
    textures: list[str]
    dietary: list[str]
    meal_times: list[str]
