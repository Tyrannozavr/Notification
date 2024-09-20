import hashlib
import hmac
import secrets
from datetime import datetime, timezone, timedelta
from typing import Annotated

import jwt
from fastapi import Depends
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from starlette import status

from core import settings
from core.database import get_db
from core.models import User, LinkToken
from core.schemas import TokenData
from core.settings import ACCESS_TOKEN_EXPIRE_MINUTES

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def get_access_token_by_username(username: str):
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": username}, expires_delta=access_token_expires
    )
    return access_token

def generate_short_token(length=16):
    return secrets.token_urlsafe(length)[:length]  # Generate a secure token


def get_or_create_link_token(user_id: int, db: Session):
    # Generate a short token
    short_token = generate_short_token()
    link_token = db.query(LinkToken).filter(LinkToken.user_id == user_id).first()
    if link_token:
        return link_token.token
    else:
        # Create a LinkAccount entry in the database
        link_account = LinkToken(user_id=user_id, token=short_token)
        db.add(link_account)
        db.commit()

        return short_token


async def get_user_by_link_token(token: str, db: Session):
    # Retrieve the LinkAccount from the database
    link_account = db.query(LinkToken).filter_by(token=token).first()

    if not link_account:
        return None  # Token not found in the database
    user = db.query(User).filter_by(id=link_account.user_id).first()
    return user  # Return the user ID associated with the token


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except:
        raise credentials_exception
    user = get_user_by_username(db=db, username=username)
    if user is None:
        raise credentials_exception
    return user


def check_telegram_authorization(auth_data: dict, bot_token: str):
    check_hash = auth_data['hash']
    del auth_data['hash']
    data_check_arr = [f"{key}={value}" for key, value in auth_data.items()]
    data_check_arr.sort()
    data_check_string = "\n".join(data_check_arr)
    secret_key = hashlib.sha256(bot_token.encode()).digest()
    hash_signature = hmac.new(secret_key, msg=data_check_string.encode(), digestmod=hashlib.sha256).hexdigest()
    return hash_signature == check_hash
