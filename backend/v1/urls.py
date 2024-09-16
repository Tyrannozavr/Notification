from datetime import timedelta
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from core.models import User
from core.schemas import Token
from core.settings import ACCESS_TOKEN_EXPIRE_MINUTES
from main import app
from services.Auth import authenticate_user, fake_users_db, create_access_token, get_current_active_user





@app.get("/users/me/", response_model=User)
async def read_users_me(
        current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user


@app.get("/users/me/items/")
async def read_own_items(
        current_user: Annotated[User, Depends(get_current_active_user)],
):
    return [{"item_id": "Foo", "owner": current_user.username}]
