from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from api.core.config import settings
import secrets
from urllib.parse import urlencode

google_auth = APIRouter(prefix="/auth", tags=["Authentication"])

@google_auth.get("/google/initiate")
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
        redirect_uri = settings.GOOGLE_REDIRECT_URI
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

        return RedirectResponse(url=auth_url, status_code=302)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OAuth initiation failed: {str(e)}"
            )

        