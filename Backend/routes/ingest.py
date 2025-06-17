from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from core.dependencies import get_vectorstore, get_db, validate_session
from models.models import TextModel
from datetime import datetime, timezone
from services.file_processing import process_file_upload, process_file_deletion, process_content_upload
from utils.logger import log_timing

router = APIRouter()
# auth_method: 'clerk'

@router.post('/uploadText')
@log_timing
async def uploadText(text: TextModel, session_id: str=Depends(validate_session), db=Depends(get_db), vectorstore=Depends(get_vectorstore)):
    if not text.text.strip():
        raise HTTPException(status_code=400, detail="Text content cannot be empty.")

    file_id = await process_content_upload(
        session_id=session_id, 
        content=text.text.strip().encode(), 
        file_name=text.file_name, 
        created_at=text.created_at, 
        vectorstore=vectorstore, 
        db=db
    )

    return { "message": "File uploaded and processed successfully.", "file_id": file_id, "session_id": session_id }
    

@router.post('/uploadPdf')
@log_timing
async def upload_pdf(file: UploadFile = File(...), session_id: str=Depends(validate_session), db=Depends(get_db), vectorstore=Depends(get_vectorstore)):
    if file.content_type != 'application/pdf':
        raise HTTPException(status_code=400, detail="Please upload a valid PDF file.")

    raw_content = await file.read()
    file_id = await process_file_upload(
        session_id=session_id,
        content=raw_content,
        file_name=file.filename,
        created_at=datetime.now(timezone.utc),
        vectorstore=vectorstore,
        db=db
    )

    return {
        "message": "PDF uploaded and processed successfully.",
        "file_id": file_id,
        "session_id": session_id
    }


@router.delete('/deleteFile/{file_id}')
@log_timing
async def deleteFile(file_id: str, session_id: str=Depends(validate_session), db=Depends(get_db), vectorstore=Depends(get_vectorstore)):    
    await process_file_deletion(session_id, file_id, vectorstore, db)

    return {
        "message": f"File ID:'{file_id}' deleted successfully."
    }