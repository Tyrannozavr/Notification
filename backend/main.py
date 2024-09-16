import os

from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv('../.env')

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
@app.get('/token')
async def get_token():
    return {'hello': "world"}


from datetime import timedelta
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from core.models import User
from core.schemas import Token, User, UserLogin, UserInDB
from core.settings import ACCESS_TOKEN_EXPIRE_MINUTES
from main import app
from services.Auth import authenticate_user, fake_users_db, create_access_token, get_current_active_user, \
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
