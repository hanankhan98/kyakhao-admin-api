from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DishCreate(BaseModel):
    name: str
    category: Optional[str] = None
    selling_price: float = 0.0
    cost_price: float = 0.0
    discounted_price: Optional[float] = None
    quantity: int = 0
    delivery: bool = False
    add_discount: bool = False
    return_policy: bool = False
    short_description: Optional[str] = None
    long_description: Optional[str] = None
    cover_image: Optional[str] = None
    additional_images: list[str] = []
    status: str = "draft"
    restaurant_id: Optional[int] = None
 
 
class DishUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    selling_price: Optional[float] = None
    cost_price: Optional[float] = None
    discounted_price: Optional[float] = None
    quantity: Optional[int] = None
    delivery: Optional[bool] = None
    add_discount: Optional[bool] = None
    return_policy: Optional[bool] = None
    short_description: Optional[str] = None
    long_description: Optional[str] = None
    cover_image: Optional[str] = None
    additional_images: Optional[list[str]] = None
    status: Optional[str] = None
    restaurant_id: Optional[int] = None
 
 
class DishResponse(BaseModel):
    id: int
    name: str
    category: Optional[str]
    selling_price: float
    cost_price: float
    discounted_price: Optional[float]
    quantity: int
    delivery: bool
    add_discount: bool
    return_policy: bool
    short_description: Optional[str]
    long_description: Optional[str]
    cover_image: Optional[str]
    additional_images: Optional[list[str]] = []
    status: str
    date_added: datetime
    restaurant_id: Optional[int]
 
    class Config:
        from_attributes = True
 
 
class DishListResponse(BaseModel):
    total: int
    dishes: list[DishResponse]
