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
    session_id = await session_services.create_session(user_id=user_id)
    return {"session_id": session_id}


@router.delete("/delete-session")
@log_duration
async def delete_session(
    session_id: str = Depends(validate_session),
    session_services: SessionServices = Depends(get_session_services),
):
    await session_services.delete_session(session_id=session_id)
    return {"message": "Session deleted successfully."}


@router.get("/get-sessions", response_model=[SessionModel])
@log_duration
async def get_sessions(user_id: str = Depends(get_user_id), db=Depends(get_db)):
    return await SessionRepository(db).get_sessions_by_user_id(user_id)
