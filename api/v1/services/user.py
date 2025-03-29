from mongoengine.errors import DoesNotExist, ValidationError
from api.utils.logger import logger
from api.v1.schemas.response_models import ErrorResponse, ErrorData
from api.v1.models.user import User
import datetime as dt
import jwt
from fastapi import HTTPException, Depends
from api.v1.schemas.user import UserCreate, TokenData
from api.core.config import settings
import random
from datetime import datetime, timedelta, timezone
import string
from passlib.context import CryptContext
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

oauth2_scheme = HTTPBearer()

class OptionalHTTPBearer(HTTPBearer):
    def __init__(self, auto_error: bool = False):
        super().__init__(auto_error=auto_error)


oauth2_scheme_optional = OptionalHTTPBearer(auto_error=False)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    """Handles database operations for user management"""
    def authenticate_user(self, email: str, password: str):
        """
        Authenticate a user with email and password
        
        Args:
            email: User's email address
            password: User's password
            
        Returns:
            User: Authenticated user object or ErrorResponse if authentication fails
        """
        try:
            # Find user by email using mongoengine
            user = User.objects.get(email=email)
            
            # Verify password
            if not self.verify_password(password, user.password):
                logger.error(f"Invalid password for user: {email}")
                raise HTTPException(
                    status_code=400,
                    detail="Invalid credentials"
                )
            

            # Update last login timestamp
            user.last_login = datetime.now(timezone.utc)
            user.save()

            # Generate access and refresh tokens
            access_token = self.create_access_token(user_id=user.id)
            refresh_token = self.create_refresh_token(user_id=user.id)
            
            logger.info(f"User authenticated successfully: {email}")
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
            }

        except DoesNotExist:
            logger.error(f"User not found with email: {email}")
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )
        except Exception as e:
            logger.error(f"Error authenticating user: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Internal server error"
            )

    def hash_password(self, password: str) -> str:
        """Function to hash a password"""

        hashed_password = pwd_context.hash(secret=password)
        return hashed_password
    

    def verify_password(self, password: str, hash: str) -> bool:
        """Function to verify a hashed password"""

        return pwd_context.verify(secret=password, hash=hash)
    
    def get_user_by_id(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except DoesNotExist:
            logger.error(f"User not found with id: {user_id}")
            return ErrorResponse(
                status_code=404,
                message="User not found",
                data=ErrorData(error="User does not exist", error_type="DoesNotExist")
            )
        except Exception as e:
            logger.error(f"Error retrieving user: {str(e)}")
            return ErrorResponse(
                status_code=500,
                message="Failed to retrieve user",
                data=ErrorData(error=str(e), error_type=type(e).__name__)
            )

    def create(self, user_data: UserCreate) -> User:
        """Creates a new user"""
        try:
            # Check if user exists
            existing_user = User.objects.filter(email=user_data.email).first()
            if existing_user:
                logger.error(f"User already exists with email: {user_data.email}")
                raise HTTPException(
                    status_code=400,
                    detail="User with this email already exists"
                )

            # Create new user
            new_user = User(
                email=user_data.email,
                password=self.hash_password(user_data.password),
                first_name=user_data.first_name,
                last_name=user_data.last_name
            )
            new_user.save()
            
            logger.info(f"Created new user: {new_user.email}")
            return new_user

        except ValidationError as e:
            logger.error(f"Validation error: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            raise HTTPException(status_code=500, detail="Could not create user")

    def update_user(self, user_id, user_data):
        try:
            user = User.objects.get(id=user_id)
            user.update(**user_data)
            user.reload()
            return user
        except DoesNotExist:
            logger.error(f"User not found with id: {user_id}")
            return ErrorResponse(
                status_code=404,
                message="User not found",
                data=ErrorData(error="User does not exist", error_type="DoesNotExist")
            )
        except Exception as e:
            logger.error(f"Error updating user: {str(e)}")
            return ErrorResponse(
                status_code=500,
                message="Failed to update user",
                data=ErrorData(error=str(e), error_type=type(e).__name__)
            )

    def delete_user(self, user_id):
        try:
            user = User.objects.get(id=user_id)
            user.delete()
            return {"message": "User deleted successfully"}
        except DoesNotExist:
            logger.error(f"User not found with id: {user_id}")
            return ErrorResponse(
                status_code=404,
                message="User not found",
                data=ErrorData(error="User does not exist", error_type="DoesNotExist")
            )
        except Exception as e:
            logger.error(f"Error deleting user: {str(e)}")
            return ErrorResponse(
                status_code=500,
                message="Failed to delete user",
                data=ErrorData(error=str(e), error_type=type(e).__name__)
            )

    def get_all_users(self):
        try:
            return User.objects.all()
        except Exception as e:
            logger.error(f"Error retrieving users: {str(e)}")
            return ErrorResponse(
                status_code=500,
                message="Failed to retrieve users",
                data=ErrorData(error=str(e), error_type=type(e).__name__)
            )

    def get_user_by_email(self, email):
        try:
            return User.objects.get(email=email)
        except DoesNotExist:
            logger.error(f"User not found with email: {email}")
            return None
        except Exception as e:
            logger.error(f"Error retrieving user: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to retrieve user"
            )

        
    def create_access_token(self, user_id: str) -> str:
        """Create JWT access token"""
        logger.info(f"Creating access token for user_id: {user_id}")
        try:
            expires = dt.datetime.now(dt.timezone.utc) + dt.timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
            payload = {
                "user_id": str(user_id),
                "exp": expires,
                "type": "access",
                "iat": dt.datetime.now(dt.timezone.utc)
            }
            return jwt.encode(
                payload, 
                settings.SECRET_KEY, 
                algorithm=settings.ALGORITHM
            )
        except Exception as e:
            logger.error(f"Error creating access token: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Could not create access token"
            )

    def create_refresh_token(self, user_id: str) -> str:
        """Create JWT refresh token"""
        try:
            expires = dt.datetime.now(dt.timezone.utc) + dt.timedelta(
                days=settings.REFRESH_TOKEN_EXPIRE_MINUTES
            )
            payload = {
                "user_id": str(user_id),
                "exp": expires,
                "type": "refresh",
                "iat": dt.datetime.now(dt.timezone.utc)
            }
            return jwt.encode(
                payload, 
                settings.SECRET_KEY, 
                algorithm=settings.ALGORITHM
            )
        except Exception as e:
            logger.error(f"Error creating refresh token: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Could not create refresh token"
            )

    def verify_access_token(self, access_token: str, credentials_exception) -> TokenData:
        """Verify and decode JWT access token"""
        try:
            payload = jwt.decode(
                access_token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            
            user_id = payload.get("user_id")
            token_type = payload.get("type")

            if not user_id:
                logger.error("Token missing user_id")
                raise credentials_exception
            
            if token_type != "access":
                logger.error("Invalid token type")
                raise HTTPException(
                    status_code=400,
                    detail="Invalid token type - access token required"
                )

            return TokenData(id=user_id)

        except jwt.ExpiredSignatureError:
            logger.error("Token has expired")
            raise HTTPException(
                status_code=401,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid token: {str(e)}")
            raise credentials_exception

    def verify_refresh_token(self, refresh_token: str, credentials_exception) -> TokenData:
        """Verify and decode JWT refresh token"""
        try:
            payload = jwt.decode(
                refresh_token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            
            user_id = payload.get("user_id")
            token_type = payload.get("type")

            if not user_id:
                logger.error("Token missing user_id")
                raise credentials_exception
            
            if token_type != "refresh":
                logger.error("Invalid token type")
                raise HTTPException(
                    status_code=400,
                    detail="Invalid token type - refresh token required"
                )

            return TokenData(id=user_id)

        except jwt.ExpiredSignatureError:
            logger.error("Token has expired")
            raise HTTPException(
                status_code=401,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid token: {str(e)}")
            raise credentials_exception

    def generate_token(self) -> tuple[str, datetime]:
        """
        Generate a 6-digit verification token with 10-minute expiration
        
        Returns:
            tuple[str, datetime]: A tuple containing (token, expiration_time)
        """
        try:
            token = "".join(random.choices(string.digits, k=6))
            expiry = datetime.now(timezone.utc) + timedelta(minutes=10)
            return token, expiry
        except Exception as e:
            logger.error(f"Error generating token: {str(e)}")
            return ErrorResponse(
                status_code=500,
                message="Failed to generate token",
                data=ErrorData(error=str(e), error_type=type(e).__name__)
            )
        
    def get_current_user(
        self,
        auth: HTTPAuthorizationCredentials = Depends(oauth2_scheme)
    ) -> User:
        """
        Get current logged in user from JWT token
        
        Args:
            auth: HTTP Authorization credentials containing JWT token
            
        Returns:
            User: Current authenticated user
            
        Raises:
            HTTPException: If credentials are invalid or user not found
        """
        credentials_exception = HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            # Verify the access token
            token = self.verify_access_token(auth.credentials, credentials_exception)
            
            # Get user from database
            user = User.objects.get(id=token.id)
            
            # Update last login
            user.last_login = datetime.now(timezone.utc)
            user.save()
            
            return user

        except DoesNotExist:
            logger.error(f"User not found with id: {token.id if token else 'unknown'}")
            raise credentials_exception
        except Exception as e:
            logger.error(f"Error getting current user: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=str(e),
            )

# Initialize service instance
user_service = UserService()