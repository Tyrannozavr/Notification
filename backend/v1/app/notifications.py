from typing import List

from fastapi import HTTPException, status
from fastapi.params import Depends
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session

from core.database import get_db  # Assume you have a function to get the DB session
from core.models import User, Notification, Tag
from core.schemas import NotificationCreate, NotificationResponse, NotificationUpdate  # Import your schemas
from services.Auth import get_current_user
from services.notifications import create_notification, update_notification

router = APIRouter()

@router.get("/", response_model=List[NotificationResponse])
async def read_notifications(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    notifications = db.query(Notification).filter(Notification.owner_id == current_user.id).all()
    return notifications


@router.get("/get/{notification_id}/", response_model=NotificationResponse)
async def read_notifications(notification_id: int, current_user: User = Depends(get_current_user),
                             db: Session = Depends(get_db)):
    notification = db.query(Notification).filter(Notification.owner_id == current_user.id,
                                                 Notification.id == notification_id).first()
    return notification


@router.get("/tags/{tag_name}/", response_model=List[NotificationResponse])
async def filter_notifications_by_tag(tag_name: str, current_user: User = Depends(get_current_user),
                                      db: Session = Depends(get_db)):
    tag_name = f"#{tag_name}"
    print(tag_name)
    tag = db.query(Tag).filter(Tag.name == tag_name).first()
    if not tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, )
    notifications = (db.query(Notification)
                     .filter(Notification.tags.contains(tag),
                             Notification.owner_id == current_user.id).all())
    return notifications


@router.post("/", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
async def create_notification_endpoint(
        notification: NotificationCreate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    return create_notification(db=db, notification=notification, owner_id=current_user.id)


@router.patch("/{notification_id}/", response_model=NotificationResponse)
async def update_notification_view(notification_id: int, notification: NotificationUpdate,
                              current_user: User = Depends(get_current_user),
                              db: Session = Depends(get_db)):
    existing_notification = db.query(Notification).filter(Notification.id == notification_id,
                                                          Notification.owner_id == current_user.id).first()
    if not existing_notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Notification not found or you don't have permission to perform this operation")

    return update_notification(notification_id=notification_id, db=db, new_notification=notification.dict())


@router.delete("/{notification_id}/")
async def delete_notification(notification_id: int, current_user: User = Depends(get_current_user),
                              db: Session = Depends(get_db)):
    notification = db.query(Notification).filter(Notification.id == notification_id,
                                                 Notification.owner_id == current_user.id).first()
    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")

    db.delete(notification)
    db.commit()
    return status.HTTP_200_OK
