from fastapi import HTTPException
from api.v1.models.user import User
from api.v1.schemas.google_auth import Tokens
from api.v1.services.user import user_service
from api.v1.schemas.response_models import ErrorResponse, ErrorData
from mongoengine.errors import ValidationError
from api.utils.logger import logger

class GoogleOauthServices:
    """Handles database operations for google oauth"""

    def create(self, google_response: dict):
        """Creates a user using information from google."""
        try:
            new_user = self.create_new_user(google_response)
            return new_user
        except Exception as e:
            logger.error(f"Error creating user with Google OAuth: {str(e)}")
            return ErrorResponse(
                status_code=500,
                message="Failed to create user",
                data=ErrorData(error=str(e), error_type=type(e).__name__)
            )

    def create_new_user(self, google_response: dict):
        """Creates a new user with Google OAuth data."""
        try:
            # Extract email and avatar_url with fallback options
            email = google_response.get("email")
            avatar_url = google_response.get(
                "picture",
                "https://media-hosting.imagekit.io//f74ce7da0fec4fbe/blank-profile-picture-973460_1280.png"
            )

            # Check nested email locations
            if not email:
                if "email" in google_response.get("payload", {}):
                    email = google_response["payload"]["email"]
                elif "emails" in google_response:
                    email = google_response["emails"][0]["value"]

            if not email:
                raise ValueError(f"Could not find email in Google response")

            # Create new user document
            new_user = User(
                first_name=google_response.get("given_name") 
                    or google_response.get("name", "").split()[0] 
                    if google_response.get("name") else "",
                last_name=google_response.get("family_name") 
                    or " ".join(google_response.get("name", "").split()[1:]) 
                    if google_response.get("name") and len(google_response.get("name", "").split()) > 1 
                    else "",
                email=email,
                avatar_url=avatar_url,
            )

            new_user.save()
            print(f"User created with ID: {new_user.id}")
            logger.info(f"User created with ID: {new_user.id}")
            return new_user

        except ValidationError as e:
            logger.error(f"Validation error while creating user: {str(e)}")
            return ErrorResponse(
                status_code=400,
                message="Invalid user data",
                data=ErrorData(error=str(e), error_type="ValidationError")
            )
        except Exception as e:
            logger.error(f"Error creating new user: {str(e)}")
            return ErrorResponse(
                status_code=500,
                message="Failed to create user",
                data=ErrorData(error=str(e), error_type=type(e).__name__)
            )

    def generate_tokens(self, user: User):
        """Generates access and refresh tokens for the user."""
        try:
            access_token = user_service.create_access_token(user.id)
            refresh_token = user_service.create_refresh_token(user.id)
            
            return Tokens(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
            )
        except Exception as e:
            logger.error(f"Error generating tokens: {str(e)}")
            return ErrorResponse(
                status_code=500,
                message="Failed to generate tokens",
                data=ErrorData(error=str(e), error_type=type(e).__name__)
            )

google_auth_service = GoogleOauthServices()