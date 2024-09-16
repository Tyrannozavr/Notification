from sqlalchemy.orm import Session

from backend.core.models import Notification, Tag
from backend.core.schemas import NotificationCreate


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
            # Check if the tag already exists
            tag = db.query(Tag).filter(Tag.name == tag_name).first()
            if not tag:
                # If not, create a new Tag
                tag = Tag(name=tag_name)
                db.add(tag)
            db_notification.tags.append(tag)

    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification