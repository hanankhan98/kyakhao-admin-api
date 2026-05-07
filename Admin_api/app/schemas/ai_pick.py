from pydantic import BaseModel, ConfigDict
from typing import Optional


class SpicyLevelItem(BaseModel):
    name: str
    order: int


class MealTimeItem(BaseModel):
    name: str
    start: str
    end: str
    enabled: bool


class AIPickPreferencesBase(BaseModel):
    spicy_levels: Optional[list[SpicyLevelItem]] = None
    meal_times: Optional[list[MealTimeItem]] = None
    cuisines: Optional[list[str]] = None
    spice_preference: Optional[str] = None
    portion_sizes: Optional[list[str]] = None
    budget_min: Optional[int] = None
    budget_max: Optional[int] = None
    suggest_new_cuisines: Optional[bool] = None
    prioritize_healthy: Optional[bool] = None
    consider_dietary_restrictions: Optional[bool] = None
    seasonal_ingredient_focus: Optional[bool] = None


class AIPickPreferencesUpdate(AIPickPreferencesBase):
    pass


class AIPickPreferencesResponse(BaseModel):
    id: int
    spicy_levels: list
    meal_times: list
    cuisines: list
    spice_preference: str
    portion_sizes: list
    budget_min: int
    budget_max: int
    suggest_new_cuisines: bool
    prioritize_healthy: bool
    consider_dietary_restrictions: bool
    seasonal_ingredient_focus: bool

    model_config = ConfigDict(from_attributes=True)
