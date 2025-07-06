from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from ..utils import log_duration, run_in_threadpool
import logging

logger = logging.getLogger(__name__)

@log_duration
@run_in_threadpool
def split_docs(documents: List[Document], metadata: dict = None):
    """
    Asynchronously splits documents into smaller chunks using a recursive character text splitter.

    Args:
        documents (List[Document]): A list of documents to split.
        metadata (dict, optional): Additional metadata to associate with each chunk. Defaults to None.

    Returns:
        List[Document]: A list of document chunks with updated metadata.
    """
    logger.debug(f"Starting document splitting for {len(documents)} documents.")
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = []
    for doc in documents:
        logger.debug(f"Splitting document with metadata: {doc.metadata}")
        doc_chunks = splitter.split_documents([doc])
        for chunk in doc_chunks:
            chunk.metadata.update(doc.metadata)
            if metadata:
                chunk.metadata.update(metadata)
            chunks.append(chunk)
    logger.info(f"Generated {len(chunks)} chunks from {len(documents)} documents.")
    return chunks