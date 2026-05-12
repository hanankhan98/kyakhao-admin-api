"""
Public API endpoints for user-side consumption.
No authentication required. Sensitive fields are excluded.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.restaurant import Restaurant
from app.models.dish import Dish

router = APIRouter(prefix="/public", tags=["Public"])


def _build_image_url(request: Request, path: Optional[str]) -> Optional[str]:
    """Convert relative image path to absolute URL."""
    if not path:
        return None
    # If already an absolute URL, return as-is
    if path.startswith("http://") or path.startswith("https://"):
        return path
    base_url = str(request.base_url).rstrip("/")
    return f"{base_url}/{path.lstrip('/')}"


def _restaurant_to_public(restaurant: Restaurant, request: Request) -> dict:
    """Serialize restaurant with public-safe fields."""
    return {
        "id": restaurant.id,
        "business_name": restaurant.business_name,
        "business_type": restaurant.business_type,
        "address": restaurant.address,
        "city": restaurant.city,
        "country": restaurant.country,
        "zip_code": restaurant.zip_code,
        "description": restaurant.description,
        "logo": _build_image_url(request, restaurant.logo),
        "banner": _build_image_url(request, restaurant.banner),
        "contact_number": restaurant.contact_number,
        "phone_number": restaurant.phone_number,
        "email": restaurant.email,
        "birth_date": restaurant.birth_date,
        "name": restaurant.name,
        "last_name": restaurant.last_name,
        "bank_name": restaurant.bank_name,
        "account_holder_name": restaurant.account_holder_name,
        "account_number": restaurant.account_number,
        "ifsc_code": restaurant.ifsc_code,
    }


def _dish_to_public(dish: Dish, request: Request) -> dict:
    """Serialize dish with public-safe data."""
    return {
        "id": dish.id,
        "name": dish.name,
        "cuisine": dish.cuisine,
        "price": dish.price,
        "meal_type": dish.meal_type,
        "meal_time": dish.meal_time,
        "texture": dish.texture,
        "dietary_type": dish.dietary_type,
        "calories": dish.calories,
        "spicy": dish.spicy,
        "long_description": dish.long_description,
        "cover_image": _build_image_url(request, dish.cover_image),
        "additional_images": [
            _build_image_url(request, img) for img in (dish.additional_images or [])
        ],
        "status": dish.status,
        "updated_at": dish.updated_at.isoformat() if dish.updated_at else None,
        "restaurant_id": dish.restaurant_id,
    }


# ── Public Restaurant Endpoints ──────────────────────────────────────────────

@router.get("/restaurants")
def get_public_restaurants(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    city: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """List all restaurants (public-safe data only)."""
    query = db.query(Restaurant)

    if city:
        query = query.filter(Restaurant.city.ilike(f"%{city}%"))
    if search:
        query = query.filter(Restaurant.business_name.ilike(f"%{search}%"))

    total = query.count()
    restaurants = query.offset(skip).limit(limit).all()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "restaurants": [_restaurant_to_public(r, request) for r in restaurants],
    }


@router.get("/restaurants/{restaurant_id}")
def get_public_restaurant(restaurant_id: int, request: Request, db: Session = Depends(get_db)):
    """Get a single restaurant by ID (public-safe data only)."""
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return _restaurant_to_public(restaurant, request)


@router.get("/restaurants/{restaurant_id}/dishes")
def get_public_restaurant_dishes(
    restaurant_id: int,
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Get all dishes for a specific restaurant."""
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    query = db.query(Dish).filter(Dish.restaurant_id == restaurant_id)
    total = query.count()
    dishes = query.offset(skip).limit(limit).all()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "restaurant_id": restaurant_id,
        "dishes": [_dish_to_public(d, request) for d in dishes],
    }


# ── Public Dish Endpoints ────────────────────────────────────────────────────

@router.get("/dishes")
def get_public_dishes(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    restaurant_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    """List all dishes (public-safe data only)."""
    query = db.query(Dish)

    if search:
        query = query.filter(Dish.name.ilike(f"%{search}%"))
    if restaurant_id:
        query = query.filter(Dish.restaurant_id == restaurant_id)

    total = query.count()
    dishes = query.offset(skip).limit(limit).all()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "dishes": [_dish_to_public(d, request) for d in dishes],
    }


@router.get("/dishes/{dish_id}")
def get_public_dish(dish_id: int, request: Request, db: Session = Depends(get_db)):
    """Get a single dish by ID."""
    dish = db.query(Dish).filter(Dish.id == dish_id).first()
    if not dish:
        raise HTTPException(status_code=404, detail="Dish not found")
    return _dish_to_public(dish, request)
