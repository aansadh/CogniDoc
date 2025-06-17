from fastapi import HTTPException, APIRouter, Depends
from rag.pipeline import process_query
from models.models import QueryModel
from core.dependencies import get_vectorstore, validate_session
from utils.logger import log_timing
from fastapi.concurrency import run_in_threadpool
from rag.exceptions import ContextNotFoundError

router = APIRouter()

@router.post('/askQuery')
@log_timing
async def ask_query_endpoint(
    query: QueryModel,
    session_id: str=Depends(validate_session),
    vectorstore=Depends(get_vectorstore)
):  
    try:
        filter = {"session_id": session_id}
        response = await run_in_threadpool(process_query, query.query, filter, vectorstore)

        return response
    
    except ContextNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))