from .base_model import BaseModel
from mongoengine import (
    StringField, ReferenceField, URLField,
    EmailField, ListField, BooleanField
)

class Company(BaseModel):
    name = StringField(required=True, unique=True)
    size = StringField(required=True)
    business_email = EmailField(required=True)
    business_phone = StringField(required=True)
    address = StringField(required=True)
    industry = StringField(requried=True)
    
    # Link to User who owns/created the company
    owner = ReferenceField("User", required=True)

    meta = {
        'collection': 'companies',
        'indexes': [
            {'fields': ['name', 'owner'], 'unique': True}
        ]
    }

    def to_dict(self):
        """Convert the Company object to a dictionary."""
        return {
            'id': str(self.id),
            'name': self.name,
            'size': self.size,
            'business_email': self.business_email,
            'business_phone': self.business_phone,
            'address': self.address,
            'industry': self.industry,
            'owner': str(self.owner.id) if self.owner else None
        }