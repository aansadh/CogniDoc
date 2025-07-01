"""
Middleware for handling authentication in the Smart PDF QA API application.
"""

from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from fastapi.responses import JSONResponse
from clerk_backend_api import Clerk
from clerk_backend_api.security.types import AuthenticateRequestOptions
from jose import jwt, JWTError
from bson.objectid import ObjectId
from core.config import settings
import logging

# consider indexing session_id and user_id in the database for faster lookups

logger = logging.getLogger(__name__)

class AuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware for authenticating requests using Clerk or JWT tokens.

    Attributes:
        app: The FastAPI application instance.
        exempt_paths (list): Paths that are exempt from authentication.
        clerk (Clerk): The Clerk authentication instance.
    """

    def __init__(self, app):
        """
        Initializes the AuthMiddleware instance.

        Args:
            app: The FastAPI application instance.
        """
        super().__init__(app)
        self.exempt_paths = ["/docs", "/redoc", "/openapi.json", "/favicon.ico"]
        self.clerk = Clerk(bearer_auth=settings.clerk_secret_key)

    async def dispatch(self, request: Request, call_next):
        """
        Dispatches the request through the middleware.

        Args:
            request (Request): The incoming HTTP request.
            call_next: The next middleware or route handler.

        Returns:
            Response: The HTTP response.
        """
        logger.info(f"Dispatching request to {request.url.path}")
        if request.method == "OPTIONS":
            logger.info("Handling CORS preflight request")
            return await call_next(request)
        if request.url.path in self.exempt_paths:
            logger.info(f"Request to {request.url.path} is exempt from authentication")
            return await call_next(request)
        if await self._handle_clerk_auth(request):
            logger.info("Clerk authentication successful")
            return await call_next(request)
        if await self._handle_token_auth(request):
            logger.info("Token authentication successful")
            return await call_next(request)

        logger.warning("Authentication failed: Invalid Session or Token")
        return JSONResponse(status_code=401, content={"error": "Invalid Session or Token"})

    def _get_token_from_request(self, request: Request):
        """
        Extracts the token from the Authorization header.

        Args:
            request (Request): The incoming HTTP request.

        Returns:
            str: The extracted token, or None if not present.
        """
        logger.debug("Extracting token from Authorization header")
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            logger.warning("Authorization header missing or invalid")
            return None
        return auth_header.split(" ")[1]

    async def _handle_clerk_auth(self, request: Request):
        """
        Handles authentication using Clerk.

        Args:
            request (Request): The incoming HTTP request.

        Returns:
            bool: True if authentication is successful, False otherwise.
        """
        logger.debug("Handling Clerk authentication")
        user_id, session_id = self._verify_clerk_token(request), request.headers.get('Session-ID')
        if user_id:
            logger.info(f"Clerk authentication successful for user_id: {user_id}")
            request.state.auth_method = "clerk"
            request.state.user_id = user_id
            if session_id and await self._owns_session(session_id, user_id, request.app.state.db):
                logger.info(f"Session ownership verified for session_id: {session_id}")
                request.state.session_id = session_id
            else:
                logger.warning("Session ownership verification failed")
                request.state.session_id = None
            return True
        logger.warning("Clerk authentication failed")
        return False

    async def _handle_token_auth(self, request: Request):
        """
        Handles authentication using JWT tokens.

        Args:
            request (Request): The incoming HTTP request.

        Returns:
            bool: True if authentication is successful, False otherwise.
        """
        logger.debug("Handling token authentication")
        token = self._get_token_from_request(request)
        if not token:
            logger.warning("Token missing in request")
            return False
        session_id, user_id = self._verify_jwt(token)
        if session_id and user_id and await self._owns_session(session_id, user_id, request.app.state.db):
            logger.info(f"Token authentication successful for user_id: {user_id}, session_id: {session_id}")
            request.state.auth_method = "token"
            request.state.session_id = session_id
            request.state.user_id = user_id
            return True
        logger.warning("Token authentication failed")
        return False

    def _verify_clerk_token(self, request: Request):
        """
        Verifies the Clerk token in the request.

        Args:
            request (Request): The incoming HTTP request.

        Returns:
            str: The user ID if verification is successful, None otherwise.
        """
        logger.debug("Verifying Clerk token")
        try:
            request_state = self.clerk.authenticate_request(
                request,
                AuthenticateRequestOptions()
            )

            if request_state.is_signed_in:
                logger.info("Clerk token verification successful")
                return request_state.payload.get("sub") or request_state.payload.get("user_id")
            logger.warning("Clerk token verification failed: User not signed in")
            return None

        except Exception as e:
            logger.error(f"Error during Clerk token verification: {e}")
            return None

    def _verify_jwt(self, token: str):
        """
        Verifies the JWT token.

        Args:
            token (str): The JWT token to verify.

        Returns:
            tuple: The session ID and user ID if verification is successful, (None, None) otherwise.
        """
        logger.debug("Verifying JWT token")
        try:
            payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
            logger.info("JWT token verification successful")
            return payload.get('session_id'), payload.get('user_id')
        except JWTError as e:
            logger.error(f"JWT token verification failed: {e}")
            return None, None

    async def _owns_session(self, session_id: str, user_id: str, db=None):
        """
        Checks if the session belongs to the user.

        Args:
            session_id (str): The session ID.
            user_id (str): The user ID.
            db: The database connection instance.

        Returns:
            str: The session ID if ownership is verified, None otherwise.
        """
        logger.debug(f"Verifying session ownership for session_id: {session_id}, user_id: {user_id}")
        session = await db['Sessions'].find_one({"user_id": user_id, "_id": ObjectId(session_id)})
        if session:
            logger.info("Session ownership verified")
            return session_id
        logger.warning("Session ownership verification failed")
        return None