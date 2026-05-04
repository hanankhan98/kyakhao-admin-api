# ⚠️ WARNING: This file is NOT included in main.py and is currently UNUSED.
# All restaurant list/create functionality exists in restaurant_add.py.
# Do NOT modify this file expecting changes to take effect.

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.restaurant import Restaurant
from app.schemas.restaurant import RestaurantCreate, RestaurantResponse, RestaurantUpdate
from app.database.database import SessionLocal

router = APIRouter(prefix="/restaurants", tags=["Restaurants List"])

# DB Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# CREATE Restaurant
@router.post("/", response_model=RestaurantResponse)
def create_restaurant(data: RestaurantCreate, db: Session = Depends(get_db)):
    restaurant = Restaurant(**data.model_dump())
    db.add(restaurant)
    db.commit()
    db.refresh(restaurant)
    return restaurant

# LIST ALL Restaurants
@router.get("/", response_model=list[RestaurantResponse])
def list_restaurants(db: Session = Depends(get_db)):
    return db.query(Restaurant).all()