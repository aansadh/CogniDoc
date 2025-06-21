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
    if not text.text.strip():
        raise HTTPException(status_code=400, detail="Text content cannot be empty.")

    file_id = await file_services.process_content_upload(
        session_id=session_id,
        content=text.text.strip(),
        file_name=text.file_name,
    )

    return {
        "message": "File uploaded and processed successfully.",
        "file_id": file_id,
        "session_id": session_id,
    }


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
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Please upload a valid PDF file.")

    raw_content = await file.read()
    file_id = await file_services.process_file_upload(
        session_id=session_id,
        content=raw_content,
        file_name=file.filename,
    )

    return {
        "message": "PDF uploaded and processed successfully.",
        "file_id": file_id,
        "session_id": session_id,
    }


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
    await file_services.process_file_deletion(session_id, file_id)

    return {"message": f"File ID:'{file_id}' deleted successfully."}
