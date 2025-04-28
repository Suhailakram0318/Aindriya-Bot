import os
from dotenv import load_dotenv
import jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Dict
from sqlalchemy.orm import Session
from models import User

# Load environment variables
load_dotenv()

# Read the secret key from .env
SECRET_KEY = os.getenv("JWT_SECRET_KEY")  # Assuming your env variable is called JWT_SECRET_KEY

# Define token expiration times
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # 1 hour
REFRESH_TOKEN_EXPIRE_DAYS = 7     # 7 days

# Initialize password context for hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Function to hash the password
def get_password_hash(password: str) -> str:
    """
    Hash the provided password using bcrypt algorithm.
    """
    return pwd_context.hash(password)

# Function to verify the password hash
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify if the plain password matches the hashed password.
    """
    return pwd_context.verify(plain_password, hashed_password)

# Function to create an access token
def create_access_token(data: Dict[str, str], expires_delta: timedelta = None) -> str:
    """
    Create an access JWT token for a given user data.
    If expires_delta is provided, it overrides the default expiration.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt

# Function to create a refresh token
def create_refresh_token(data: Dict[str, str]) -> str:
    """
    Create a refresh JWT token with a longer expiration time (7 days).
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt

# Function to verify a token and return its payload
def verify_token(token: str) -> dict:
    """
    Verify a given token and return the payload if valid.
    Raises exceptions if the token is expired or invalid.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise Exception("Token expired")
    except jwt.InvalidTokenError:
        raise Exception("Invalid token")

# Optional: Function to get the current user from a JWT token (based on 'sub' claim)
def get_current_user_from_token(token: str) -> dict:
    """
    Decode the token and get the user details. Typically, the 'sub' claim
    will hold the user identifier.
    """
    try:
        payload = verify_token(token)
        return payload.get("sub")  # 'sub' is typically used for the subject (user)
    except Exception as e:
        raise Exception(f"Failed to extract user from token: {str(e)}")


# Database operations

# Register user in the database
def register_user(db: Session, username: str, email: str, password: str, full_name: str, role: str = "user") -> User:
    """
    Registers a new user in the database, hashes the password before storing it.
    """
    hashed_password = get_password_hash(password)
    db_user = User(username=username, email=email, hashed_password=hashed_password, full_name=full_name, role=role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Authenticate user login
def authenticate_user(db: Session, email: str, password: str) -> User:
    """
    Authenticate a user by verifying their email and password.
    If valid, return the User object, otherwise return None.
    """
    user = db.query(User).filter(User.email == email).first()
    if user and verify_password(password, user.hashed_password):
        return user
    return None

# Get user by email
def get_user_by_email(db: Session, email: str) -> User:
    """
    Retrieve a user from the database by email.
    """
    return db.query(User).filter(User.email == email).first()

