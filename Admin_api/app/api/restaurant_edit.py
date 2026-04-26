from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.restaurant import Restaurant
from app.schemas.restaurant import RestaurantUpdate, RestaurantResponse
from app.database.database import SessionLocal

router = APIRouter(prefix="/restaurants", tags=["Restaurant Edit"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# UPDATE Restaurant
@router.put("/{id}", response_model=RestaurantResponse)
def update_restaurant(id: int, data: RestaurantUpdate, db: Session = Depends(get_db)):
    restaurant = db.query(Restaurant).filter(Restaurant.id == id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(restaurant, key, value)
    db.commit()
    db.refresh(restaurant)
    return restaurant

# DELETE Restaurant
@router.delete("/{id}")
def delete_restaurant(id: int, db: Session = Depends(get_db)):
    restaurant = db.query(Restaurant).filter(Restaurant.id == id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    db.delete(restaurant)
    db.commit()
    return {"message": "Restaurant deleted successfully"}