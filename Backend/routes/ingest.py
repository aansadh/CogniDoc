"""
Routes for handling file ingestion in the Smart PDF QA API application.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from core.dependencies import (
    validate_session,
    get_file_services,
)
from models.models import TextModel
from services.file_services import FileServices
from utils.logger import log_duration
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
# auth_method: 'clerk'


@router.post("/upload-text")
@log_duration
async def uploadText(
    text: TextModel,
    session_id: str = Depends(validate_session),
    file_services: FileServices = Depends(get_file_services),
):
    """
    Uploads text content and processes it.

    Args:
        text (TextModel): The text content to upload.
        session_id (str): The session ID.
        file_services (FileServices): The file services instance.

    Returns:
        dict: A response containing the file ID and session ID.

    Raises:
        HTTPException: If the text content is empty.
    """
    logger.debug(f"Uploading text content: session_id={session_id}, file_name={text.file_name}")
    if not text.text.strip():
        logger.warning("Text content is empty. Raising HTTPException.")
        raise HTTPException(status_code=400, detail="Text content cannot be empty.")

    try:
        file_id = await file_services.process_content_upload(
            session_id=session_id,
            content=text.text.strip(),
            file_name=text.file_name,
        )

        logger.info(f"Text content uploaded successfully: file_id={file_id}, session_id={session_id}")
        return {
            "message": "File uploaded and processed successfully.",
            "file_id": file_id,
            "session_id": session_id,
        }
    except Exception as e:
        logger.error(f"Failed to upload text content: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to upload text content.")


@router.post("/upload-pdf")
@log_duration
async def upload_pdf(
    file: UploadFile = File(...),
    session_id: str = Depends(validate_session),
    file_services: FileServices = Depends(get_file_services),
):
    """
    Uploads a PDF file and processes it.

    Args:
        file (UploadFile): The PDF file to upload.
        session_id (str): The session ID.
        file_services (FileServices): The file services instance.

    Returns:
        dict: A response containing the file ID and session ID.

    Raises:
        HTTPException: If the file is not a valid PDF.
    """
    logger.debug(f"Uploading PDF file: session_id={session_id}, file_name={file.filename}")
    if file.content_type != "application/pdf":
        logger.warning("Invalid file type. Raising HTTPException.")
        raise HTTPException(status_code=400, detail="Please upload a valid PDF file.")

    try:
        raw_content = await file.read()
        file_id = await file_services.process_file_upload(
            session_id=session_id,
            content=raw_content,
            file_name=file.filename,
        )

        logger.info(f"PDF file uploaded successfully: file_id={file_id}, session_id={session_id}")
        return {
            "message": "PDF uploaded and processed successfully.",
            "file_id": file_id,
            "session_id": session_id,
        }
    except Exception as e:
        logger.error(f"Failed to upload PDF file: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to upload PDF file.")


