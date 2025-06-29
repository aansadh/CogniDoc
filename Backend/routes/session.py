"""
Routes for handling session-related operations in the Smart PDF QA API application.
"""

from fastapi import APIRouter, Depends
from models.db_models import SessionModel
from core.dependencies import (
    validate_session,
    get_user_id,
    get_session_services,
    get_db,
)
from utils.logger import log_duration
from repositories.session_repository import SessionRepository
from services.session_services import SessionServices

router = APIRouter()
# auth_method: 'clerk'


@router.post("/new-session")
@log_duration
async def create_session(
    user_id: str = Depends(get_user_id),
    session_services: SessionServices = Depends(get_session_services),
):
    """
    Creates a new session for the user.

    Args:
        user_id (str): The user ID.
        session_services (SessionServices): The session services instance.

    Returns:
        dict: A response containing the session ID.
    """
    session_id = await session_services.create_session(user_id=user_id)
    return {"session_id": session_id}


@router.delete("/delete-session")
@log_duration
async def delete_session(
    session_id: str = Depends(validate_session),
    session_services: SessionServices = Depends(get_session_services),
):
    """
    Deletes a session by its ID.

    Args:
        session_id (str): The session ID.
        session_services (SessionServices): The session services instance.

    Returns:
        dict: A response confirming the deletion.
    """
    await session_services.delete_session(session_id=session_id)
    return {"message": "Session deleted successfully."}


@router.get("/get-sessions", response_model=list[SessionModel])
@log_duration
async def get_sessions(user_id: str = Depends(get_user_id), db=Depends(get_db)):
    """
    Retrieves all sessions associated with the user.

    Args:
        user_id (str): The user ID.
        db: The database connection instance.

    Returns:
        list: A list of sessions associated with the user.
    """
    return await SessionRepository(db).get_sessions_by_user_id(user_id)
