from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.settings import DropdownSettings
from app.models.dish import Dish
from app.schemas.settings import DropdownAddRequest, DropdownsResponse, VALID_CATEGORIES
from app.auth.auth import get_current_user, require_admin
from app.models.auth import User

router = APIRouter(prefix="/api/v1/settings", tags=["Dropdown Settings"])

# ── Default seed data ─────────────────────────────────────────────────────────
DEFAULT_DATA = {
    "cuisines": [
        "Pakistani", "Chinese", "Italian", "Mexican", "Thai",
        "Japanese", "Middle Eastern", "Fast Food", "Coffee",
        "Continental", "Korean", "Vietnamese", "Turkish"
    ],
    "meal_types": [
        "Appetizer", "Side", "Main Course", "Dessert", "Drink"
    ],
    "textures": [],
    "dietary": [],
    "meal_times": [],
}


def _get_or_create_category(db: Session, category: str) -> DropdownSettings:
    """Category row fetch karo, agar nahi hai toh default se bana do."""
    row = db.query(DropdownSettings).filter(
        DropdownSettings.category == category
    ).first()

    if not row:
        row = DropdownSettings(
            category=category,
            values=DEFAULT_DATA.get(category, [])
        )
        db.add(row)
        db.commit()
        db.refresh(row)

    return row


def _seed_all(db: Session):
    """Pehli call pe saari categories ensure karo."""
    for cat in VALID_CATEGORIES:
        _get_or_create_category(db, cat)


# ── GET /api/v1/settings/dropdowns ───────────────────────────────────────────
@router.get("/dropdowns", response_model=DropdownsResponse)
def get_all_dropdowns(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Saare dropdown options ek saath return karo."""
    _seed_all(db)

    result = {}
    rows = db.query(DropdownSettings).all()
    for row in rows:
        result[row.category] = row.values or []

    # Ensure sab keys present hain
    for cat in VALID_CATEGORIES:
        if cat not in result:
            result[cat] = []

    return DropdownsResponse(**result)


# ── POST /api/v1/settings/dropdowns ──────────────────────────────────────────
@router.post("/dropdowns", status_code=201)
def add_dropdown_option(
    payload: DropdownAddRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Kisi bhi category mein naya option add karo.
    Body: { "category": "cuisines", "value": "Afghan" }
    """
    row = _get_or_create_category(db, payload.category)

    current_values: list = list(row.values or [])

    # Duplicate check (case-insensitive)
    if any(v.lower() == payload.value.lower() for v in current_values):
        raise HTTPException(
            status_code=409,
            detail=f"'{payload.value}' already exists in '{payload.category}'"
        )

    current_values.append(payload.value)
    row.values = current_values
    db.commit()

    return {
        "message": f"'{payload.value}' successfully '{payload.category}' mein add ho gaya",
        "category": payload.category,
        "values": current_values
    }


# ── DELETE /api/v1/settings/dropdowns?category=cuisines&value=Italian ────────
@router.delete("/dropdowns", status_code=200)
def delete_dropdown_option(
    category: str = Query(..., description="Category name, e.g. cuisines"),
    value: str = Query(..., description="Delete karne wali value, e.g. Italian"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Category se value remove karo.
    - Agar category 'cuisines' hai → sab dishes ki cuisine field bhi NULL ho jayegi.
    - Agar category 'meal_types' hai → sab dishes ki meal_type field bhi NULL ho jayegi.
    """
    # Validate category
    if category not in VALID_CATEGORIES:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid category '{category}'. Allowed: {sorted(VALID_CATEGORIES)}"
        )

    value = value.strip()
    if not value:
        raise HTTPException(status_code=422, detail="Value empty nahi ho sakti")

    row = _get_or_create_category(db, category)
    current_values: list = list(row.values or [])

    # Find exact match (case-insensitive)
    matched = next((v for v in current_values if v.lower() == value.lower()), None)
    if not matched:
        raise HTTPException(
            status_code=404,
            detail=f"'{value}' nahi mila '{category}' mein"
        )

    # Settings se remove karo
    current_values.remove(matched)
    row.values = current_values
    db.commit()

    dishes_updated = 0

    # ── Cascade: dishes mein bhi clear karo ──────────────────────────────────
    if category == "cuisines":
        dishes = db.query(Dish).filter(Dish.cuisine == matched).all()
        for dish in dishes:
            dish.cuisine = None
        db.commit()
        dishes_updated = len(dishes)

    elif category == "meal_types":
        dishes = db.query(Dish).filter(Dish.meal_type == matched).all()
        for dish in dishes:
            dish.meal_type = None
        db.commit()
        dishes_updated = len(dishes)

    return {
        "message": f"'{matched}' successfully '{category}' se remove ho gaya",
        "category": category,
        "values": current_values,
        "dishes_updated": dishes_updated
    }
