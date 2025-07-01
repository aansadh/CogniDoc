"""
Routes for handling web scraping operations in the Smart PDF QA API application.

Suspected to be a blocking operation due too use of Request in WebScraper.
"""

from fastapi import APIRouter, HTTPException, Depends
from models.models import ScrapeUrlModel
from core.dependencies import validate_session, get_file_services
from web_extraction.web_scraper import WebScraper
from utils.logger import log_duration
from services.file_services import FileServices
import logging

router = APIRouter()
# auth_method: 'clerk'

logger = logging.getLogger(__name__)

@router.post('/')
@log_duration
async def scrape_url(
    url: ScrapeUrlModel,
    session_id: str=Depends(validate_session),
    file_services: FileServices = Depends(get_file_services)
):
    logger.debug(f"Scraping URL: session_id={session_id}, url={url.url}")
    if not url.url.strip():
        logger.warning("URL is empty. Raising HTTPException.")
        raise HTTPException(status_code=400, detail="URL cannot be empty.")

    try:
        logger.info(f"Starting web scraping for URL: {url.url}")
        content = WebScraper(url.url).scrape()
        if not content:
            logger.warning(f"No content found to scrape from URL: {url.url}")
            raise HTTPException(status_code=404, detail=f"No content found to scrape from URL: {url.url}")

        file_name = f"{url.url.strip()}-scr.txt"

        file_id = await file_services.process_content_upload(
            session_id=session_id,
            content=content.strip(),
            file_name=file_name,
        )

        logger.info(f"Content scraped and processed successfully: file_id={file_id}, session_id={session_id}")
        return {
            "message": "Content scraped and processed successfully.",
            "file_id": file_id,
            "session_id": session_id,
            "file_name": file_name,
            "preview": f"{content[:200]}..."
        }
    except Exception as e:
        logger.error(f"Failed to scrape URL: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to scrape URL.")