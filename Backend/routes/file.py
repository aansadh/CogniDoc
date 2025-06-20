from fastapi import APIRouter, Depends, HTTPException
from core.dependencies import get_db, validate_session
from repositories.file_repository import FileRepository

router = APIRouter()

@router.get('/')
async def get_all_files(session_id: str=Depends(validate_session), db=Depends(get_db)):
    """
    Retrieve all files associated with the current session.
    """
    files = await FileRepository(db).get_files_by_session(session_id)
    return {
        "message": "Files retrieved successfully.",
        "payload": files
    }