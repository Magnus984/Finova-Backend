from mongoengine import connect
from api.core.config import settings
from api.utils.logger import logger
from pymongo.errors import ConnectionFailure
from api.v1.schemas.response_models import ErrorResponse, ErrorData


DB_HOST = settings.DB_HOST
DB_PORT = settings.DB_PORT
DB_NAME = settings.DB_NAME


def init_db() -> None:
    """Initialize MongoDB connection using mongoengine"""
    try:
        connect(
            db=DB_NAME,
            host=DB_HOST,
            port=DB_PORT
        )
        logger.info(f"Connected to MongoDB: {DB_NAME}")
    except ConnectionFailure as e:
        logger.error(f"Failed to connect to MongoDB: {DB_NAME}")
        error_response = ErrorResponse(
            status_code=500,
            message="Failed to connect to MongoDB",
            data=ErrorData(
                error=str(e),
                error_type="ConnectionFailure"
            )
        )
        return error_response
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {DB_NAME}")
        error_response = ErrorResponse(
            status_code=500,
            message="Failed to connect to MongoDB",
            data=ErrorData(
                error=str(e),
                error_type=type(e).__name__
            )
        )
        return error_response