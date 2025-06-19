from langchain_chroma import Chroma
from Backend.repositories.file_io import create_and_write_file_async
from repositories.vectorstore_repo import add_pdf_to_vectorstore_async, delete_doc_from_vectorstore_async, add_content_to_vectorstore_async
from Backend.repositories.file_repository import add_file_metadata_to_db, delete_file_from_db
import os 
from datetime import datetime, timezone

async def process_file_upload(
        session_id: str, 
        content, 
        file_name: str, 
        created_at = datetime.now(timezone.utc), 
        vectorstore: Chroma = None, 
        db=None
):
    file_path = None
    try:
        file_id = await add_file_metadata_to_db(file_name, session_id, created_at, db)
        _, file_path = await create_and_write_file_async(content, str(file_id))
        await add_pdf_to_vectorstore_async(file_id, file_path, file_name, session_id, vectorstore)
        return file_id
    
    except Exception:
        await delete_file_from_db(file_id, db)
        raise
    finally:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as cleanup_error:
            print(f"Failed to delete temp file: {file_path}: {cleanup_error}")


async def process_content_upload(
        session_id: str, 
        content: str, 
        file_name: str, 
        created_at = datetime.now(timezone.utc), 
        vectorstore: Chroma = None, 
        db=None
):
    if not content.strip():
        raise ValueError("Content cannot be empty.")
    try:
        file_id = await add_file_metadata_to_db(file_name, session_id, created_at, db)
        await add_content_to_vectorstore_async(file_id, content.strip(), file_name, session_id, vectorstore)
        return file_id
    except Exception:
        await delete_file_from_db(file_id, db)
        raise


async def process_file_deletion(
        session_id: str,
        file_id: str = None,
        vectorstore: Chroma = None,
        db=None
):
    await delete_doc_from_vectorstore_async(file_id=file_id, session_id=session_id, vectorstore=vectorstore)
    await delete_file_from_db(file_id, session_id, db)