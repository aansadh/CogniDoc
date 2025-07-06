"""
Routes for handling query-related operations in the Smart PDF QA API application.
"""

from fastapi import HTTPException, APIRouter, Depends
from models.models import QueryModel
from core.dependencies import get_rag_services, validate_session
from utils.logger import log_duration
from fastapi.concurrency import run_in_threadpool
from rag.exceptions import ContextNotFoundError
import logging
from rag.services.rag_services import RagServices

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post('/askQuery')
@log_duration
async def ask_query_endpoint(
    query: QueryModel,
    session_id: str=Depends(validate_session),
    rag_services: RagServices=Depends(get_rag_services)
):  
    logger.debug(f"Processing query: session_id={session_id}, query={query.query}")
    try:
        filter = {"session_id": session_id}
        response = await rag_services.process_query(
            query=query.query,
            filter=filter,
            k=5
        )
        logger.info(f"Query processed successfully: session_id={session_id}")
        return response
    except ContextNotFoundError as e:
        logger.warning(f"Context not found for query: {e}")
        raise HTTPException(status_code=404, detail="Context not found.")
    except Exception as e:
        logger.error(f"Failed to process query: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to process query.")