from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON
from app.database.database import Base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class Dish(Base):
    __tablename__ = "dishes"
 
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    category = Column(String(100))
    selling_price = Column(Float, default=0.0)
    cost_price = Column(Float, default=0.0)
    discounted_price = Column(Float, nullable=True)
    quantity = Column(Integer, default=0)
    delivery = Column(Boolean, default=False)
    add_discount = Column(Boolean, default=False)
    return_policy = Column(Boolean, default=False)
    short_description = Column(Text, nullable=True)
    long_description = Column(Text, nullable=True)
    cover_image = Column(String(500), nullable=True)
    additional_images = Column(JSON, default=list)
    status = Column(String(20), default="draft")  
    expiry_date = Column(DateTime, nullable=True)
    date_added = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
 
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=True)
    restaurant = relationship("Restaurant", back_populates="dishes")
