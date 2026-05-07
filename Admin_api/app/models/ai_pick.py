from sqlalchemy import Column, Integer, String, Boolean, JSON
from app.database.database import Base


class AIPickPreferences(Base):
    __tablename__ = "ai_pick_preferences"

    id = Column(Integer, primary_key=True, index=True)

    spicy_levels = Column(JSON, default=list)
    meal_times = Column(JSON, default=list)
    cuisines = Column(JSON, default=list)
    spice_preference = Column(String(20), default="spicy")
    portion_sizes = Column(JSON, default=list)
    budget_min = Column(Integer, default=0)
    budget_max = Column(Integer, default=50)
    suggest_new_cuisines = Column(Boolean, default=True)
    prioritize_healthy = Column(Boolean, default=True)
    consider_dietary_restrictions = Column(Boolean, default=False)
    seasonal_ingredient_focus = Column(Boolean, default=False)
