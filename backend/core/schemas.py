from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    username: str
    hashed_password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserInDB(User):
    hashed_password: str
