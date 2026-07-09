"""
Public API endpoints for user-side consumption.
No authentication required. Sensitive fields are excluded.
"""
import os
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.restaurant import Restaurant
from app.models.dish import Dish
from app.models.ai_pick import AIPickPreferences

router = APIRouter(prefix="/public", tags=["Public"])


def _get_public_base_url(request: Request) -> str:
    """Return the public base URL used for generating media links."""
    configured = os.getenv("PUBLIC_BASE_URL", "").strip()
    if configured:
        return configured.rstrip("/")

    forwarded_proto = request.headers.get("x-forwarded-proto", "")
    forwarded_host = request.headers.get("x-forwarded-host", "")
    if forwarded_host:
        proto = forwarded_proto.split(",")[0].strip() or request.url.scheme
        host = forwarded_host.split(",")[0].strip()
        return f"{proto}://{host}".rstrip("/")

    return str(request.base_url).rstrip("/")


def _build_image_url(request: Request, path: Optional[str]) -> Optional[str]:
    """Convert relative image path to an absolute URL."""
    if not path:
        return None

    # If already an absolute URL, return as-is
    if path.startswith("http://") or path.startswith("https://"):
        return path

    base_url = _get_public_base_url(request)
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


# ── AI Survey Config — Public ────────────────────────────────────────────────

# Static allergies list — no DB needed, fixed set of common food allergies
STATIC_ALLERGIES = [
    {"id": "nuts",       "name": "Nuts",       "identifier": "nuts"},
    {"id": "wheat",      "name": "Wheat",      "identifier": "wheat"},
    {"id": "dairy",      "name": "Dairy",      "identifier": "dairy"},
    {"id": "eggs",       "name": "Eggs",       "identifier": "eggs"},
    {"id": "fish",       "name": "Fish",       "identifier": "fish"},
    {"id": "shellfish",  "name": "Shellfish",  "identifier": "shellfish"},
    {"id": "soy",        "name": "Soy",        "identifier": "soy"},
    {"id": "gluten",     "name": "Gluten",     "identifier": "gluten"},
]


@router.get("/ai-survey-config")
def get_ai_survey_config(db: Session = Depends(get_db)):
    """
    Public endpoint — no authentication required.

    Returns the AI onboarding survey configuration:
    - cuisines: Admin ne jo cuisines allow ki hain (from ai_pick_preferences)
    - spice_levels: Available spice options
    - allergies: Static list of common food allergies
    - budget: Min/max budget range
    - flags: suggest_new_cuisines, prioritize_healthy, consider_dietary_restrictions

    Frontend is API ko call kare aur user ko wohi survey dikhaye
    jo Admin ne configure kiya hai.
    """
    # Load admin preferences from DB (id=1, always single row)
    prefs = db.query(AIPickPreferences).filter(AIPickPreferences.id == 1).first()

    # Default values agar admin ne abhi config nahi ki
    if not prefs:
        cuisines = ["Pakistani", "Chinese", "Italian", "Mexican", "Thai", "Fast Food"]
        spice_levels = ["Mild", "Medium", "Spicy", "Extra Spicy"]
        budget_min = 0
        budget_max = 50
        suggest_new_cuisines = True
        prioritize_healthy = False
        consider_dietary_restrictions = False
    else:
        cuisines = prefs.cuisines or []
        # Extract spice level names from spicy_levels JSON
        spice_levels = [
            s["name"] for s in (prefs.spicy_levels or [])
            if isinstance(s, dict) and s.get("name")
        ]
        if not spice_levels:
            spice_levels = ["Mild", "Medium", "Spicy", "Extra Spicy"]
        budget_min = prefs.budget_min or 0
        budget_max = prefs.budget_max or 50
        suggest_new_cuisines = prefs.suggest_new_cuisines
        prioritize_healthy = prefs.prioritize_healthy
        consider_dietary_restrictions = prefs.consider_dietary_restrictions

    return {
        "cuisines": cuisines,
        "spice_levels": spice_levels,
        "allergies": STATIC_ALLERGIES,
        "budget": {
            "min": budget_min,
            "max": budget_max,
        },
        "suggest_new_cuisines": suggest_new_cuisines,
        "prioritize_healthy": prioritize_healthy,
        "consider_dietary_restrictions": consider_dietary_restrictions,
    }
