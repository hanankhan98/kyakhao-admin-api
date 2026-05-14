from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, status
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from typing import Optional, Annotated
import os, shutil, uuid

from app.database.database import get_db
from app.models.dish import Dish
from app.models.auth import User 
from app.schemas.dishes import DishCreate, DishUpdate, DishResponse, DishListResponse
from app.auth.auth import get_current_user, require_admin

router = APIRouter(prefix="/dishes", tags=["Dishes"])

MEDIA_DIR = "media/dishes"
os.makedirs(MEDIA_DIR, exist_ok=True)


def _validate_image(file: UploadFile):
    allowed = {"image/jpeg", "image/png", "image/jpg"}
    if file.content_type not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Sirf JPG aur PNG allowed hain. Invalid file: {file.filename}"
        )
    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(0)
    if size > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail=f"File 5MB se bari hai: {file.filename}"
        )


def _save_file(file: UploadFile) -> str:
    ext = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(MEDIA_DIR, filename).replace("\\", "/")
    with open(filepath, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return filepath


# ── Dishes List (Screen 2: Dishes List) ─────────────────────────────────────
@router.get("/", response_model=DishListResponse)
def get_dishes(
    skip: int = 0,
    limit: int = 20,
    status: Optional[str] = Query(None, description="draft ya published"),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Dish)

    if status:
        query = query.filter(Dish.status == status)
    if search:
        query = query.filter(Dish.name.ilike(f"%{search}%"))

    total = query.count()
    dishes = query.offset(skip).limit(limit).all()
    return {"total": total, "dishes": dishes}


# ── Dish Detail (Screen 4: Product Detail) ───────────────────────────────────
@router.get("/{dish_id}", response_model=DishResponse)
def get_dish(
    dish_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    dish = db.query(Dish).filter(Dish.id == dish_id).first()
    if not dish:
        raise HTTPException(status_code=404, detail="Dish nahi mili")
    return dish


# ── Dish Add (Screen 1: Dish Add) ────────────────────────────────────────────
@router.post("/", response_model=DishResponse, status_code=201)
def create_dish(
    dish_data: DishCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    dish = Dish(**dish_data.model_dump())
    db.add(dish)
    db.commit()
    db.refresh(dish)
    return dish


# ── Dish Edit (Screen 3: Products Edit) ──────────────────────────────────────
@router.put("/{dish_id}", response_model=DishResponse)
def update_dish(
    dish_id: int,
    dish_data: DishUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    dish = db.query(Dish).filter(Dish.id == dish_id).first()
    if not dish:
        raise HTTPException(status_code=404, detail="Dish nahi mili")

    update_fields = dish_data.model_dump(exclude_unset=True)
    for field, value in update_fields.items():
        setattr(dish, field, value)

    db.commit()
    db.refresh(dish)
    return dish


# ── Delete Dish ──────────────────────────────────────────────────────────────
@router.delete("/{dish_id}", status_code=204)
def delete_dish(
    dish_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    dish = db.query(Dish).filter(Dish.id == dish_id).first()
    if not dish:
        raise HTTPException(status_code=404, detail="Dish nahi mili")

    # Cover image delete karo agar hai
    if dish.cover_image and os.path.exists(dish.cover_image):
        os.remove(dish.cover_image)

    # Additional images bhi delete karo
    for img_url in dish.additional_images or []:
        if os.path.exists(img_url):
            os.remove(img_url)

    db.delete(dish)
    db.commit()


# ── Cover Image Upload ───────────────────────────────────────────────────────
@router.post("/{dish_id}/cover-image", response_model=DishResponse)
def upload_cover_image(
    dish_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    dish = db.query(Dish).filter(Dish.id == dish_id).first()
    if not dish:
        raise HTTPException(status_code=404, detail="Dish nahi mili")

    _validate_image(file)

    # Purani cover image delete karo
    if dish.cover_image and os.path.exists(dish.cover_image):
        os.remove(dish.cover_image)

    dish.cover_image = _save_file(file)
    db.commit()
    db.refresh(dish)
    return dish


# ── Additional Images Upload ─────────────────────────────────────────────────
@router.post("/{dish_id}/additional-images", response_model=DishResponse)
def upload_additional_images(
    dish_id: int,
    files: Annotated[list[UploadFile], File(description="Multiple image files")],
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    dish = db.query(Dish).filter(Dish.id == dish_id).first()
    if not dish:
        raise HTTPException(status_code=404, detail="Dish nahi mili")

    if not files:
        raise HTTPException(status_code=400, detail="Koi file upload nahi ki gayi")

    # Ensure additional_images is a list (handles NULL from old DB rows)
    images = []
    if dish.additional_images is not None:
        images = list(dish.additional_images)

    for file in files:
        _validate_image(file)
        filepath = _save_file(file)
        images.append(filepath)

    dish.additional_images = images
    db.commit()
    db.refresh(dish)
    return dish


# ── Cover Image Delete ───────────────────────────────────────────────────────
@router.delete("/{dish_id}/cover-image", status_code=204)
def delete_cover_image(
    dish_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Dish ki cover image delete karo"""
    dish = db.query(Dish).filter(Dish.id == dish_id).first()
    if not dish:
        raise HTTPException(status_code=404, detail="Dish nahi mili")

    if dish.cover_image and os.path.exists(dish.cover_image):
        os.remove(dish.cover_image)

    dish.cover_image = None
    db.commit()
    return


# ── Additional Image Delete ──────────────────────────────────────────────────
@router.delete("/{dish_id}/additional-images", status_code=204)
def delete_additional_image(
    dish_id: int,
    image_url: str = Query(..., description="Delete karne wali image ka URL"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Dish ki specific additional image delete karo"""
    dish = db.query(Dish).filter(Dish.id == dish_id).first()
    if not dish:
        raise HTTPException(status_code=404, detail="Dish nahi mili")

    images = list(dish.additional_images) if dish.additional_images else []
    if not images or image_url not in images:
        raise HTTPException(status_code=404, detail="Image nahi mili")

    if os.path.exists(image_url):
        os.remove(image_url)

    images.remove(image_url)
    dish.additional_images = images
    db.commit()
    return


# ── Status Toggle (Draft ↔ Published) ────────────────────────────────────────
@router.patch("/{dish_id}/status", response_model=DishResponse)
def toggle_status(
    dish_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Dish ka status draft ↔ published toggle karo"""
    dish = db.query(Dish).filter(Dish.id == dish_id).first()
    if not dish:
        raise HTTPException(status_code=404, detail="Dish nahi mili")

    dish.status = "published" if dish.status == "draft" else "draft"
    db.commit()
    db.refresh(dish)
    return dish
