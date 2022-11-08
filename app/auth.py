import os
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import ValidationError

from .models import User, TokenPayload


ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7
ALGORITHM = "HS256"
JWT_SECRET_KEY = os.environ['JWT_SECRET_KEY']
JWT_REFRESH_SECRET_KEY = os.environ['JWT_REFRESH_SECRET_KEY']

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

reuseable_oauth = OAuth2PasswordBearer(tokenUrl="/login", scheme_name="JWT")


def get_hashed_password(password: str) -> str:
    """
        Returns the hash value of user password
    """

    return password_context.hash(password)


def verify_password(password: str, hashed_pass: str) -> bool:
    """
        Verifying the given password by stored hash
    """

    return password_context.verify(password, hashed_pass)


def create_access_token(subject: str, expires_delta: int = None) -> str:
    """
        Creating access JWT token from the user's email
    """

    if expires_delta is not None:
        expires_delta += datetime.utcnow()
    else:
        expires_delta = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {"exp": expires_delta, "sub": subject}

    return jwt.encode(to_encode, JWT_SECRET_KEY, ALGORITHM)


def create_refresh_token(subject: str, expires_delta: int = None) -> str:
    """
        Creating refresh JWT token from the user's email
    """

    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)

    to_encode = {"exp": expires_delta, "sub": subject}

    return jwt.encode(to_encode, JWT_REFRESH_SECRET_KEY, ALGORITHM)


async def get_current_user(token: str = Depends(reuseable_oauth)) -> User:
    """
        Validating the current JWT token not expired and getting the user's email
        from the token. Retrieving user instance by this email
    """

    try:
        payload = jwt.decode(
            token, JWT_SECRET_KEY, algorithms=[ALGORITHM]
        )

        token_data = TokenPayload(**payload)

        if datetime.fromtimestamp(token_data.exp) < datetime.now():
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )

    except(JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if not (user := User.find(User.email == token_data.sub).all()):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user[0]
