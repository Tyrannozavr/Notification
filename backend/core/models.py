from sqlalchemy import Boolean
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.schema import Table

from backend.core.database import Base

# Association Table
notification_tags = Table(
    'notification_tags',
    Base.metadata,
    Column('notification_id', Integer, ForeignKey('notifications.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    telegram_id = Column(String, nullable=True)

    notifications = relationship("Notification", back_populates="owner")
    link_token = relationship("LinkToken", back_populates="user", uselist=False)  # One-to-one relationship


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, index=True)

    notifications = relationship("Notification", secondary=notification_tags, back_populates="tags")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="notifications")
    tags = relationship("Tag", secondary=notification_tags, back_populates="notifications")

    # New fields for timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class LinkToken(Base):
    __tablename__ = "link_tokens"

    id = Column(Integer, primary_key=True)
    token = Column(String, unique=True, index=True)  # This will store the generated token
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)  # Ensure one-to-one relationship

    user = relationship("User", back_populates="link_token")

    # New fields for timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())



