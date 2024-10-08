from typing import Optional, List

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class UserLogin(BaseModel):
    username: str
    password: str


class TagBase(BaseModel):
    name: str  # Assuming each Tag has a name attribute


class NotificationBase(BaseModel):
    title: str
    description: str


class NotificationCreate(BaseModel):
    title: str
    description: str
    tags: List[str] = []  # List of tag names (strings)

class NotificationUpdate(BaseModel):
    title: str = None
    description: str = None
    tags: List[str] = None  # List of tag names (strings)


class NotificationResponse(NotificationBase):
    id: int
    tags: Optional[List[TagBase]] = []  # List of tag names (strings)

    class Config:
        from_attributes = True


class Payload(BaseModel):
    data: dict
