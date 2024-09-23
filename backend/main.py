from urllib.request import Request

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from starlette.responses import JSONResponse

from core.database import init_db
from logger import logger
from v1.app.router import api_router

load_dotenv('../.env')

app = FastAPI()
init_db()

app.include_router(api_router, prefix="/api", tags=["api"])

# Dependency to get the DB session

# Custom exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # You can log the exception here if needed
    logger.exception(exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred.", "error": str(exc)},
    )

