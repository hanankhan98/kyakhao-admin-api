from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.models.restaurant import Restaurant
from app.schemas.restaurant import RestaurantCreate, RestaurantResponse, RestaurantUpdate
from app.database.database import SessionLocal
import os, shutil, uuid

router = APIRouter(prefix="/restaurants", tags=["Restaurants"])

MEDIA_DIR = "media/restaurants"
os.makedirs(MEDIA_DIR, exist_ok=True)

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


# GET ALL
@router.get("/", response_model=list[RestaurantResponse])
def get_restaurants(db: Session = Depends(get_db)):
    return db.query(Restaurant).all()


# GET SINGLE
@router.get("/{id}", response_model=RestaurantResponse)
def get_restaurant(id: int, db: Session = Depends(get_db)):
    restaurant = db.query(Restaurant).filter(Restaurant.id == id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return restaurant


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

# ── Logo Upload ──────────────────────────────────────────────────────────────
@router.post("/{id}/logo", response_model=RestaurantResponse)
def upload_logo(
    id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    restaurant = db.query(Restaurant).filter(Restaurant.id == id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    allowed = {"image/jpeg", "image/png", "image/jpg"}
    if file.content_type not in allowed:
        raise HTTPException(status_code=400, detail="Sirf JPG aur PNG allowed hain")

    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(0)
    if size > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File 5MB se bari hai")

    if restaurant.logo and os.path.exists(restaurant.logo):
        os.remove(restaurant.logo)

    ext = file.filename.split(".")[-1]
    filename = f"logo_{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(MEDIA_DIR, filename)

    with open(filepath, "wb") as f:
        shutil.copyfileobj(file.file, f)

    restaurant.logo = filepath
    db.commit()
    # Explicitly re-query to ensure fresh data in response
    restaurant = db.query(Restaurant).filter(Restaurant.id == id).first()
    return restaurant


# ── Banner Upload ────────────────────────────────────────────────────────────
@router.post("/{id}/banner", response_model=RestaurantResponse)
def upload_banner(
    id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    restaurant = db.query(Restaurant).filter(Restaurant.id == id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    allowed = {"image/jpeg", "image/png", "image/jpg"}
    if file.content_type not in allowed:
        raise HTTPException(status_code=400, detail="Sirf JPG aur PNG allowed hain")

    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(0)
    if size > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File 5MB se bari hai")

    if restaurant.banner and os.path.exists(restaurant.banner):
        os.remove(restaurant.banner)

    ext = file.filename.split(".")[-1]
    filename = f"banner_{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(MEDIA_DIR, filename)

    with open(filepath, "wb") as f:
        shutil.copyfileobj(file.file, f)

    restaurant.banner = filepath
    db.commit()
    # Explicitly re-query to ensure fresh data in response
    restaurant = db.query(Restaurant).filter(Restaurant.id == id).first()
    return restaurant
