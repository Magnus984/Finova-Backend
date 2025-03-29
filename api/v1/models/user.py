from .base_model import BaseModel
from datetime import datetime, timezone
from mongoengine import (
    StringField, EmailField, URLField,
    BooleanField, DateTimeField, ReferenceField
)
import mongoengine
from .company import Company

class User(BaseModel):
    email = EmailField(required=True, unique=True)
    first_name = StringField()
    last_name = StringField()
    password = StringField()
    avatar_url = URLField()
    is_active = BooleanField(default=False)
    is_superadmin = BooleanField(default=False)
    is_deleted = BooleanField(default=False)
    is_verified = BooleanField(default=False)
    last_login = DateTimeField(default=lambda: datetime.now(timezone.utc))
    
    company = ReferenceField("Company", reverse_delete_rule=mongoengine.NULLIFY)

    meta = {
        "collection": "users",
        "indexes": [
            "email",
        ]
    }