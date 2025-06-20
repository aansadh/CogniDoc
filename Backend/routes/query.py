from fastapi import HTTPException, APIRouter, Depends
from rag.pipeline import process_query
from models.models import QueryModel
from core.dependencies import get_vectorstore, validate_session
from utils.logger import log_duration
from fastapi.concurrency import run_in_threadpool
from rag.exceptions import ContextNotFoundError

router = APIRouter()

@router.post('/askQuery')
@log_duration
async def ask_query_endpoint(
    query: QueryModel,
    session_id: str=Depends(validate_session),
    vectorstore=Depends(get_vectorstore)
):  
    filter = {"session_id": session_id}
    response = await run_in_threadpool(process_query, query.query, filter, vectorstore)

    return response