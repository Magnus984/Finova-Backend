# Register user
from fastapi import APIRouter, Depends, HTTPException
from api.v1.schemas.response_models import (
    SuccessResponse, ErrorResponse, ErrorData
)
from api.v1.services.user import user_service
from api.v1.schemas.user import UserCreate, UserLogin
from api.utils.logger import logger
from api.core.config import settings
from api.v1.models.user import User

auth = APIRouter(prefix="/auth", tags=["Authentication"])

@auth.post(
    "/register",
    response_model=SuccessResponse,
    responses={
        400: {
            "model": ErrorResponse,
            "description": "Bad Request"
        },
        409: {
            "model": ErrorResponse,
            "description": "Conflict"
        }
    }
)
def register_user(
    user: UserCreate
) -> SuccessResponse:
    """
    Register a new user with the provided details.
    """
    try:
        # Create new user
        new_user = user_service.create(user)
        return SuccessResponse(
            status_code=201,
            message="User registered successfully",
            data={
                "id": new_user.id,
                "first_name": new_user.first_name,
                "last_name": new_user.last_name,
                "email": new_user.email,
                "avatar_url": new_user.avatar_url
            }
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error registering user: {str(e)}")
        return ErrorResponse(
            status_code=500,
            message="Failed to register user",
            data=ErrorData(error=str(e), error_type=type(e).__name__)
        )
@auth.post(
    "/login",
    response_model=SuccessResponse,
    responses={
        400: {
            "model": ErrorResponse,
            "description": "Bad Request"
        },
        401: {
            "model": ErrorResponse,
            "description": "Unauthorized"
        }
    }
)
def login_user(user_data: UserLogin) -> SuccessResponse:
    """
    Log in a user with the provided credentials.
    """
    try:
        # Validate user credentials
        auth_data = user_service.authenticate_user(
            email=user_data.email,
            password=user_data.password
        )
        print(auth_data)
        logger.info(f"User logged in: {auth_data}")
        return SuccessResponse(
            status_code=200,
            message="User logged in successfully",
            data=auth_data
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error logging in user: {str(e)}")
        return ErrorResponse(
            status_code=500,
            message="Failed to log in user",
            data=ErrorData(error=str(e), error_type=type(e).__name__)
        )

@auth.get(
    "/user/{user_id}",
    response_model=SuccessResponse
)
def get_user(
    user_id: str,
    current_user: User = Depends(user_service.get_current_user)
) -> SuccessResponse:
    """
    Retrieve user details by user ID.
    """
    try:
        # Get user by ID
        user = user_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )
        success_response = SuccessResponse(
            status_code=200,
            message="User retrieved successfully",
            data={
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "avatar_url": user.avatar_url
            }
        )
        return success_response

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error retrieving user: {str(e)}")
        return ErrorResponse(
            status_code=500,
            message="Failed to retrieve user",
            data=ErrorData(error=str(e), error_type=type(e).__name__)
        )

