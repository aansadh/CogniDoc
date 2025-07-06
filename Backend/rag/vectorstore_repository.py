from langchain_chroma import Chroma
from langchain.docstore.document import Document
from .exceptions import VectorstoreInitError, DocumentProcessingError, VectorstoreError, ContextNotFoundError
from typing import Iterable, Dict, Any
from .utils import run_in_threadpool, log_duration
import logging

logger = logging.getLogger(__name__)

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
            logger.error("Vectorstore instance is missing.")
            raise VectorstoreInitError("Vectorstore instance is missing.")
        self.vectorstore = vectorstore
        logger.info("VectorstoreRepository initialized successfully.")

    @log_duration
    @run_in_threadpool
    def add_documents(self, chunks: Iterable[Document]):
        """
        Asynchronously adds document chunks to the vectorstore.

        Args:
            chunks (Iterable[Document]): The document chunks to add.

        Raises:
            DocumentProcessingError: If the operation fails.
        """
        try:
            logger.debug(f"Adding {len(chunks)} document chunks to the vectorstore.")
            self.vectorstore.add_documents(chunks)
            logger.info("Documents added to the vectorstore successfully.")
        except Exception as e:
            logger.error(f"Failed to add documents to vectorstore: {e}", exc_info=True)
            raise DocumentProcessingError(f"Failed to split and add document to vectorstore: {e}")

    @log_duration
    @run_in_threadpool
    def get_relevant_chunks(self, query: str, filter=None, relevance_threshold=0.3, k=5):
        """
        Asynchronously retrieves relevant document chunks from the vectorstore based on a query.

        Args:
            query (str): The query string.
            filter (optional): Filter criteria for the search.
            relevance_threshold (float, optional): Minimum relevance score. Defaults to 0.3.
            k (int, optional): Number of top results to retrieve. Defaults to 5.

        Returns:
            List[Tuple[Document, float]]: Relevant document chunks and their relevance scores.

        Raises:
            ContextNotFoundError: If no relevant documents are found.
            VectorstoreError: If the operation fails.
        """
        try:
            logger.debug(f"Fetching relevant chunks for query: {query}")
            relevant_chunks = self.vectorstore.similarity_search_with_relevance_scores(query, k=k, filter=filter)
            if len(relevant_chunks) == 0 or relevant_chunks[0][1] < relevance_threshold:
                logger.warning("No relevant documents found for the query!")
                raise ContextNotFoundError("No relevant documents found for the query!")
            logger.info(f"Found {len(relevant_chunks)} relevant chunks for query: {query}")
            return relevant_chunks
        except Exception as e:
            logger.error(f"Error fetching relevant chunks: {e}", exc_info=True)
            raise VectorstoreError(f"Error fetching relevant chunks: {str(e)}")

    @log_duration
    @run_in_threadpool
    def delete_doc_async(self, filter_criteria: Dict[str, Any]):
        """
        Asynchronously deletes documents from the vectorstore based on filter criteria.

        Args:
            filter_criteria (Dict[str, Any]): The criteria for filtering documents to delete.

        Raises:
            VectorstoreError: If the operation fails.
        """
        try:
            logger.debug(f"Deleting documents with filter criteria: {filter_criteria}")
            chroma_collection = self.vectorstore._collection
            chroma_collection.delete(where=filter_criteria)
            logger.info("Documents deleted from the vectorstore successfully.")
        except Exception as e:
            logger.error(f"Error deleting documents from vectorstore: {e}", exc_info=True)
            raise VectorstoreError(f"Error deleting documents from vectorstore: {str(e)}")

