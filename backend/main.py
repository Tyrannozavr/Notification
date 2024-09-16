from dotenv import load_dotenv
from fastapi import FastAPI

from backend.core.db import init_db
from backend.v1.router.main import api_router

load_dotenv('../.env')

app = FastAPI()
init_db()

app.include_router(api_router, prefix="/api", tags=["api"])

# Dependency to get the DB session


# @app.get("/users/me", response_model=User)
# async def read_users_me(current_user: User = Depends(get_current_active_user)):
#     return current_user


