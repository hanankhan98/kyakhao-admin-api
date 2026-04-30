from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
import enum

# ✅ Role Enum
class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"
    SUPERADMIN = "superadmin"

class RegisterSchema(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: Optional[str] = "user"
    
    # ✅ Role validation - sirf 3 allowed
    @validator('role')
    def validate_role(cls, v):
        allowed = ["user", "admin", "superadmin"]
        if v not in allowed:
            raise ValueError(f'Role must be one of: {allowed}')
        return v

class LoginSchema(BaseModel):
    email: EmailStr
    password: str

class VerifyOTP(BaseModel):
    email: EmailStr
    otp: str

# ✅ Response Schema
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    is_verified: bool
    
    class Config:
        from_attributes = True