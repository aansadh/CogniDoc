from fastapi import APIRouter, HTTPException, Depends
from models.models import ScrapeUrlModel
from core.dependencies import get_vectorstore, get_db, validate_session
from web_extraction.web_scraper import WebScraper
from fastapi.concurrency import run_in_threadpool
from datetime import datetime, timezone
from services.file_processing import process_content_upload
from utils.logger import log_timing

router = APIRouter()
# auth_method: 'clerk'

# Suspected blocking operation

@router.post('/')
@log_timing
async def scrape_url(
    url: ScrapeUrlModel,
    session_id: str=Depends(validate_session),
    db=Depends(get_db),
    vectorstore=Depends(get_vectorstore)
):
    if not url.url.strip():
        raise HTTPException(status_code=400, detail="URL cannot be empty.")

    try:
        scraper = WebScraper(url.url)
        print(f"Scraping URL: {url.url}")
        
        content = scraper.scrape()
        if not content:
            raise HTTPException(status_code=404, detail=f"No content found to scrape from URL: {url.url}")

        file_name = f"{url.url.strip()}-scr.txt"

        file_id = await process_content_upload(
            session_id=session_id,
            content=content.encode(),
            file_name=file_name,
            created_at=datetime.now(timezone.utc),
            vectorstore=vectorstore,
            db=db
        )

        return {
            "message": "Content scraped and processed successfully.",
            "file_id": file_id,
            "session_id": session_id,
            "file_name": file_name,
            "preview": f"{content[:200]}..."
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during scraping or processing: {str(e)}")