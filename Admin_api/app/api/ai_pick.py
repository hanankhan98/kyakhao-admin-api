from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from app.database.database import get_db
from app.models.ai_pick import AIPickPreferences
from app.models.auth import User
from app.schemas.ai_pick import AIPickPreferencesUpdate, AIPickPreferencesResponse
from app.auth.auth import require_admin

router = APIRouter(prefix="/ai-pick", tags=["AI Pick"])


def _get_or_create_preferences(db: Session) -> AIPickPreferences:
    prefs = db.query(AIPickPreferences).filter(AIPickPreferences.id == 1).first()
    if not prefs:
        prefs = AIPickPreferences(
            id=1,
            spicy_levels=[
                {"name": "Mild", "order": 1},
                {"name": "Medium", "order": 2},
                {"name": "Hot", "order": 3},
                {"name": "Extra Hot", "order": 4},
            ],
            meal_times=[
                {"name": "Breakfast", "start": "07:00", "end": "09:00", "enabled": True},
                {"name": "Lunch", "start": "12:00", "end": "14:00", "enabled": True},
                {"name": "Dinner", "start": "18:00", "end": "20:00", "enabled": True},
                {"name": "Snacks", "start": "", "end": "", "enabled": False},
            ],
            cuisines=["Italian", "Mexican", "Indian"],
            spice_preference="spicy",
            portion_sizes=["Regular (standard serving)"],
            budget_min=10,
            budget_max=50,
            suggest_new_cuisines=True,
            prioritize_healthy=True,
            consider_dietary_restrictions=False,
            seasonal_ingredient_focus=False,
        )
        db.add(prefs)
        db.commit()
        db.refresh(prefs)
    return prefs


@router.get("/preferences", response_model=AIPickPreferencesResponse)
def get_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    prefs = _get_or_create_preferences(db)
    return prefs


@router.put("/preferences", response_model=AIPickPreferencesResponse)
def update_preferences(
    data: AIPickPreferencesUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    prefs = _get_or_create_preferences(db)

    update_fields = data.model_dump(exclude_unset=True)

    for field, value in update_fields.items():
        setattr(prefs, field, value)
        if field in ("spicy_levels", "meal_times", "cuisines", "portion_sizes"):
            flag_modified(prefs, field)

    db.commit()
    db.refresh(prefs)
    return prefs


@router.post("/preferences/reset", response_model=AIPickPreferencesResponse)
def reset_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    prefs = db.query(AIPickPreferences).filter(AIPickPreferences.id == 1).first()
    if prefs:
        db.delete(prefs)
        db.commit()

    prefs = _get_or_create_preferences(db)
    return prefs
