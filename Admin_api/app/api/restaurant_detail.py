# ⚠️ WARNING: This file is NOT included in main.py and is currently UNUSED.
# Restaurant detail (GET /{id}) functionality exists in restaurant_add.py.
# Do NOT modify this file expecting changes to take effect.

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.restaurant import Restaurant
from app.schemas.restaurant import RestaurantResponse
from app.database.database import SessionLocal

router = APIRouter(prefix="/restaurants", tags=["Restaurant Detail"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# GET Single Restaurant
@router.get("/{id}", response_model=RestaurantResponse)
def restaurant_detail(id: int, db: Session = Depends(get_db)):
    restaurant = db.query(Restaurant).filter(Restaurant.id == id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return restaurant