from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database.database import engine, get_db
from app.models.auth import Base, User, UserRole
from app.schemas.auth import RegisterSchema, LoginSchema, VerifyOTP, UserResponse
from app.auth.auth import (
    hash_password, verify_password, create_token, 
    security, get_current_user, require_admin, require_superadmin
)
from app.auth.otp import generate_otp
from app.auth.email_utils import send_otp
from jose import jwt
from app.auth.auth import SECRET_KEY, ALGORITHM
# from app.api.restaurant_add import restaurant
from app.api.restaurant_add import router
from app.api import restaurant_list, restaurant_detail, restaurant_edit
from app.api.dishes import router as dishes_router
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv()

Base.metadata.create_all(bind=engine, checkfirst=True)

app = FastAPI(
    title="ADMIN API",
    description="Roles: user, admin, superadmin",
    version="2.0.0"
)

# ✅ CORS Middleware - Frontend se requests allow krne ke liye
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production mein sirf frontend URL dena (e.g., ["http://localhost:3000"])
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Media files ─────────────────────────────
os.makedirs("media", exist_ok=True)
app.mount("/media", StaticFiles(directory="media"), name="media")

app.include_router(router)
app.include_router(dishes_router)
@app.get("/health")
def health_check():
    return {"status": "OK"}
# ✅ Register - Role assign ho sakta hai
@app.post("/register")
def register(user: RegisterSchema, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(400, "Email already exists")
    
    existing_username = db.query(User).filter(User.username == user.username).first()
    if existing_username:
        raise HTTPException(400, "Username already exists")

    otp = generate_otp()

    # ✅ Role set karna
    role = UserRole(user.role) if user.role else UserRole.USER
    
    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hash_password(user.password),
        otp=otp,
        role=role
    )

    db.add(new_user)
    db.commit()

    send_otp(user.email, otp)

    return {"message": "User registered. Check email for OTP", "role_assigned": user.role or "user"}

# ✅ Verify OTP
@app.post("/verify")
def verify(data: VerifyOTP, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or user.otp != data.otp:
        raise HTTPException(400, "Invalid OTP")

    user.is_verified = True
    user.otp = None
    db.commit()

    return {"message": "Account verified", "role": user.role.value}

# ✅ Login - Token mein role bhi jayega
@app.post("/login")
def login(user: LoginSchema, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(400, "Invalid credentials")

    if not db_user.is_verified:
        raise HTTPException(400, "Verify your account first")

    token = create_token({
        "sub": db_user.email,
        "role": db_user.role.value
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "role": db_user.role.value
    }

# ✅ ANY USER - Apna profile dekhe
@app.get("/me", response_model=UserResponse)
def get_me(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
    except jwt.JWTError:
        raise HTTPException(401, "Invalid token")
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(404, "User not found")
    
    return user

# ✅ USER ONLY - Normal user endpoints
@app.get("/user/dashboard")
def user_dashboard(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.USER:
        raise HTTPException(403, "Only for users")
    return {"message": f"Welcome User {current_user.username}", "role": current_user.role.value}

# ✅ ADMIN + SUPERADMIN - Admin endpoints
@app.get("/admin/dashboard")
def admin_dashboard(current_user: User = Depends(require_admin)):
    return {
        "message": f"Welcome Admin {current_user.username}",
        "role": current_user.role.value,
        "access_level": "admin"
    }

@app.get("/admin/users")
def admin_get_users(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    users = db.query(User).all()
    return [{"id": u.id, "username": u.username, "email": u.email, "role": u.role.value} for u in users]

# ✅ SUPERADMIN ONLY - Super admin endpoints
@app.get("/superadmin/dashboard")
def superadmin_dashboard(current_user: User = Depends(require_superadmin)):
    return {
        "message": f"Welcome Superadmin {current_user.username}",
        "role": current_user.role.value,
        "access_level": "super"
    }

@app.delete("/superadmin/user/{user_id}")
def superadmin_delete_user(
    user_id: int,
    current_user: User = Depends(require_superadmin),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    
    db.delete(user)
    db.commit()
    return {"message": f"User {user.username} deleted by superadmin"}

@app.post("/superadmin/promote/{user_id}")
def superadmin_promote_user(
    user_id: int,
    new_role: str,  # "admin" ya "user"
    current_user: User = Depends(require_superadmin),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    
    if new_role not in ["user", "admin"]:
        raise HTTPException(400, "Can only promote to user or admin")
    
    user.role = UserRole(new_role)
    db.commit()
    return {"message": f"User {user.username} promoted to {new_role}"}
