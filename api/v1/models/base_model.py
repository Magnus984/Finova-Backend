"""
Base Model module
"""
import uuid
from datetime import datetime, timezone
from mongoengine import Document, StringField, DateTimeField, UUIDField

class BaseModel(Document):
    """
    BaseModel class
    """
    id = StringField(primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = DateTimeField(default=lambda: datetime.now(timezone.utc))
    updated_at = DateTimeField(default=lambda: datetime.now(timezone.utc))

    meta = {
        'abstract': True
    }