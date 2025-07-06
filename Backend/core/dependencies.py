"""
Dependency injection utilities for the Smart PDF QA API application.
"""

from fastapi import Request, FastAPI, HTTPException, Header, Depends
from fastapi.security import HTTPBearer
from typing import Optional
from langchain_chroma import Chroma
import os
from rag.store.embeddings_store import get_embedding_model
from utils.logger import log_duration
from pymongo import AsyncMongoClient
from core.config import settings
import logging
from services.file_services import FileServices
from services.session_services import SessionServices
from rag.services.rag_services import RagServices

logger = logging.getLogger(__name__)

# This cannot be async as it only performs blocking operations
@log_duration
def init_vectorstore_sync(app: FastAPI):
    """
    Initializes the vectorstore synchronously.

    Args:
        app (FastAPI): The FastAPI application instance.
    """
    logger.debug("Initializing vectorstore synchronously.")
    os.makedirs("rag/chroma_db", exist_ok=True)
    embedding_model = get_embedding_model(
        settings.embedding_provider,
        settings.embedding_model
    )
    app.state.vectorstore = Chroma(persist_directory="rag/chroma_db", embedding_function=embedding_model)
    logger.info("Vectorstore initialized successfully.")

@log_duration
async def init_mongodb_async(app: FastAPI):
    """
    Initializes the MongoDB connection asynchronously.

    Args:
        app (FastAPI): The FastAPI application instance.
    """
    logger.debug("Initializing MongoDB connection asynchronously.")
    mongo_uri = settings.mongodb_uri
    mongodb_db = settings.mongodb_db
    app.state.mongo_client = AsyncMongoClient(mongo_uri)
    app.state.db = app.state.mongo_client[mongodb_db]
    logger.info(f"Connected to MongoDB at {mongo_uri}/{mongodb_db}")

def get_db(request: Request):
    """
    Retrieves the database connection from the application state.

    Args:
        request (Request): The incoming HTTP request.

    Returns:
        Database connection instance.

    Raises:
        RuntimeError: If the database connection is not initialized.
    """
    logger.debug("Retrieving database connection from application state.")
    if not hasattr(request.app.state, 'db') or request.app.state.db is None:
        logger.error("Database connection is not initialized.")
        raise RuntimeError("Database connection is not initialized.")
    return request.app.state.db

def get_vectorstore(request: Request) -> Chroma:
    """
    Retrieves the vectorstore instance from the application state.

    Args:
        request (Request): The incoming HTTP request.

    Returns:
        Chroma: The vectorstore instance.

    Raises:
        RuntimeError: If the vectorstore is not initialized.
    """
    logger.debug("Retrieving vectorstore instance from application state.")
    if not hasattr(request.app.state, 'vectorstore') or request.app.state.vectorstore is None:
        logger.error("Vectorstore is not initialized.")
        raise RuntimeError("Vectorstore is not initialized. Set it using set_vectorstore() before accessing.")
    return request.app.state.vectorstore

async def validate_session(request: Request) -> str:
    """
    Validates the session ID in the request state.

    Args:
        request (Request): The incoming HTTP request.

    Returns:
        str: The session ID.

    Raises:
        HTTPException: If the session ID is not valid.
    """
    logger.debug("Validating session ID in request state.")
    if not request.state.session_id:
        logger.error("Valid Session ID is required.")
        raise HTTPException(status_code=401, detail="Valid Session ID is required")
    return request.state.session_id

bearer_scheme = HTTPBearer(auto_error=False)

async def get_session_id_header(session_id: Optional[str] = Header(None, alias="Session-ID", description="Your unique session identifier")):
    """
    Retrieves the session ID from the request header.

    Args:
        session_id (Optional[str]): The session ID from the header.

    Returns:
        Optional[str]: The session ID.
    """
    return session_id

async def get_user_id(request: Request) -> str:
    """
    Retrieves the user ID from the request state.

    Args:
        request (Request): The incoming HTTP request.

    Returns:
        str: The user ID.

    Raises:
        HTTPException: If the user ID is not set.
    """
    logger.debug("Retrieving user ID from request state.")
    if not hasattr(request.state, 'user_id') or request.state.user_id is None:
        logger.error("User ID is not set in the request state.")
        raise HTTPException(status_code=401, detail="User ID is not set in the request state.")
    return request.state.user_id

async def get_rag_services(
        request: Request, 
        vectorstore: Chroma = Depends(get_vectorstore)
):
    """
    Retrieves the RagServices instance from the request state or initializes it if not present.

    Args:
        request (Request): The incoming HTTP request.
        vectorstore (Chroma): The vectorstore instance.

    Returns:
        RagServices: The RagServices instance.
    """
    logger.debug("Retrieving or initializing RagServices instance.")
    if not hasattr(request.state, 'rag_services') or request.state.rag_services is None:
        request.state.rag_services = RagServices(vectorstore=vectorstore, provider=settings.llm_provider, model=settings.llm)
        logger.info(f"RagServices instance initialized. llm_provider: {settings.llm_provider}, llm: {settings.llm}")
    return request.state.rag_services

async def get_file_services(request: Request, db=Depends(get_db), rag_services: RagServices=Depends(get_rag_services)) -> FileServices:
    """
    Retrieves the FileServices instance from the request state or initializes it if not present.

    Args:
        request (Request): The incoming HTTP request.
        db: The database connection instance.
        rag_services (RagServices): The RagServices instance.

    Returns:
        FileServices: The FileServices instance.
    """
    logger.debug("Retrieving or initializing FileServices instance.")
    if not hasattr(request.state, 'file_services') or request.state.file_services is None:
        request.state.file_services = FileServices(db=db, rag_services=rag_services)
        logger.info("FileServices instance initialized.")
    return request.state.file_services

async def get_session_services(request: Request, db=Depends(get_db), rag_services: RagServices=Depends(get_rag_services)) -> SessionServices:
    """
    Retrieves the SessionServices instance from the request state or initializes it if not present.

    Args:
        request (Request): The incoming HTTP request.
        db: The database connection instance.
        rag_services (RagServices): The RagServices instance.

    Returns:
        SessionServices: The SessionServices instance.
    """
    logger.debug("Retrieving or initializing SessionServices instance.")
    if not hasattr(request.state, 'session_services') or request.state.session_services is None:
        request.state.session_services = SessionServices(db=db, rag_services=rag_services)
        logger.info("SessionServices instance initialized.")
    return request.state.session_services
