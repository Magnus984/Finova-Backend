from fastapi import FastAPI, status
from api.core.config import settings
from fastapi.middleware.cors import CORSMiddleware
import logging
from logging.handlers import RotatingFileHandler
from api.v1.schemas.response_models import (
    StandardResponse, SuccessResponse
)
from starlette.requests import Request
import uvicorn
from api.db.database import init_db


LOG_FILE = "uvicorn.log"
uvicorn_logger = logging.getLogger("uvicorn")
file_handler = RotatingFileHandler(LOG_FILE, maxBytes=10485760, backupCount=5)
file_handler.setFormatter(
    logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )
uvicorn_logger.addHandler(file_handler)

# Initialize the database
init_db()

app = FastAPI(
    title=settings.PROJECT_TITLE,
    description="",
    version="1.0.0",
    docs_url="/docs"
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/",
         tags=["Home"],
         response_model=StandardResponse,
         responses={
             200: {
                 "model": StandardResponse,
                 "description": "Welcome response"
             }
         })



async def get_root(request: Request) -> dict:
    """
    Root endpoint for the API
    
    Returns:
        Standardized success response with welcome message
    """
    success_response = SuccessResponse(
        status_code=status.HTTP_200_OK,
        message="Welcome to Finova Backend",
        data={}
    )
    return success_response

@app.get("/probe",
         tags=["Home"],
         response_model=StandardResponse,
         responses={
             200: {
                 "model": StandardResponse,
                 "description": "API probe response"
             }
         })
async def probe():
    """
    Probe endpoint to check if the API is running
    
    Returns:
        Standardized success response confirming API is running
    """
    success_response = SuccessResponse(
        status_code=status.HTTP_200_OK,
        message="I am the Python FastAPI API responding",
        data={}
    )
    return success_response


@app.get("/health",
         tags=["Home"],
         response_model=StandardResponse,
         responses={
             200: {
                 "model": StandardResponse,
                 "description": "Health check response"
             }
         })
async def health_check():
    """
    Health check endpoint for monitoring
    
    Returns:
        Standardized success response with health status
    """
    success_response = SuccessResponse(
        status_code=status.HTTP_200_OK,
        message="Health check successful",
        data={"status": "healthy"}
    )
    return success_response


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )