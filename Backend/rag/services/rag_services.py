from ..vectorstore_repository import VectorstoreRepository
import logging
from langchain.docstore.document import Document
from ..store.llm_store import get_llm
from ..store.embeddings_store import get_embedding_model
from langchain_chroma import Chroma
from typing import Iterable, Dict, Any, List
from ..ingestion.document_loaders import load_documents_from_pdf, load_documents_from_string
from ..ingestion.document_splitter import split_docs
from ..exceptions import DocumentProcessingError, ContextNotFoundError, QueryProcessingError
from ..utils import log_duration

logger = logging.getLogger(__name__)

class RagServices:
    """
    Provides services for managing and querying a vectorstore, including adding documents and generating responses.
    Note: All the methods in this class are asynchronous, allowing for non-blocking operations.
    """

    def __init__(self, vectorstore: Chroma, provider: str = 'ollama', model: str = 'phi3:mini', url: str = None):
        """
        Initializes the RagServices instance.

        Args:
            vectorstore (Chroma): The vectorstore instance for document storage.
            provider (str, optional): The LLM provider. Defaults to 'ollama'.
            model (str, optional): The LLM model to use. Defaults to 'phi3:mini'.
        """
        self.vectorstore_repository = VectorstoreRepository(vectorstore)
        self.url = url.strip() if url else None
        self.provider = provider
        self.model = model
        logger.info(f"RagServices initialized with provider: {self.provider}, model: {self.model}")
        self.llm = get_llm(provider=self.provider, model=self.model, url=self.url)

    @log_duration
    async def _split_and_add_docs_to_vectorstore(self, docs: Iterable[Document], metadata: Dict[str, Any]):
        """
        Asynchronously splits and adds documents to the vectorstore.

        Args:
            docs (Iterable[Document]): The documents to split and add.
            metadata (Dict[str, Any]): Metadata associated with the documents.

        Raises:
            DocumentProcessingError: If the operation fails.
        """
        try:
            logger.debug("Splitting and adding documents to the vectorstore.")
            chunks = await split_docs(docs, metadata=metadata or {})
            await self.vectorstore_repository.add_documents(chunks)
            logger.info(f"Successfully added {len(chunks)} chunks to the vectorstore.")
        except Exception as e:
            logger.error(f"Failed to split and add documents to vectorstore: {e}", exc_info=True)
            raise DocumentProcessingError(f"Failed to split and add documents to vectorstore: {e}")

    @log_duration
    async def add_pdf_async(self, file_path: str, metadata: Dict[str, Any] = None):
        """
        Asynchronously loads a PDF, splits its content, and adds it to the vectorstore.

        Args:
            file_path (str): The path to the PDF file.
            metadata (Dict[str, Any], optional): Metadata associated with the PDF. Defaults to None.

        Raises:
            DocumentProcessingError: If the operation fails.
        """
        try:
            logger.debug(f"Loading PDF from file: {file_path}")
            docs = await load_documents_from_pdf(file_path)
            await self._split_and_add_docs_to_vectorstore(docs, metadata)
            logger.info(f"PDF added to vectorstore successfully: {file_path}")
        except Exception as e:
            logger.error(f"Failed to process and insert PDF document: {e}", exc_info=True)
            raise DocumentProcessingError(f"Failed to process and insert PDF document: {e}")

    @log_duration
    async def add_content_async(self, content: str, metadata: Dict[str, Any] = None):
        """
        Asynchronously converts string content to a document, splits it, and adds it to the vectorstore.

        Args:
            content (str): The content to add.
            metadata (Dict[str, Any], optional): Metadata associated with the content. Defaults to None.

        Raises:
            DocumentProcessingError: If the operation fails.
        """
        try:
            logger.debug("Loading content into vectorstore.")
            docs = load_documents_from_string(content)
            await self._split_and_add_docs_to_vectorstore(docs, metadata)
            logger.info("Content added to vectorstore successfully.")
        except Exception as e:
            logger.error(f"Failed to process and insert content: {e}", exc_info=True)
            raise DocumentProcessingError(f"Failed to process and insert content: {e}")

    @log_duration
    async def retrieve_context(self, query: str, filter=None, relevance_threshold=0.3, k=5) -> dict:
        """
        Asynchronously retrieves relevant context from the vectorstore based on the query.

        Args:
            query (str): The query string to search for.
            filter (dict, optional): Additional filters for the search.
            relevance_threshold (float, optional): Minimum relevance score for returned chunks.
            k (int, optional): Number of top relevant chunks to return.

        Returns:
            dict: A dictionary containing the concatenated context and sources in format: 
            {
                "context": str,
                "sources": List[str]
            }
        """
        try:
            logger.debug(f"Retrieving context for query: {query}")
            relevant_chunks = await self.vectorstore_repository.get_relevant_chunks(
                query, filter=filter, relevance_threshold=relevance_threshold, k=k
            )
            context_data = self._get_context_from_relevant_chunks(relevant_chunks)
            
            logger.info("Context retrieved successfully.")
            logger.debug(f"Context data: {context_data['context']}")  
            return context_data
        except ContextNotFoundError as e:
            logger.warning(f"No relevant documents found for the query: {query}")
            raise e
        except Exception as e:
            logger.error(f"Error retrieving context for query '{query}': {e}", exc_info=True)
            raise QueryProcessingError(f"Error retrieving context for query '{query}': {str(e)}")
        
    @log_duration
    async def generation_async(self, context: str, query: str) -> str:
        f"""
        Asynchronously generates a response from the LLM based on the provided context and query.

        Args:
            context (str): The context for the query.
            query (str): The query string.

        Returns:
            str: The generated response content from the LLM.

        Raises:
            QueryProcessingError: If there is an error during LLM response generation.
        """
        try:
            logger.debug("Generating response using LLM.")

            # Define the system prompt based on your RAG requirements
            system_prompt = (
                "You are an intelligent assistant. Your task is to answer the user's question based ONLY on the provided context. "
                "If the answer is not found in the context, clearly state that you don't have enough information. "
                "Avoid making up answers or using external knowledge."
            )

            # Construct the user message using the context and query
            user_message_content = (
                f"Context:\n{context}\n\n"
                f"Question:\n{query}\n\n"
                f"Answer:"
            )

            messages = [
                {"role": "system", "content": system_prompt.strip()},
                {"role": "user", "content": user_message_content.strip()}
            ]

            response_dict = await self.llm.generate_async(messages=messages)
            generated_content = response_dict.get('content', '')

            if not generated_content:
                logger.warning(f"LLM generated an empty response for query: {query}")
                return ""

            logger.info("Response generated successfully.")
            return generated_content

        except Exception as e:
            logger.error(f"Error generating response for query '{query}': {e}", exc_info=True)
            raise QueryProcessingError(f"Error generating response for query '{query}': {str(e)}") from e

    @log_duration
    async def process_query(self, query: str, filter=None, relevance_threshold=0.3, k=5) -> dict:
        """
        Asynchronously processes a query by retrieving relevant context and generating a response.

        Args:
            query (str): The query string to process.
            filter (dict, optional): Additional filters for the search.
            relevance_threshold (float, optional): Minimum relevance score for returned chunks.
            k (int, optional): Number of top relevant chunks to return.

        Returns:
            dict: A dictionary containing the generated response and sources.
            {
                "response": str,
                "sources": list[str]
            }
        """
        try:
            logger.debug(f"Processing query: {query}")
            context_data = await self.retrieve_context(query, filter=filter, relevance_threshold=relevance_threshold, k=k)
            response = await self.generation_async(context_data['context'], query)
            logger.info("Query processed successfully.")
            return {
                "response": response,
                "sources": list(set(context_data['sources']))
            }
        except QueryProcessingError as e:
            logger.error(f"Error processing query '{query}': {e}", exc_info=True)
            raise e
        except Exception as e:
            logger.error(f"Unexpected error processing query '{query}': {e}", exc_info=True)
            raise QueryProcessingError(f"Unexpected error processing query '{query}': {str(e)}")

    @log_duration
    def _get_context_from_relevant_chunks(self, relevant_chunks: list[tuple[Document, float]]) -> dict:
        """
        Synchronously extracts context and sources from relevant document chunks.

        Args:
            relevant_chunks (list[tuple[Document, float]]): Relevant document chunks and their scores.

        Returns:
            dict: A dictionary containing the concatenated context and sources.
        """
        logger.debug("Assembling context from relevant chunks.")
        context = ""
        sources = []
        for doc, _ in relevant_chunks:
            page = doc.metadata.get("page", "N/A")
            source = doc.metadata.get("file_name", "Unknown")
            sources.append(f"{source} (page {page})")
            context += f"{doc.page_content}\n---\n"
        logger.info(f"Context assembled with {len(sources)} sources.")
        return {
            "context": context.strip(),
            "sources": sources
        }
    
    async def delete_doc_async(self, filter_criteria: Dict[str, Any]):
        """
        Asynchronously deletes documents from the vectorstore based on filter criteria.

        Args:
            filter_criteria (Dict[str, Any]): The criteria for filtering documents to delete.

        Raises:
            VectorstoreError: If the operation fails.
        """
        try:
            logger.debug(f"Deleting documents with filter criteria: {filter_criteria}")
            await self.vectorstore_repository.delete_doc_async(filter_criteria)
            logger.info("Documents deleted successfully.")
        except Exception as e:
            logger.error(f"Failed to delete documents from vectorstore: {e}", exc_info=True)
            raise QueryProcessingError(f"Failed to delete documents from vectorstore: {e}")

@log_duration    
async def main():
    """
    Main function to demonstrate the RagService functionality.
    This is for testing purposes and can be removed in production.
    """
    logging.basicConfig(level=logging.DEBUG)
    logger.info("RagService module loaded successfully.")
    
    embedding_model = get_embedding_model()
    vectorstore = Chroma(persist_directory='Backend/chroma_db', embedding_function=embedding_model)
    rag_service = RagServices(vectorstore=vectorstore, provider='ollama', model='phi3:mini')

    # await rag_service.add_pdf_async('F:/pdfs-w/orwell1984.pdf')

    query = "What is the main theme of 1984?"
    try:
        response = await rag_service.process_query(query, k=15)
        logger.info(f"Response: {response['response']}")
        logger.info(f"Sources: {response['sources']}")
    except QueryProcessingError as e:
        logger.error(f"Error processing query: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())