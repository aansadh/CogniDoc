"""
This module initializes and configures the FastAPI application for the Smart PDF QA API.
It includes route registration, middleware setup, exception handling, and application lifespan management.
"""

from fastapi import FastAPI
from dotenv import load_dotenv
import os
from fastapi.concurrency import run_in_threadpool
from routes import ingest, query, web_routes, session, token, file
from core.dependencies import init_vectorstore_sync, init_mongodb_async, bearer_scheme, get_session_id_header
from core.auth import clerk_only
from contextlib import asynccontextmanager
from middlewares.auth_middleware import AuthMiddleware
import logging
from fastapi import Depends
from core.config import settings
from core.exception_handlers import EXCEPTION_HANDLERS

load_dotenv(override=True)
logging.basicConfig(level=settings.log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages the lifespan of the FastAPI application.

    This function initializes necessary resources during application startup
    and cleans up resources during shutdown.

    Args:
        app (FastAPI): The FastAPI application instance.

    Yields:
        None

    Raises:
        Exception: If an error occurs during application startup.
    """
    try:
        os.makedirs("data", exist_ok=True)
        app.state.settings = settings
        await init_mongodb_async(app)
        await run_in_threadpool(init_vectorstore_sync, app)
        yield
    except Exception as e:
        logging.critical(f"Fatal error during application startup: {e}", exc_info=True)
    finally:
        logging.info("Application lifespan context exiting...")
        if hasattr(app.state, 'mongo_client'):
            logging.info("Closing MongoDB connection...")
            await app.state.mongo_client.close()

app = FastAPI(
    lifespan=lifespan,
    dependencies=[Depends(bearer_scheme), Depends(get_session_id_header)]
)
"""
Initializes the FastAPI application instance with lifespan management and global dependencies.
"""

for exc_type, handler_func in EXCEPTION_HANDLERS:
    """
    Registers exception handlers for the application.

    Args:
        exc_type (type): The exception type to handle.
        handler_func (function): The function to handle the exception.
    """
    app.add_exception_handler(exc_type, handler_func)

app.add_middleware(AuthMiddleware)
"""
Adds authentication middleware to the application.
"""

app.include_router(session.router, prefix='/session', dependencies=[Depends(clerk_only)])
"""
Includes session-related routes with clerk-only access.
"""

app.include_router(ingest.router, prefix="/ingest", dependencies=[Depends(clerk_only)])
"""
Includes ingest-related routes with clerk-only access.
"""

app.include_router(query.router, prefix="/query")
"""
Includes query-related routes.
"""

app.include_router(web_routes.router, prefix="/webscrape", dependencies=[Depends(clerk_only)])
"""
Includes web scraping routes with clerk-only access.
"""

app.include_router(token.router, prefix='/token', dependencies=[Depends(clerk_only)])
"""
Includes token-related routes with clerk-only access.
"""

app.include_router(file.router, prefix='/file', dependencies=[Depends(clerk_only)])
"""
Includes file-related routes with clerk-only access.
"""

@app.get("/")
async def root():
    """
    Root endpoint of the API.

    Returns:
        dict: A welcome message and documentation links.
    """
    return {"message": "Welcome to Smart PDF QA API! Use /docs or /redoc for documentation."}