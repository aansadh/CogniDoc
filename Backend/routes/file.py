from fastapi import APIRouter, Depends, HTTPException
from core.dependencies import get_db, validate_session

router = APIRouter()

@router.get('/')
async def get_all_files(session_id: str=Depends(validate_session), db=Depends(get_db)):
    """
    Retrieve all files associated with the current session.
    """
    try:
        files = await db["Files"].find({"session_id": session_id}).to_list(length=None)
        if not files:
            raise HTTPException(status_code=404, detail="No files found for this session.")
        return files
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve files. Error: {str(e)}")