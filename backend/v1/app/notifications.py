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
from backend.services.notifications import create_notification, get_or_create_tag

router = APIRouter()


# Dependency to get the current user (assuming you have an authentication mechanism)


@router.get("/", response_model=List[NotificationResponse])
async def read_notifications(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    notifications = db.query(Notification).filter(Notification.owner_id == current_user.id).all()
    return notifications


@router.post("/", response_model=NotificationResponse)
async def create_notification_endpoint(
    notification: NotificationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return create_notification(db=db, notification=notification, owner_id=current_user.id)

@router.patch("/{notification_id}/", response_model=NotificationResponse)
async def update_notification(notification_id: int, notification: NotificationCreate, current_user: User = Depends(get_current_user),
                              db: Session = Depends(get_db)):
    existing_notification = db.query(Notification).filter(Notification.id == notification_id,
                                                          Notification.owner_id == current_user.id).first()
    if not existing_notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")

    for key, value in notification.dict().items():
        if value:
            if key == 'tags':
                # print(notification.tags, type(notification.tags))
                # existing_notification.tags = value
                value = [get_or_create_tag(db, tag_name) for tag_name in value]
                # print(existing_notification.tags, value)
            # else:
            setattr(existing_notification, key, value)

    db.commit()
    db.refresh(existing_notification)
    return existing_notification

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



