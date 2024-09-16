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
