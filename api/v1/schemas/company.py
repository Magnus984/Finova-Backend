from pydantic import (
    BaseModel, 
    EmailStr, 
    constr, 
    field_validator,
    Field,
    ConfigDict
)
from typing import Annotated, Optional
from enum import Enum

class CompanySize(str, Enum):
    MICRO = "1-9"
    SMALL = "10-49"
    MEDIUM = "50-249"
    LARGE = "250+"

class CompanyCreate(BaseModel):
    name: Annotated[str, Field(min_length=2, max_length=100)]
    size: CompanySize
    business_email: EmailStr
    business_phone: Annotated[str, Field(
        pattern=r'^\d{10}$',
        description="Phone number must be exactly 10 digits"
    )]
    address: Annotated[str, Field(min_length=5, max_length=200)]
    industry: Annotated[str, Field(min_length=2, max_length=100)]

    @field_validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty or just whitespace')
        return v.strip()

    @field_validator('business_phone')
    def validate_phone(cls, v):
        # Remove any spaces or special characters
        cleaned = ''.join(filter(str.isdigit, v))
        if len(cleaned) < 10:
            raise ValueError('Phone number must be at least 10 digits')
        return cleaned
    


    class Config:
        json_schema_extra = {
            "example": {
                "name": "Acme Corporation",
                "size": "10-49",
                "business_email": "contact@acme.com",
                "business_phone": "1234567890",
                "address": "123 Business Street, City, Country",
                "industry": "Technology"
            }
        }

class CompanyResponse(BaseModel):
    id: str
    name: str
    size: str
    business_email: EmailStr
    business_phone: str
    address: str
    industry: str
    owner: str
    model_config = ConfigDict(from_attributes=True)

    @field_validator('owner', mode='before')
    def validate_owner_id(cls, v):
        """Convert owner ObjectId to string if present"""
        if hasattr(v, 'id'):  # If v is a User object
            return str(v.id)
        elif v:  # If v is already an ID
            return str(v)
        return None