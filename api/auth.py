"""Authentication module for LangExtract API."""

import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from dotenv import load_dotenv

load_dotenv()

# Configuration
SECRET_KEY = os.getenv("API_SECRET_KEY", "your-super-secret-key-change-this-in-production")
ALGORITHM = os.getenv("API_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("API_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


def verify_token(token: str) -> dict:
    """Verify and decode a JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return payload
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def authenticate_token(token: str) -> dict:
    """Authenticate a token and return user info."""
    return verify_token(token)


class UserManager:
    """Simple user management for demo purposes."""
    
    def __init__(self):
        # In production, use a proper database
        self.users = {
            "admin": {
                "username": "admin",
                "hashed_password": get_password_hash("admin"),
                "is_active": True,
                "roles": ["admin"]
            },
            "user": {
                "username": "user",
                "hashed_password": get_password_hash("user123"),
                "is_active": True,
                "roles": ["user"]
            }
        }
    
    def get_user(self, username: str) -> Optional[dict]:
        """Get user by username."""
        return self.users.get(username)
    
    def authenticate_user(self, username: str, password: str) -> Optional[dict]:
        """Authenticate user with username and password."""
        user = self.get_user(username)
        if not user:
            return None
        
        if not verify_password(password, user["hashed_password"]):
            return None
        
        return user
    
    def create_user(self, username: str, password: str, roles: list = None) -> dict:
        """Create a new user."""
        if username in self.users:
            raise ValueError("User already exists")
        
        if roles is None:
            roles = ["user"]
        
        user = {
            "username": username,
            "hashed_password": get_password_hash(password),
            "is_active": True,
            "roles": roles
        }
        
        self.users[username] = user
        return user
    
    def update_user(self, username: str, **kwargs) -> Optional[dict]:
        """Update user information."""
        user = self.users.get(username)
        if not user:
            return None
        
        for key, value in kwargs.items():
            if key == "password":
                user["hashed_password"] = get_password_hash(value)
            elif key in user:
                user[key] = value
        
        return user
    
    def delete_user(self, username: str) -> bool:
        """Delete a user."""
        if username in self.users:
            del self.users[username]
            return True
        return False
    
    def list_users(self) -> list:
        """List all users (without passwords)."""
        users = []
        for user in self.users.values():
            user_info = user.copy()
            del user_info["hashed_password"]
            users.append(user_info)
        return users


# Global user manager instance
user_manager = UserManager()


def get_current_user(token: str) -> dict:
    """Get current user from token."""
    payload = verify_token(token)
    username = payload.get("sub")
    
    user = user_manager.get_user(username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


def require_role(required_role: str):
    """Decorator to require specific role."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # This would be implemented with proper dependency injection
            # For now, it's a placeholder
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def check_api_key(api_key: str, provider: str) -> bool:
    """Check if API key is valid for provider."""
    # In production, implement proper API key validation
    if not api_key:
        return False
    
    # Basic validation - check if key looks valid
    if provider == "openai" and not api_key.startswith("sk-"):
        return False
    
    if provider == "gemini" and len(api_key) < 20:
        return False
    
    return True


def get_api_key_for_provider(provider: str, user_provided_key: str = None) -> Optional[str]:
    """Get API key for a specific provider."""
    if user_provided_key:
        return user_provided_key
    
    # Try to get from environment
    env_keys = {
        "openai": "OPENAI_API_KEY",
        "gemini": "GEMINI_API_KEY",
        "langextract": "LANGEXTRACT_API_KEY"
    }
    
    env_key = env_keys.get(provider.lower())
    if env_key:
        return os.getenv(env_key)
    
    return None