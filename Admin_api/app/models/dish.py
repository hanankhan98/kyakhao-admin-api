from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON
from app.database.database import Base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class Dish(Base):
    __tablename__ = "dishes"
 
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    cuisine = Column(String(100), nullable=True)
    price = Column(Float, default=0.0)
    meal_type = Column(String(100), nullable=True)
    meal_time = Column(String(100), nullable=True)
    texture = Column(String(100), nullable=True)
    dietary_type = Column(String(100), nullable=True)
    calories = Column(Integer, nullable=True)
    spicy = Column(Boolean, default=False)
    long_description = Column(Text, nullable=True)
    cover_image = Column(String(500), nullable=True)
    additional_images = Column(JSON, default=lambda: [])
    status = Column(String(20), default="draft")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
 
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=True)
    restaurant = relationship("Restaurant", back_populates="dishes")
