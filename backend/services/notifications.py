from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from core.models import Notification, Tag
from core.schemas import NotificationCreate, NotificationUpdate


def get_or_create_tag(db: Session, tag_name: str) -> Tag:
    if not tag_name.startswith('#'):
        tag_name = f"#{tag_name}"
    tag = db.query(Tag).filter(Tag.name == tag_name).first()
    if not tag:
        tag = Tag(name=tag_name)
        db.add(tag)
    return tag


def create_notification(db: Session, notification: NotificationCreate, owner_id: int):
    # Create a new Notification instance
    db_notification = Notification(
        title=notification.title,
        description=notification.description,
        owner_id=owner_id
    )

    # Add tags if provided
    if notification.tags:
        for tag_name in notification.tags:
            tag = get_or_create_tag(db, tag_name)
            if tag not in db_notification.tags:
                db_notification.tags.append(tag)
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification


def update_notification(notification_id: int, new_notification: dict,  db: Session):
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    for key, value in new_notification.items():
        if value:
            if key == 'tags':
                value = [get_or_create_tag(db, tag_name) for tag_name in value]
            setattr(notification, key, value)

    db.commit()
    db.refresh(notification)
    return notification
