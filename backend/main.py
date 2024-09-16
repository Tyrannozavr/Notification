from dotenv import load_dotenv
from fastapi import Depends
from fastapi import FastAPI
from fastapi.routing import APIRouter

from backend.v1.router import auth
from core.schemas import User
from services.Auth import get_current_active_user

load_dotenv('../.env')

app = FastAPI()

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(api_router, prefix="/api", tags=["api"])



@app.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


