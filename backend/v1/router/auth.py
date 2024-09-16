from fastapi.routing import APIRouter

router = APIRouter()

@router.get("/")
def hello():
    return {"message": "Hello World"}