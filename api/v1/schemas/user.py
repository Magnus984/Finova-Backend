from pydantic import (
    BaseModel,
    EmailStr,
    ConfigDict,
    StringConstraints,
    model_validator,
)
from typing import Optional
from typing import Optional, Union, List, Annotated, Dict, Any
from datetime import datetime


class UserCreate(BaseModel):
    """Schema to create a user"""
    email: EmailStr
    password: Annotated[str, StringConstraints(min_length=3, max_length=64)]
    first_name: Annotated[str, StringConstraints(min_length=3, max_length=30)]
    last_name: Annotated[str, StringConstraints(min_length=3, max_length=30)]
    model_config = ConfigDict(from_attributes=True)

class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Schema to structure token data"""

    id: Optional[str]

# class UserResponse(BaseModel):
#     id: str
#     email: EmailStr
#     first_name: Optional[str] = None
#     last_name: Optional[str] = None
#     avatar_url: Optional[str] = None