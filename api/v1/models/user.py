from .base_model import BaseModel
from datetime import datetime
from mongoengine import (
    StringField, EmailField, URLField,
    BooleanField, DateTimeField
)

class User(BaseModel):
    email = EmailField(required=True, unique=True)
    first_name = StringField()
    last_name = StringField()
    avatar_url = URLField()
    is_active = BooleanField(default=False)
    is_superadmin = BooleanField(default=False)
    is_deleted = BooleanField(default=False)
    is_verified = BooleanField(default=False)
    last_login = DateTimeField(defualt= lambda: datetime.now(datetime.timezone.utc))

    meta = {
        "collection": "users"
    }