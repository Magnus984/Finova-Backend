from fastapi import (
    APIRouter, HTTPException, status, Request, BackgroundTasks
)
from fastapi.responses import RedirectResponse
from api.core.config import settings
import secrets
from urllib.parse import urlencode
from api.v1.schemas.response_models import (
    SuccessResponse, ErrorResponse, ErrorData
)
import requests
from api.v1.services.user import user_service
from api.utils.logger import logger
from api.v1.services.google_auth import google_auth_service
import asyncio
from datetime import timedelta

google_auth = APIRouter(prefix="/auth", tags=["Google Authentication"])

@google_auth.get(
        "/google/initiate",
        response_model=SuccessResponse
                 )
async def initiate_google_auth():
    """
    Robust Google OAuth flow initiation with strict parameter handling
    """
    try:
        # Retrieve and validate client ID
        client_id = settings.GOOGLE_CLIENT_ID
        if not client_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Google Client ID is not configured"
                )
        
        # Get redirect URI
        print(f"Redirect URI: {settings.NGROK_REDIRECT_URI}")
        logger.info(f"Redirect URI: {settings.NGROK_REDIRECT_URI}")
        redirect_uri = settings.NGROK_REDIRECT_URI
        if not redirect_uri:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Redirect URI is not configured"
                )
        
        # Generate state for CSRF protection
        state = secrets.token_urlsafe(16) + ":local"

        # Construct OAuth parameters carefully
        params = {
            'client_id': client_id,
            'redirect_uri': redirect_uri,
            'response_type': 'code',
            'scope': 'openid email profile',
            'state': state,
            'access_type': 'offline'
        }

        # Construct the Google OAuth URL
        base_url = "https://accounts.google.com/o/oauth2/v2/auth"
        query_string = urlencode(params)
        auth_url = f"{base_url}?{query_string}"

        # return RedirectResponse(url=auth_url, status_code=302)
        return {
                "status_code": status.HTTP_200_OK,
                "status": "success",
                "message": "Google OAuth URL generated",
                "data": {
                    "auth_url": auth_url,
                    "state": state,
                    "redirect_uri": redirect_uri
                }
            }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OAuth initiation failed: {str(e)}"
            )
    

@google_auth.get("/google/callback")
async def google_callback(
    request: Request,
    background_tasks: BackgroundTasks,
    ):
    """Google OAuth callback endpoint
    """
    # Extract the authorization code and state from the request
    query_params = dict(request.query_params)
    code = query_params.get("code")
    state = query_params.get("state", "")

    if not code:
        error_response = ErrorResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Invalid request",
            data=ErrorData(
                error="Authorization code is missing",
                error_type="validation_error"),
        )
        return error_response
    
    try:
        # Exchange the authorization code for an access token
        token_url = "https://oauth2.googleapis.com/token"
        token_response = requests.post(
            token_url,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": settings.NGROK_REDIRECT_URI,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
            },
        )

        if token_response.status_code != 200:
            error_response = ErrorResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Authentication failed",
                data=ErrorData(
                    error="Failed to exchange authorization code",
                    error_type="auth_error"),
            )
            return error_response

        token_data = token_response.json()
        id_token = token_data.get("id_token")

        # Validate the ID token
        profile_endpoint = f"https://www.googleapis.com/oauth2/v3/tokeninfo?id_token={id_token}"
        profile_response = requests.get(profile_endpoint)
        logger.info(f"Profile response: {profile_response.json()}")
        if profile_response.status_code != 200:
            return error_response(message="Authentication failed",
                                  data=ErrorData(error="Invalid ID token",
                                                 error_type="auth_error"),
                                  status_code=status.HTTP_400_BAD_REQUEST)

        profile_data = profile_response.json()
        email = profile_data.get('email')

        # Fallback for email if needed
        if not email and "sub" in profile_data:
            email = f"{profile_data['sub']}@placeholder.google.com"

        user = user_service.get_user_by_email(email=email)
        
        is_new_user = False

        if not user:
            # Create a new user if not found
            logger.info("Creating new user")
            user = google_auth_service.create_new_user(profile_data)
            logger.info(f"New user created: {user}")
            is_new_user = True
            logger.info(f"New user created: {user.email}")

        # Generate tokens for the user
        tokens = google_auth_service.generate_tokens(user)
        access_token = tokens.access_token
        refresh_token = tokens.refresh_token

        frontend_url = "https://2f00-102-208-89-6.ngrok-free.app/home"

        redirect_url = (
            f"{frontend_url}?auth_success=true&access_token={access_token}&id_token={id_token}"
        )

        # Create response with the redirect
        response = RedirectResponse(url=redirect_url, status_code=302)

        # Store refresh token and ID token in cookies
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            expires=timedelta(days=30),
            httponly=True,
            secure=True,
            samesite="none",
        )

        # store access token in cookies
        response.set_cookie(
            key="access_token",
            value=access_token,
            expires=timedelta(hours=1),
            httponly=True,
            secure=True,
            samesite="none",
        )
        
        response.set_cookie(
            key="id_token",
            value=id_token,
            expires=timedelta(hours=1),
            httponly=True,
            secure=True,
            samesite="none",
        )

        if is_new_user:
            await asyncio.sleep(0.5)

        return response

    except Exception as e:
        # Log the exception for debugging
        logger.error(f"Google callback error: {str(e)}", exc_info=True)


        