from fastapi.concurrency import run_in_threadpool
from fastapi import HTTPException
from rag.vectorstore_ops import add_pdf_to_vectorstore, delete_doc_from_vectorstore, add_content_to_vectorstore
from langchain_chroma import Chroma
from rag.exceptions import DocumentProcessingError, VectorstoreInitError, VectorstoreError

async def _add_to_vectorstore(
        file_id: str, 
        file_name: str,
        session_id: str,
        vectorstore: Chroma = None, 
        metadata: dict = None,
        process_func: callable = None,
        *args,
        **kwargs
):
    if not file_id or not file_name or not session_id or not vectorstore or not process_func:
        raise HTTPException(status_code=400, detail="Missing required parameters: file_id, file_name, session_id, vectorstore, or process_func.")
    try:
        metadata = metadata or {}
        metadata.update({ "file_id": file_id, "file_name": file_name, "session_id": session_id })
        await run_in_threadpool(
            process_func, *args, **kwargs, vectorstore=vectorstore, metadata=metadata
        )
    except DocumentProcessingError as e:
        raise HTTPException(status_code=500, detail=f"Error processing the document: {str(e)}")
    except VectorstoreInitError as e:
        raise HTTPException(status_code=500, detail=f"Vectorstore not initialized: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}") 


async def add_pdf_to_vectorstore_async(file_id: str, file_path: str, file_name: str, session_id: str, vectorstore: Chroma = None, metadata: dict = None):
    if not file_id or not file_path or not file_name or not session_id or not vectorstore:
        raise HTTPException(status_code=400, detail="Missing required parameters: file_id, file_path, file_name, session_id, or vectorstore.")
    await _add_to_vectorstore(
        file_id, file_name, session_id, vectorstore, metadata,
        process_func=add_pdf_to_vectorstore, file_path=file_path
    )


async def add_content_to_vectorstore_async(file_id: str, content: str, file_name: str, session_id: str, vectorstore: Chroma = None, metadata: dict = None):
    if not file_id or not content.strip() or not file_name or not session_id or not vectorstore:
        raise HTTPException(status_code=400, detail="Missing required parameters: file_id, content, file_name, session_id, or vectorstore.")
    await _add_to_vectorstore(
        file_id, file_name, session_id, vectorstore, metadata,
        process_func=add_content_to_vectorstore, content=content
    )
    

async def delete_doc_from_vectorstore_async(session_id: str, file_id: str = None, vectorstore: Chroma = None):
    if not file_id and not session_id:
        raise HTTPException(status_code=400, detail="Either file_id or session_id must be provided.")
    
    try:
        filter = {"$and": [{"file_id": file_id}, {"session_id": session_id}]} if file_id else {"session_id": session_id}
        await run_in_threadpool(delete_doc_from_vectorstore, filter, vectorstore)

    except VectorstoreError as e:
        raise HTTPException(status_code=500, detail=f"Error deleting file: {str(e)}")