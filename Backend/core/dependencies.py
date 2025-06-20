from fastapi import Request, FastAPI, HTTPException, Header, Depends
from fastapi.security import HTTPBearer
from typing import Optional
from langchain_chroma import Chroma
import os
from rag.embeddings.embeddings_store import get_embedding_model
from utils.logger import log_timing
from pymongo import AsyncMongoClient
from core.config import settings
import logging
from services.file_services import FileServices
from services.session_services import SessionServices

logger = logging.getLogger(__name__)

# This cannot be async as it only performs blocking operations
@log_timing
def init_vectorstore_sync(app: FastAPI):
    os.makedirs("chroma_db", exist_ok=True)
    embedding_model = get_embedding_model(
        settings.embedding_provider,
        settings.embedding_model
    )
    app.state.vectorstore = Chroma(persist_directory="chroma_db", embedding_function=embedding_model)
    logger.info("Vectorstore initialized successfully.")

@log_timing
async def init_mongodb_async(app: FastAPI):
    mongo_uri = settings.mongodb_uri
    mongodb_db = settings.mongodb_db
    app.state.mongo_client = AsyncMongoClient(mongo_uri)
    app.state.db = app.state.mongo_client[mongodb_db]
    logger.info(f"Connected to MongoDB at {mongo_uri}/{mongodb_db}")

def get_db(request: Request):
    if not hasattr(request.app.state, 'db') or request.app.state.db is None:
        raise RuntimeError("Database connection is not initialized.")
    return request.app.state.db

def get_vectorstore(request: Request) -> Chroma:
    if not hasattr(request.app.state, 'vectorstore') or request.app.state.vectorstore is None:
        raise RuntimeError("Vectorstore is not initialized. Set it using set_vectorstore() before accessing.")
    return request.app.state.vectorstore

async def validate_session(request: Request) -> str:
    if not request.state.session_id:
        raise HTTPException(status_code=401, detail="Valid Session ID is required")
    return request.state.session_id

bearer_scheme = HTTPBearer(auto_error=False)

async def get_session_id_header(session_id: Optional[str] = Header(None, alias="Session-ID", description="Your unique session identifier")):
    return session_id

async def get_user_id(request: Request) -> str:
    if not hasattr(request.state, 'user_id') or request.state.user_id is None:
        raise HTTPException(status_code=401, detail="User ID is not set in the request state.")

async def get_file_services(request: Request, db=Depends(get_db), vectorstore: Chroma=Depends(get_vectorstore)) -> FileServices:
    if not hasattr(request.state, 'file_services') or request.state.file_services is None:
        request.state.file_services = FileServices(vectorstore=vectorstore, db=db)
    return request.state.file_services

async def get_session_services(request: Request, db=Depends(get_db), vectorstore: Chroma=Depends(get_vectorstore)) -> SessionServices:  
    if not hasattr(request.state, 'session_services') or request.state.session_services is None:
        request.state.session_services = SessionServices(vectorstore=vectorstore, db=db)
    return request.state.session_services