from .ai_analysis import router as ai_router
from fastapi import APIRouter

# Create a main router that includes all sub-routers
router = APIRouter()

# Import sub-routers

# Include sub-routers
router.include_router(ai_router, prefix="/ai", tags=["AI Financial Analysis"])
