from datetime import timedelta

from fastapi import HTTPException
from fastapi import status
from fastapi.params import Depends
from fastapi.routing import APIRouter
from sqlalchemy.orm.session import Session

from core import settings
from core.database import get_db
from core.models import User
from core.schemas import Token, UserLogin, Payload
from core.settings import ACCESS_TOKEN_EXPIRE_MINUTES
from services.Auth import create_access_token, verify_password, get_password_hash, get_user_by_username, \
    check_telegram_authorization, get_current_user, get_or_create_link_token, get_user_by_link_token, \
    get_access_token_by_username

router = APIRouter()


@router.post("/register/", status_code=status.HTTP_201_CREATED)
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


@router.get("/telegram/link/")
def telegram_link(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """provides a link to our telegram bot which allows user to bind telegram to existing user"""
    link_token = get_or_create_link_token(current_user.id, db)
    return f"https://t.me/notification_dmiv_bot?start={link_token}"


@router.post("/telegram/link")
async def telegram_link(payload: Payload, db: Session = Depends(get_db)):
    BOT_TOKEN = settings.BOT_TOKEN
    is_from_telegram = check_telegram_authorization(auth_data=payload.data, bot_token=BOT_TOKEN)
    if is_from_telegram:
        user_data = payload.data
        link_token = user_data.get('link_token')
        if not link_token:
            raise HTTPException(status_code=401, detail="to connect bot get link on the website")
        user_telegram_id = user_data.get('id')
        user = await get_user_by_link_token(token=link_token, db=db)
        if not user:
            raise HTTPException(status_code=401, detail="account not found")
        user.telegram_id = user_telegram_id
        db.commit()
        return "OK"
    else:
        return HTTPException(status_code=401, detail="Telegram authorization failed")


@router.post("/telegram/login/")
async def telegram_login(payload: Payload, db: Session = Depends(get_db)):
    BOT_TOKEN = settings.BOT_TOKEN
    is_from_telegram = check_telegram_authorization(auth_data=payload.data, bot_token=BOT_TOKEN)
    if is_from_telegram:
        user_data = payload.data
        user_telegram_id = str(user_data.get('id'))
        user = db.query(User).filter(User.telegram_id == user_telegram_id).first()
        if not user:
            raise HTTPException(status_code=401, detail="Link you telegram to website's account")
        username = str(user.username)
        access_token = get_access_token_by_username(username=username)
        return {'access': access_token}
