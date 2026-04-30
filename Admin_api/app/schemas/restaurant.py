from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
import re

class RestaurantBase(BaseModel):
    # Business Details
    business_name: Optional[str] = None
    tax_id: Optional[str] = None
    business_type: Optional[str] = None
    address: Optional[str] = None
    registration_number: Optional[str] = None

    # Personal Details
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    contact_number: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    birth_date: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    zip_code: Optional[str] = None
    description: Optional[str] = None
    logo: Optional[str] = None
    banner: Optional[str] = None

    # Bank Details
    bank_name: Optional[str] = None
    account_holder_name: Optional[str] = None
    account_number: Optional[str] = None
    ifsc_code: Optional[str] = None


class _ValidationMixin(BaseModel):
    @field_validator('business_name', 'tax_id', 'business_type', 'registration_number', mode='before', check_fields=False)
    @classmethod
    def no_special_chars(cls, v):
        if v is not None and v != "":
            if not re.match(r'^[a-zA-Z0-9\s]+$', str(v)):
                raise ValueError('Special characters are not allowed')
        return v

    @field_validator('first_name', 'last_name', 'city', 'country', 'bank_name', 'account_holder_name', mode='before', check_fields=False)
    @classmethod
    def letters_and_spaces_only(cls, v):
        if v is not None and v != "":
            if not re.match(r'^[a-zA-Z\s]+$', str(v)):
                raise ValueError('Only letters and spaces are allowed')
        return v

    @field_validator('contact_number', 'phone_number', 'zip_code', 'account_number', mode='before', check_fields=False)
    @classmethod
    def digits_only(cls, v):
        if v is not None and v != "":
            if not re.match(r'^\d+$', str(v)):
                raise ValueError('Only digits are allowed')
        return v

    @field_validator('ifsc_code', mode='before', check_fields=False)
    @classmethod
    def ifsc_alphanumeric(cls, v):
        if v is not None and v != "":
            if not re.match(r'^[a-zA-Z0-9]+$', str(v)):
                raise ValueError('Only letters and digits are allowed')
        return v


class RestaurantCreate(RestaurantBase, _ValidationMixin):
    business_name: str


class RestaurantUpdate(RestaurantBase, _ValidationMixin):
    pass


class RestaurantResponse(RestaurantBase):
    id: int

    class Config:
        from_attributes = True
