from fastapi import APIRouter, Depends, HTTPException, Request
from jose import jwt
import time
from core.dependencies import validate_session
from dotenv import load_dotenv
from utils.logger import log_timing
from core.config import settings

load_dotenv(override=True)

router = APIRouter()
# auth_method: 'clerk'

JWT_SECRET = settings.jwt_secret
JWT_ALGORITHM = settings.jwt_algorithm

@router.post("/new-token")
@log_timing
async def create_token(
    request: Request,
    session_id: str=Depends(validate_session)
):  
    try:
        payload = {
            "session_id": session_id,
            "user_id": request.state.user_id,
            "iat": int(time.time()),
            "exp": int(time.time()) + (3600 * 24 * 60)  
        }

        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

        return {"token": token, "message": f"Create new token in {3600 * 24 * 60} seconds."}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating token: {str(e)}")
