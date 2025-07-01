"""
Routes for handling session-related operations in the Smart PDF QA API application.
"""

from fastapi import APIRouter, Depends, HTTPException
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
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
# auth_method: 'clerk'


@router.post("/new-session")
@log_duration
async def create_session(
    session_name: str,
    user_id: str = Depends(get_user_id),
    session_services: SessionServices = Depends(get_session_services),
):
    logger.debug(f"Creating new session: user_id={user_id}, session_name={session_name}")
    try:
        session_id = await session_services.create_session(user_id=user_id, session_name=session_name)
        logger.info(f"Session created successfully: session_id={session_id}")
        return {"session_id": session_id}
    except Exception as e:
        logger.error(f"Failed to create session: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create session.")


@router.delete("/delete-session")
@log_duration
async def delete_session(
    session_id: str = Depends(validate_session),
    session_services: SessionServices = Depends(get_session_services),
):
    logger.debug(f"Deleting session: session_id={session_id}")
    try:
        await session_services.delete_session(session_id=session_id)
        logger.info(f"Session deleted successfully: session_id={session_id}")
        return {"message": "Session deleted successfully."}
    except Exception as e:
        logger.error(f"Failed to delete session: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to delete session.")


@router.get("/get-sessions", response_model=list[SessionModel])
@log_duration
async def get_sessions(user_id: str = Depends(get_user_id), db=Depends(get_db)):
    logger.debug(f"Retrieving sessions for user_id={user_id}")
    try:
        sessions = await SessionRepository(db).get_sessions_by_user_id(user_id)
        logger.info(f"Retrieved {len(sessions)} sessions for user_id={user_id}")
        return sessions
    except Exception as e:
        logger.error(f"Failed to retrieve sessions for user_id={user_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve sessions.")


@router.get("/get-session", response_model=SessionModel)
@log_duration
async def get_session(
    session_id: str = Depends(validate_session),
    session_services: SessionServices = Depends(get_session_services),
):
    logger.debug(f"Retrieving session: session_id={session_id}")
    try:
        session = await session_services.get_session(session_id=session_id)
        logger.info(f"Session retrieved successfully: session_id={session_id}")
        return session
    except Exception as e:
        logger.error(f"Failed to retrieve session: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve session.")