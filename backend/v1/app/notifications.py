from typing import List

from fastapi.routing import APIRouter

from backend.core.models import Notification

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from backend.core.models import User, Notification
from backend.core.database import get_db  # Assume you have a function to get the DB session
from backend.core.schemas import NotificationCreate, NotificationResponse  # Import your schemas
from backend.services.Auth import get_current_user

router = APIRouter()


# Dependency to get the current user (assuming you have an authentication mechanism)


@router.get("/", response_model=List[NotificationResponse])
async def read_notifications(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    notifications = db.query(Notification).filter(Notification.owner_id == current_user.id).all()
    return notifications


@router.post("/", response_model=NotificationResponse)
async def create_notification(notification: NotificationCreate, current_user: User = Depends(get_current_user),
                              db: Session = Depends(get_db)):
    new_notification = Notification(**notification.dict(), owner_id=current_user.id)
    db.add(new_notification)
    db.commit()
    db.refresh(new_notification)
    return new_notification


@router.delete("/{id}", response_model=NotificationResponse)
async def delete_notification(notification_id: int, current_user: User = Depends(get_current_user),
                              db: Session = Depends(get_db)):
    notification = db.query(Notification).filter(Notification.id == notification_id,
                                                 Notification.owner_id == current_user.id).first()
    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")

    db.delete(notification)
    db.commit()
    return notification


@router.put("/{id}", response_model=NotificationResponse)
async def update_notification(notification_id: int, notification: NotificationCreate, current_user: User = Depends(get_current_user),
                              db: Session = Depends(get_db)):
    existing_notification = db.query(Notification).filter(Notification.id == notification_id,
                                                          Notification.owner_id == current_user.id).first()
    if not existing_notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")

    for key, value in notification.dict().items():
        setattr(existing_notification, key, value)

    db.commit()
    db.refresh(existing_notification)
    return existing_notification
