import os
from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional, Dict

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.ext.asyncio.session import AsyncSession

from .db import get_session
from .models.user import User


async def get_user_by_username(username: str, session: AsyncSession) -> Optional[User]:
    """Fetches a user from the database by username"""
    pass


SECRET_KEY = os.getenv("SECRET_KEY", "secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class TokenData(BaseModel):
    """Schema for data contained within the JWT."""

    username: Optional[str] = None


class Token(BaseModel):
    """Schema for the response when requesting a token."""

    access_token: str
    token_type: str = "bearer"


def create_access_token(data: Dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], session: Annotated[AsyncSession, Depends(get_session)]
) -> Optional[User]:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    user = await get_user_by_username(username=token_data.username, session=session)
    if user is None:
        raise credentials_exception
    return user


async def authenticate_user(username: str, password: str, session: AsyncSession):
    """Authenticates a user by username and password"""
    user = await get_user_by_username(username, session)
    if not user:
        return None

    if not hasattr(user, "hashed_password") or not user.hashed_password:
        print(f"Warning: User {username} has no hashed_password set")
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
