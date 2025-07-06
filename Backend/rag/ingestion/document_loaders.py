from langchain_community.document_loaders import PyMuPDFLoader
import os
from typing import Iterable
from langchain.docstore.document import Document
from ..utils import run_in_threadpool
import logging

logger = logging.getLogger(__name__)

@run_in_threadpool
def load_documents_from_pdf(file_path: str) -> Iterable[Document]:
    """
    Synchronously loads documents from a PDF file.

    Args:
        file_path (str): The path to the PDF file.

    Returns:
        Iterable[Document]: A list of documents extracted from the PDF.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    logger.debug(f"Attempting to load documents from PDF: {file_path}")
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        raise FileNotFoundError(f"The file {file_path} doesn't exist.")
    loader = PyMuPDFLoader(file_path)
    documents = loader.load()
    logger.info(f"Loaded {len(documents)} documents from PDF: {file_path}")
    logger.debug(f"Documents Loaded: {[doc for doc in documents]}")
    return documents

def load_documents_from_string(content: str, metadata: dict = None) -> Iterable[Document]:
    """
    Synchronously loads documents from a string.
    Note: This is a non-blocking operation.

    Args:
        content (str): The string content to load as a document.
        metadata (dict, optional): Metadata to associate with the document. Defaults to None.

    Returns:
        Iterable[Document]: A list containing a single document created from the string.

    Raises:
        ValueError: If the content is empty.
    """
    logger.debug("Attempting to load document from string content.")
    if not content:
        logger.error("Content cannot be empty.")
        raise ValueError("Content cannot be empty.")
    doc = Document(page_content=content, metadata=metadata or {})
    logger.info("Document created from string content.")
    return [doc]