from langchain_chroma import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyMuPDFLoader
import os, httpx, requests
from rag.exceptions import ContextNotFoundError, QueryProcessingError, EnvironmentError
from typing import List, Iterable
import logging

logger = logging.getLogger(__name__)

def load_documents(file_path: str):
    logger.debug(f"Loading documents from file: {file_path}")
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        raise FileNotFoundError(f"The file {file_path} doesn't exist.")
    loader = PyMuPDFLoader(file_path)
    documents = loader.load()
    logger.info(f"Loaded {len(documents)} documents from file: {file_path}")
    return documents

def split_docs(documents: List[Iterable], metadata: dict = None):
    logger.debug("Splitting documents into chunks.")
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = []
    for doc in documents:
        logger.debug(f"Splitting document with metadata: {doc.metadata}")
        doc_chunks = splitter.split_documents([doc])
        for chunk in doc_chunks:
            chunk.metadata.update(doc.metadata)
            if metadata:
                chunk.metadata.update(metadata)
            chunks.append(chunk)
    logger.info(f"Generated {len(chunks)} chunks from documents.")
    return chunks

def get_relevant_chunks(vectorstore: Chroma, query: str, filter=None, relevance_threshold=0.3, k=5):
    logger.debug(f"Fetching relevant chunks for query: {query}")
    relevant_chunks = vectorstore.similarity_search_with_relevance_scores(query, k=k, filter=filter)
    if len(relevant_chunks) == 0 or relevant_chunks[0][1] < relevance_threshold:
        logger.warning("No relevant documents found for the query!")
        raise ContextNotFoundError("No relevant documents found for the query!")
    logger.info(f"Found {len(relevant_chunks)} relevant chunks for query: {query}")
    return relevant_chunks

def get_context(vectorstore: Chroma, query: str, filter=None):
    logger.debug(f"Getting context for query: {query}")
    relevant_chunks = get_relevant_chunks(vectorstore, query, filter)
    context = ""
    sources = []
    for doc, _ in relevant_chunks:
        page = doc.metadata.get("page", "N/A")
        source = doc.metadata.get("file_name", "Unknown")
        sources.append(f"{source} (page {page})")
        context += f"{doc.page_content}\n\n"
    logger.info(f"Context assembled with {len(sources)} sources.")
    return {
        "context": context.strip(),
        "sources": sources
    }

def ask_query(context: str, query: str, url: str = None):
    logger.debug(f"Preparing to ask query: {query}")
    API_URL = url or os.getenv("HUGGINGFACE_INFERENCE_API_URL")
    if not API_URL:
        logger.error("API URL is missing. Set the API_URL environment variable.")
        raise EnvironmentError("API URL is missing. Set the API_URL environment variable.")
    API_KEY = os.getenv("HUGGINGFACE_API_KEY")
    if not API_KEY:
        logger.error("Hugging Face API key is missing. Set HUGGINGFACE_API_KEY environment variable.")
        raise EnvironmentError("Hugging Face API key is missing. Set HUGGINGFACE_API_KEY environment variable.")

    headers = {"Authorization": f"Bearer {API_KEY}"}
    prompt = f"""
                You are an intelligent assistant. Your task is to answer the user's question based ONLY on the provided context.
                If the answer is not found in the context, clearly state that you don't have enough information.
                Avoid making up answers or using external knowledge.\n
                Context:
                {context}\n
                Question:
                {query}\n
                Answer:
            """
    payload = {
        "messages": [
            {"role": "user", "content": prompt.strip()}
        ],
        "model": "microsoft/phi-4"
    }
    try:
        logger.info("Sending query to Hugging Face API.")
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        logger.info("Query processed successfully.")
        return result['choices'][0]['message']
    except requests.HTTPError as e:
        logger.error(f"Model API error: {e.response.status_code} - {e.response.text}", exc_info=True)
        raise QueryProcessingError(f"Model API error: {e.response.status_code} - {e.response.text}")
    except requests.RequestException as e:
        logger.error(f"Request to model API failed: {str(e)}", exc_info=True)
        raise QueryProcessingError(f"Request to model API failed: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error during query: {str(e)}", exc_info=True)
        raise QueryProcessingError(f"Unexpected error during query: {str(e)}")

def process_query(query: str, vectorstore: Chroma, filter: dict=None):
    logger.debug(f"Processing query: {query}")
    context = get_context(vectorstore, query, filter=filter)
    results = ask_query(context['context'], query)
    logger.info("Query processed and response generated.")
    return {
        "response": results['content'],
        "sources": list(set(context["sources"])),
    }
