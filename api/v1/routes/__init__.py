from fastapi import APIRouter

api_version_one = APIRouter()

from .google_auth import google_auth
from .auth import auth
from .company import company

api_version_one.include_router(google_auth)
api_version_one.include_router(auth)
api_version_one.include_router(company)
from .ai_analysis import router as ai_router
from fastapi import APIRouter

# Create a main router that includes all sub-routers
router = APIRouter()

# Import sub-routers

# Include sub-routers
router.include_router(ai_router, prefix="/ai", tags=["AI Financial Analysis"])
