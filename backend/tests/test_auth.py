import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from backend.main import app  # Adjust according to your project structure
from backend.core.database import get_db
from backend.core.models import User
from backend.core.schemas import UserLogin

# Create a test client using the FastAPI app
client = TestClient(app)


@pytest.fixture(scope="module")
def test_db():
    # Setup a test database session
    db = get_db()
    yield db
    # Teardown logic if needed


def test_register_user(test_db: Session):
    # Test user registration
    user_data = {"username": "testuser", "password": "testpassword"}
    response = client.post("/api/auth/register/", json=user_data)

    assert response.status_code == 200
    assert response.json()["username"] == "testuser"

    # Check if the user is created in the database
    new_user = test_db.query(User).filter_by(username="testuser").first()
    assert new_user is not None
    assert new_user.username == "testuser"


def test_register_existing_user(test_db: Session):
    # Attempt to register the same user again
    user_data = {"username": "testuser", "password": "testpassword"}
    response = client.post("/register/", json=user_data)

    assert response.status_code == 400
    assert response.json()["detail"] == "Username already registered"


def test_login_user(test_db: Session):
    # Test user login
    login_data = {"username": "testuser", "password": "testpassword"}
    response = client.post("/token", data=login_data)

    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_invalid_user(test_db: Session):
    # Attempt to login with invalid credentials
    login_data = {"username": "invaliduser", "password": "wrongpassword"}
    response = client.post("/token", data=login_data)

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"
