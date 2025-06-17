from fastapi import FastAPI, Request, HTTPException, Header
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os
from fastapi.concurrency import run_in_threadpool
from routes import ingest, query, web_routes, session, token
from core.dependencies import init_vectorstore_sync, init_mongodb_async, bearer_scheme, get_session_id_header
from core.auth import clerk_only
from contextlib import asynccontextmanager
from middlewares.auth_middleware import AuthMiddleware
import logging
from fastapi import Depends
from utils.logger import log_timing
from core.config import settings

load_dotenv(override=True)
logging.basicConfig(level=settings.log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
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

app = FastAPI(lifespan=lifespan, dependencies=[Depends(bearer_scheme), Depends(get_session_id_header)])

@app.exception_handler(Exception)
async def handler(request: Request, exc: Exception):
    if isinstance(exc, HTTPException):
        raise exc
    logging.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})

app.add_middleware(AuthMiddleware)

app.include_router(session.router, prefix='/session', dependencies=[Depends(clerk_only)])
app.include_router(ingest.router, prefix="/ingest", dependencies=[Depends(clerk_only)])
app.include_router(query.router, prefix="/query")
app.include_router(web_routes.router, prefix="/webscrape", dependencies=[Depends(clerk_only)])
app.include_router(token.router, prefix='/token', dependencies=[Depends(clerk_only)])

@app.get("/")
async def root():
    return {"message": "Welcome to Smart PDF QA API! Use /docs or /redoc for documentation."}