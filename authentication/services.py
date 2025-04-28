# services.py

from sqlalchemy.orm import Session
from models import User
from utils import get_password_hash, verify_password, create_access_token
from models import UserRegister, UserLogin, PasswordReset
from datetime import timedelta

def register_user(user_data: UserRegister, db: Session):
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise Exception("User already exists")

    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        role=user_data.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return "✅ User registered successfully!"

def login_user(login_data: UserLogin, db: Session):
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise Exception("Invalid credentials")

    access_token = create_access_token(
        data={"sub": user.email, "role": user.role},
        expires_delta=timedelta(minutes=60)
    )
    return {"access_token": access_token, "token_type": "bearer"}

def reset_password(reset_data: PasswordReset, db: Session):
    user = db.query(User).filter(User.email == reset_data.email).first()
    if not user:
        raise Exception("User not found")

    hashed_password = get_password_hash(reset_data.new_password)
    user.hashed_password = hashed_password
    db.commit()
    return "✅ Password reset successful!"
