from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from .database import SessionLocal, engine
from .models import Base, User
from .schemas import RegisterSchema, LoginSchema, VerifyOTP
from .auth import hash_password, verify_password, create_token
from .otp import generate_otp
from .email_utils import send_otp

Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ✅ Register
@app.post("/register")
def register(user: RegisterSchema, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(400, "Email already exists")

    otp = generate_otp()

    new_user = User(
        email=user.email,
        password=hash_password(user.password),
        otp=otp
    )

    db.add(new_user)
    db.commit()

    send_otp(user.email, otp)

    return {"message": "User registered. Check email for OTP"}


# ✅ Verify OTP
@app.post("/verify")
def verify(data: VerifyOTP, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()

    if not user or user.otp != data.otp:
        raise HTTPException(400, "Invalid OTP")

    user.is_verified = True
    user.otp = None
    db.commit()

    return {"message": "Account verified"}


# ✅ Login
@app.post("/login")
def login(user: LoginSchema, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(400, "Invalid credentials")

    if not db_user.is_verified:
        raise HTTPException(400, "Verify your account first")

    token = create_token({"sub": db_user.email})

    return {"access_token": token}