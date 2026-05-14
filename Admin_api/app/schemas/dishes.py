from pydantic import BaseModel
from typing import Optional


class DishCreate(BaseModel):
    name: str
    cuisine: Optional[str] = None
    price: float = 0.0
    meal_type: Optional[str] = None
    meal_time: Optional[str] = None
    texture: Optional[str] = None
    dietary_type: Optional[str] = None
    calories: Optional[int] = None
    spicy: bool = False
    long_description: Optional[str] = None
    cover_image: Optional[str] = None
    additional_images: list[str] = []
    status: str = "draft"
    restaurant_id: Optional[int] = None


class DishUpdate(BaseModel):
    name: Optional[str] = None
    cuisine: Optional[str] = None
    price: Optional[float] = None
    meal_type: Optional[str] = None
    meal_time: Optional[str] = None
    texture: Optional[str] = None
    dietary_type: Optional[str] = None
    calories: Optional[int] = None
    spicy: Optional[bool] = None
    long_description: Optional[str] = None
    cover_image: Optional[str] = None
    additional_images: Optional[list[str]] = None
    status: Optional[str] = None
    restaurant_id: Optional[int] = None


class DishResponse(BaseModel):
    id: int
    name: str
    cuisine: Optional[str] = None
    price: Optional[float] = None
    meal_type: Optional[str] = None
    meal_time: Optional[str] = None
    texture: Optional[str] = None
    dietary_type: Optional[str] = None
    calories: Optional[int] = None
    spicy: Optional[bool] = None
    long_description: Optional[str] = None
    cover_image: Optional[str] = None
    additional_images: Optional[list[str]] = None
    status: Optional[str] = None
    restaurant_id: Optional[int] = None

    class Config:
        from_attributes = True


class DishListResponse(BaseModel):
    total: int
    dishes: list[DishResponse]
