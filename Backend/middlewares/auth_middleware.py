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
    def __init__(self, app):
        super().__init__(app)
        self.exempt_paths = ["/docs", "/redoc", "/openapi.json", "/favicon.ico"]
        self.clerk = Clerk(bearer_auth=settings.clerk_secret_key)

    async def dispatch(self, request: Request, call_next):
        if request.url.path in self.exempt_paths:
            return await call_next(request)
        if await self._handle_clerk_auth(request):
            return await call_next(request)
        if await self._handle_token_auth(request):
            return await call_next(request)

        return JSONResponse(status_code=401, content={"error": "Invalid Session or Token"})

    def _get_token_from_request(self, request: Request):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None
        return auth_header.split(" ")[1]

    async def _handle_clerk_auth(self, request: Request):
        user_id, session_id = self._verify_clerk_token(request), request.headers.get('Session-ID')
        if user_id:
            request.state.auth_method = "clerk"
            request.state.user_id = user_id
            if session_id and await self._owns_session(session_id, user_id, request.app.state.db):
                request.state.session_id = session_id
            else:
                request.state.session_id = None
            return True
        return False

    async def _handle_token_auth(self, request: Request):
        token = self._get_token_from_request(request)
        if not token:
            return False
        session_id, user_id = self._verify_jwt(token)
        if session_id and await self._owns_session(session_id, user_id, request.app.state.db):
            request.state.auth_method = "token"
            request.state.session_id = session_id
            request.state.user_id = user_id
            return True
        return False

    def _verify_clerk_token(self, request: Request):
        try:
            request_state = self.clerk.authenticate_request(
                request,
                AuthenticateRequestOptions()
            )

            if request_state.is_signed_in:
                return request_state.payload.get("sub") or request_state.payload.get("user_id")
            return None

        except Exception:
            return None

    def _verify_jwt(self, token: str):
        try:
            payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
            return payload.get('session_id'), payload.get('user_id')
        except JWTError:
            return None, None
    
    async def _owns_session(self, session_id: str, user_id: str, db=None):
        session = await db['Sessions'].find_one({"user_id": user_id, "_id": ObjectId(session_id)})
        return session_id if session else None