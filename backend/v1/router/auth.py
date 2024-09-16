from fastapi.routing import APIRouter
from datetime import timedelta

from fastapi import HTTPException
from fastapi.routing import APIRouter

from backend.core.schemas import Token, User, UserLogin, UserInDB
from backend.core.settings import ACCESS_TOKEN_EXPIRE_MINUTES
from backend.services.Auth import fake_users_db, create_access_token, verify_password, get_password_hash

router = APIRouter()

@router.get("/")
def hello():
    return {"message": "Hello World"}


@router.post("/register", response_model=User)
async def register(user: UserLogin):
    if user.username in fake_users_db:
        raise HTTPException(status_code=400, detail="Username already registered")

    password_hash = get_password_hash(user.password)
    response_user = UserInDB(
        username=user.username,
        hashed_password=password_hash  # Set a default password or add a password field,

    )
    fake_users_db[user.username] = response_user
    return response_user


@router.post("/token", response_model=Token)
async def login(form_data: UserLogin):
    user = fake_users_db.get(form_data.username)
    if not user or not verify_password(form_data.password, user.get('hashed_password')):
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.get('username')}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}