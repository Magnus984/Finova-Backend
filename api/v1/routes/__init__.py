from fastapi import APIRouter

api_version_one = APIRouter()

from .google_auth import google_auth
from .auth import auth
from .company import company

api_version_one.include_router(google_auth)
api_version_one.include_router(auth)
api_version_one.include_router(company)