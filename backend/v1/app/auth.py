from fastapi.params import Depends
from fastapi.routing import APIRouter
from datetime import timedelta

from fastapi import HTTPException
from fastapi.routing import APIRouter
from sqlalchemy.orm.session import Session

from backend.core import settings
from backend.core.database import get_db
from backend.core.models import User
from backend.core.schemas import Token, UserLogin, Payload
from backend.core.settings import ACCESS_TOKEN_EXPIRE_MINUTES
from backend.services.Auth import create_access_token, verify_password, get_password_hash, get_user_by_username, \
    check_telegram_authorization

router = APIRouter()


@router.post("/register/")
def register_user(user: UserLogin, db: Session = Depends(get_db)):
    # Hash password here (use your preferred hashing method)
    existing_user = get_user_by_username(db, user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_password = get_password_hash(user.password)  # Implement this function as needed

    # Create new user instance
    new_user = User(
        username=user.username,
        hashed_password=hashed_password,
        is_active=True,
    )

    # Add user to the database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/token", response_model=Token)
async def login(form_data: UserLogin, db: Session = Depends(get_db)):
    user = get_user_by_username(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/telegram/link")
def telegram_link():
    access_token = 'test_access_token'
    return f"<a href='https://t.me/notification_dmiv_bot?start={access_token}'>Telegram</a>"




@router.post("/telegram/link")
async def telegram_link(payload: Payload, db: Session = Depends(get_db)):
    BOT_TOKEN = settings.BOT_TOKEN
    is_from_telegram = check_telegram_authorization(auth_data=payload.data, bot_token=BOT_TOKEN)
    if is_from_telegram:
        return "OK"
    else:
        return HTTPException(status_code=401, detail="Telegram authorization failed")
