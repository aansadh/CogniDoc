from fastapi import APIRouter, HTTPException, Depends, Request
from datetime import datetime, timezone
from models.models import SessionModel
from core.dependencies import get_db, get_vectorstore, validate_session
from utils.vectorstore_utils import delete_doc_from_vectorstore_async
from utils.logger import log_timing
from utils.db_ops import delete_file_from_db, delete_session_from_db

router = APIRouter()
# auth_method: 'clerk'

@router.post("/new-session")
@log_timing
async def create_session(request: Request, db=Depends(get_db)):
    try:
        user_id = getattr(request.state, 'user_id', None)
        created_at = datetime.now(timezone.utc)
        session = SessionModel(user_id=user_id, created_at=created_at)

        session_data = session.model_dump()
        del session_data["session_id"]
        response = await db["Sessions"].insert_one(session_data)
        if not response or not response.acknowledged or not response.inserted_id:
            raise
        
        session.session_id = str(response.inserted_id)
        return session
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create session. Error: {e}")


@router.delete("/delete-session")
@log_timing
async def delete_session(
    session_id: str=Depends(validate_session), 
    db=Depends(get_db),
    vectorstore=Depends(get_vectorstore)
):
    ##### Future consideration: Implement transactional delete to make this atomic.
    try:
        await delete_doc_from_vectorstore_async(session_id=session_id, vectorstore=vectorstore)
        await delete_file_from_db(session_id=session_id, db=db)
        await delete_session_from_db(session_id=session_id, db=db)

        return {"message": "Session deleted successfully"}
    except Exception as e:
        print(f"Error deleting session: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete session. Error: {e}")