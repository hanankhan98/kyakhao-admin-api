from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import Response, JSONResponse
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database.database import engine, get_db
from app.models.auth import Base, User, UserRole
from app.models.settings import DropdownSettings  # settings table auto-create ke liye
from app.schemas.auth import RegisterSchema, LoginSchema, VerifyOTP, UserResponse
from app.auth.auth import (
    hash_password, verify_password, create_token,
    security, get_current_user, require_admin, require_superadmin,
    SECRET_KEY, ALGORITHM
)
from app.auth.otp import generate_otp
from app.auth.email_utils import send_otp
from jose import jwt
from app.api.restaurant_add import router
from app.api.dishes import router as dishes_router
from app.api.public import router as public_router
from app.api.ai_pick import router as ai_pick_router
from app.api.settings import router as settings_router
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from dotenv import load_dotenv
import os
import traceback

load_dotenv()

# ================== DB INIT ==================
try:
    Base.metadata.create_all(bind=engine, checkfirst=True)
except Exception as e:
    print(f"[WARNING] DB connection failed: {e}")

# ================== APP INIT ==================
app = FastAPI(
    title="ADMIN API",
    description="Roles: user, admin, superadmin",
    version="2.0.0"
)

# ================== CORS ==================
cors_origins_str = os.getenv("CORS_ORIGINS", "")
origins = [origin.strip() for origin in cors_origins_str.split(",")] if cors_origins_str else []

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================== ERROR LOGGER ==================
class LogExceptionsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except Exception as exc:
            print("=== UNHANDLED EXCEPTION ===")
            traceback.print_exc()
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "Internal Server Error",
                    "error": str(exc)
                }
            )

app.add_middleware(LogExceptionsMiddleware)

# ================== STATIC ==================
os.makedirs("media", exist_ok=True)
app.mount("/media", StaticFiles(directory="media"), name="media")

# ================== ROUTERS ==================
app.include_router(router)
app.include_router(dishes_router)
app.include_router(public_router)
app.include_router(ai_pick_router)
app.include_router(settings_router)

# ================== PREFLIGHT ==================
@app.options("/{path:path}")
def preflight(path: str):
    return Response(status_code=200)

# ================== HEALTH ==================
@app.get("/health")
def health_check():
    return {"status": "OK"}

# ================== REGISTER ==================
@app.post("/register")
def register(user: RegisterSchema, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(400, "Email already exists")

    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(400, "Username already exists")

    otp = generate_otp()
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

    return {
        "message": "User registered. Check email for OTP",
        "role_assigned": role.value
    }

# ================== VERIFY ==================
@app.post("/verify")
def verify(data: VerifyOTP, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()

    if not user or user.otp != data.otp:
        raise HTTPException(400, "Invalid OTP")

    user.is_verified = True
    user.otp = None
    db.commit()

    return {"message": "Account verified", "role": user.role.value}

# ================== LOGIN (FULL DEBUG VERSION) ==================
@app.post("/login")
def login(user: LoginSchema, db: Session = Depends(get_db)):
    try:
        print(f"[LOGIN] Attempt: {user.email}")

        db_user = db.query(User).filter(User.email == user.email).first()
        print("[LOGIN] User:", db_user)

        if not db_user:
            raise HTTPException(400, "Invalid credentials")

        print("[LOGIN] Checking password...")
        if not verify_password(user.password, db_user.hashed_password):
            raise HTTPException(400, "Invalid credentials")

        print("[LOGIN] Checking verification...")
        if not getattr(db_user, "is_verified", False):
            raise HTTPException(400, "Please verify your account first")

        print("[LOGIN] Creating token...")
        token = create_token({
            "sub": db_user.email,
            "role": db_user.role.value if db_user.role else "user"
        })

        print("[LOGIN] SUCCESS")

        return {
            "access_token": token,
            "token_type": "bearer",
            "role": db_user.role.value if db_user.role else "user"
        }

    except HTTPException:
        raise
    except Exception as e:
        print("🔥 LOGIN ERROR:", str(e))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# ================== ME ==================
@app.get("/me", response_model=UserResponse)
def get_me(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
    except jwt.JWTError:
        raise HTTPException(401, "Invalid token")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(404, "User not found")

    return user

# ================== USER ==================
@app.get("/user/dashboard")
def user_dashboard(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.USER:
        raise HTTPException(403, "Only for users")

    return {"message": f"Welcome {current_user.username}", "role": current_user.role.value}

# ================== ADMIN ==================
@app.get("/admin/dashboard")
def admin_dashboard(current_user: User = Depends(require_admin)):
    return {
        "message": f"Welcome Admin {current_user.username}",
        "role": current_user.role.value
    }

@app.get("/admin/users")
def admin_users(current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [
        {"id": u.id, "username": u.username, "email": u.email, "role": u.role.value}
        for u in users
    ]

# ================== SUPERADMIN ==================
@app.get("/superadmin/dashboard")
def superadmin_dashboard(current_user: User = Depends(require_superadmin)):
    return {
        "message": f"Welcome Superadmin {current_user.username}",
        "role": current_user.role.value
    }

@app.delete("/superadmin/user/{user_id}")
def delete_user(user_id: int, current_user: User = Depends(require_superadmin), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(404, "User not found")

    db.delete(user)
    db.commit()

    return {"message": f"{user.username} deleted"}

@app.post("/superadmin/promote/{user_id}")
def promote_user(user_id: int, new_role: str, current_user: User = Depends(require_superadmin), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(404, "User not found")

    if new_role not in ["user", "admin"]:
        raise HTTPException(400, "Invalid role")

    user.role = UserRole(new_role)
    db.commit()

    return {"message": f"{user.username} promoted to {new_role}"}
