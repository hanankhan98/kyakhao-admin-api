from sqlalchemy import Column, Integer, String, JSON
from app.database.database import Base


class DropdownSettings(Base):
    """
    Ek hi table jisme sabhi dropdown options store honge.
    Har row ek category hai (cuisines, meal_types, textures, dietary, meal_times).
    'values' column mein us category ki saari values JSON array mein hain.
    """
    __tablename__ = "dropdown_settings"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(100), unique=True, nullable=False, index=True)
    values = Column(JSON, default=list)
