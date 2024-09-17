from sqlalchemy.orm import Session

from backend.core.models import Notification, Tag
from backend.core.schemas import NotificationCreate


def get_or_create_tag(db: Session, tag_name: str) -> Tag:
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
            if not tag_name.startswith("#"):
                tag_name = f"#{tag_name}"
            tag = get_or_create_tag(db, tag_name)
            if tag not in db_notification.tags:
                db_notification.tags.append(tag)
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification

def update_notification(db: Session, notification: Notification, owner_id: int):
    db_notification = db.query(Notification).filter(
        Notification.id == notification.id
    )
    if notification.title:
        db_notification.title = notification.title
        db_notification.description = notification.description
        db_notification.owner_id = owner_id
        db.commit()
        db.refresh(db_notification)
        return db_notification
