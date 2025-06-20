from langchain_chroma import Chroma
from langchain.docstore.document import Document
from rag.pipeline import load_documents, split_docs
from rag.exceptions import VectorstoreInitError, DocumentProcessingError, VectorstoreError
from typing import Iterable, Dict, Any
from fastapi.concurrency import run_in_threadpool 

class VectorstoreRepository:
    """
    Provides methods for interacting with the vectorstore, including adding, splitting, and deleting documents.
    """

    def __init__(self, vectorstore: Chroma):
        """
        Initializes the VectorstoreRepository instance.

        Args:
            vectorstore (Chroma): The vectorstore instance for document storage.

        Raises:
            VectorstoreInitError: If the vectorstore instance is missing.
        """
        if not vectorstore:
            raise VectorstoreInitError("Vectorstore instance is missing.")
        self.vectorstore = vectorstore

    def _split_and_add_docs_to_vectorstore_blocking(self, docs: Iterable[Document], metadata: Dict[str, Any]):
        """
        Helper for splitting and adding documents to the vectorstore.

        Args:
            docs (Iterable[Document]): The documents to split and add.
            metadata (Dict[str, Any]): Metadata associated with the documents.

        Raises:
            DocumentProcessingError: If the operation fails.
        """
        try:
            chunks = split_docs(docs, metadata=metadata or {})
            self.vectorstore.add_documents(chunks)
        except Exception as e:
            raise DocumentProcessingError(f"Failed to split and add documents to vectorstore: {e}")

    async def add_pdf_async(self, file_path: str, metadata: Dict[str, Any] = None):
        """
        Loads a PDF, splits its content, and adds it to the vectorstore asynchronously.

        Args:
            file_path (str): The path to the PDF file.
            metadata (Dict[str, Any], optional): Metadata associated with the PDF. Defaults to None.

        Raises:
            DocumentProcessingError: If the operation fails.
        """
        try:
            docs = await run_in_threadpool(load_documents, file_path)
            await run_in_threadpool(self._split_and_add_docs_to_vectorstore_blocking, docs, metadata)
        except Exception as e:
            raise DocumentProcessingError(f"Failed to process and insert PDF document: {e}")

    async def add_content_async(self, content: str, metadata: Dict[str, Any] = None):
        """
        Converts string content to a document, splits it, and adds it to the vectorstore asynchronously.

        Args:
            content (str): The content to add.
            metadata (Dict[str, Any], optional): Metadata associated with the content. Defaults to None.

        Raises:
            DocumentProcessingError: If the operation fails.
        """
        try:
            doc = Document(page_content=content, metadata=metadata)
            await run_in_threadpool(self._split_and_add_docs_to_vectorstore_blocking, [doc], metadata)
        except Exception as e:
            raise DocumentProcessingError(f"Failed to process and insert content: {e}")

    async def delete_doc_async(self, filter_criteria: Dict[str, Any]):
        """
        Asynchronously deletes documents from the vectorstore based on filter criteria.

        Args:
            filter_criteria (Dict[str, Any]): The criteria for filtering documents to delete.

        Raises:
            VectorstoreError: If the operation fails.
        """
        try:
            chroma_collection = self.vectorstore._collection
            await run_in_threadpool(chroma_collection.delete, where=filter_criteria)
        except Exception as e:
            raise VectorstoreError(f"Error deleting documents from vectorstore: {str(e)}")