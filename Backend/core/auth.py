"""
Authentication utilities for validating user and session access.
"""

from fastapi import Request, HTTPException

def clerk_only(request: Request):
    """
    Validates that the request is authenticated via Clerk.

    Args:
        request (Request): The incoming HTTP request.

    Returns:
        str: The user ID of the authenticated Clerk user.

    Raises:
        HTTPException: If the authentication method is not Clerk.
    """
    if getattr(request.state, "auth_method", None) != "clerk":
        raise HTTPException(status_code=403, detail="Only Clerk-authenticated users allowed")
    return request.state.user_id 

def token_only(request: Request):
    """
    Validates that the request is authenticated via token.

    Args:
        request (Request): The incoming HTTP request.

    Returns:
        str: The session ID of the authenticated token session.

    Raises:
        HTTPException: If the authentication method is not token.
    """
    if getattr(request.state, "auth_method", None) != "token":
        raise HTTPException(status_code=403, detail="Only token-authenticated sessions allowed")
    return request.state.session_id