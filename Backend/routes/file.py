"""
Routes for handling file-related operations in the Smart PDF QA API application.
"""

from fastapi import APIRouter, Depends, HTTPException
from core.dependencies import get_db, validate_session
from repositories.file_repository import FileRepository
from models.db_models import FileModel

router = APIRouter()

@router.get('/', response_model=list[FileModel])
async def get_all_files(session_id: str=Depends(validate_session), db=Depends(get_db)):
    """
    Retrieves all files associated with the current session.

    Args:
        session_id (str): The session ID.
        db: The database connection instance.

    Returns:
        dict: A response containing the retrieved files.
    """
    return await FileRepository(db).get_files_by_session_id(session_id=session_id)