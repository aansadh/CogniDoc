"""
Routes for handling file-related operations in the Smart PDF QA API application.
"""

from fastapi import APIRouter, Depends, HTTPException
from core.dependencies import get_db, validate_session, get_file_services
from repositories.file_repository import FileRepository
from models.db_models import FileModel
from typing import List
import logging
from services.file_services import FileServices
from utils.logger import log_duration

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get('/', response_model=List[dict])
async def get_all_files(session_id: str=Depends(validate_session), db=Depends(get_db)):
    """
    Retrieves all files associated with the current session.

    Args:
        session_id (str): The session ID.
        db: The database connection instance.

    Returns:
        dict: A response containing the retrieved files.
    """
    logger.debug(f"Retrieving all files for session_id={session_id}")
    try:
        files = await FileRepository(db).get_files_by_session_id(session_id=session_id)
        logger.info(f"Retrieved {len(files)} files for session_id={session_id}")
        return files
    except Exception as e:
        logger.error(f"Failed to retrieve files for session_id={session_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve files.")
    
@router.delete("/delete-file/{file_id}")
@log_duration
async def deleteFile(
    file_id: str,
    session_id: str = Depends(validate_session),
    file_services: FileServices = Depends(get_file_services),
):
    """
    Deletes a file by its ID.

    Args:
        file_id (str): The ID of the file to delete.
        session_id (str): The session ID.
        file_services (FileServices): The file services instance.

    Returns:
        dict: A response confirming the deletion.
    """
    logger.debug(f"Deleting file: file_id={file_id}, session_id={session_id}")
    try:
        await file_services.process_file_deletion(session_id, file_id)
        logger.info(f"File deleted successfully: file_id={file_id}, session_id={session_id}")
        return {"message": f"File ID:'{file_id}' deleted successfully."}
    except Exception as e:
        logger.error(f"Failed to delete file: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to delete file.")