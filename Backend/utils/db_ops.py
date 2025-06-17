from fastapi import HTTPException
from models.models import FileModel
from bson.objectid import ObjectId
from typing import Optional

async def add_file_metadata_to_db(file_name: str, session_id: str, created_at, db):
    if not file_name or not session_id:
        raise HTTPException(status_code=400, detail="File name and session ID are required.")
    
    file_doc = FileModel(
        file_name=file_name,
        session_id=session_id,
        created_at=created_at,
    )

    result = await db["Files"].insert_one(file_doc.model_dump())

    if not result or not result.acknowledged or not result.inserted_id:
        raise HTTPException(status_code=500, detail="Failed to save file metadata in the database.")
    
    return str(result.inserted_id)


async def delete_file_from_db(
    session_id: str, 
    file_id: Optional[str] = None, 
    db=None
):
    if db is None or not session_id:
        raise HTTPException(status_code=400, detail="Session ID and db is required for deletion.")

    if file_id and session_id:
        result = await db["Files"].delete_one({"_id": ObjectId(file_id), "session_id": session_id})
    elif session_id:
        result = await db["Files"].delete_many({"session_id": session_id})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="File not found in the database.")
    
    return {"message": "File metadata deleted successfully."}

    
async def delete_session_from_db(
        session_id: str,
        db=None
):
    if db is None:
        raise HTTPException(status_code=400, detail="Database connection is required for session deletion.")
    
    try:
        result = await db["Sessions"].delete_one({"_id": ObjectId(session_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Session not found")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting session: {str(e)}")