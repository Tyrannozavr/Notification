import pytest
from main import app  # Replace with the actual path to your FastAPI app
from fastapi.testclient import TestClient

from services.Auth import fake_users_db

# Create a TestClient instance
client = TestClient(app)

# Sample user data for testing
test_user = {
    "username": "johndoe",
    "full_name": "John Doe",
    "email": "johndoe@example.com",
    "password": "123456",
}


@pytest.fixture
def create_user():
    # Simulate creating a user in the fake database
    fake_users_db[test_user["username"]] = {
        "username": test_user["username"],
        "full_name": test_user["full_name"],
        "email": test_user["email"],
        "password": test_user["password"],  # In a real scenario, this should be hashed
        "disabled": False,
    }


def test_authenticate_user(create_user):
    response = client.post("/token", data={"username": test_user["username"], "password": test_user["password"]})

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_authenticate_invalid_user():
    response = client.post("/token", data={"username": "invaliduser", "password": "wrongpassword"})

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"


def test_get_current_user(create_user):
    # First, authenticate to get the access token
    token_response = client.post("/token", data={"username": test_user["username"], "password": test_user["password"]})
    access_token = token_response.json()["access_token"]

    # Use the access token to get the current user
    response = client.get("/users/me", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 200
    assert response.json()["username"] == test_user["username"]
    assert response.json()["full_name"] == test_user["full_name"]


def test_get_current_active_user(create_user):
    # Authenticate to get the access token
    token_response = client.post("/token", data={"username": test_user["username"], "password": test_user["password"]})
    access_token = token_response.json()["access_token"]

    # Use the access token to get the current active user
    response = client.get("/users/me", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 200
    assert response.json()["username"] == test_user["username"]
    assert not response.json().get("disabled")


def test_get_current_active_inactive_user():
    # Simulate creating an inactive user
    fake_users_db["inactiveuser"] = {
        "username": "inactiveuser",
        "full_name": "Inactive User",
        "email": "inactive@example.com",
        "password": "123456",
        "disabled": True,
    }

    # Authenticate to get the access token for inactive user
    token_response = client.post("/token", data={"username": "inactiveuser", "password": "123456"})
    access_token = token_response.json()["access_token"]

    # Try to get the current active user with the inactive user token
    response = client.get("/users/me", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 400
    assert response.json()["detail"] == "Inactive user"
