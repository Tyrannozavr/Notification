from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.routing import APIRouter

load_dotenv('../.env')

app = FastAPI()


from backend.v1.router import auth


api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(api_router, prefix="/api", tags=["api"])



from datetime import timedelta

from fastapi import Depends, HTTPException

from core.schemas import Token, User, UserLogin, UserInDB
from core.settings import ACCESS_TOKEN_EXPIRE_MINUTES
from services.Auth import fake_users_db, create_access_token, get_current_active_user, \
    verify_password, get_password_hash


@app.post("/register", response_model=User)
async def register(user: UserLogin):
    if user.username in fake_users_db:
        raise HTTPException(status_code=400, detail="Username already registered")

    password_hash = get_password_hash(user.password)
    response_user = UserInDB(
        username=user.username,
        hashed_password=password_hash  # Set a default password or add a password field
    )
    fake_users_db[user.username] = response_user
    return response_user

@app.post("/token", response_model=Token)
async def login(form_data: UserLogin):
    user = fake_users_db.get(form_data.username)
    if not user or not verify_password(form_data.password, user.get('hashed_password')):
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.get('username')}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


