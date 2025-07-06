from langchain_community.embeddings import (
    HuggingFaceInstructEmbeddings,
)
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import OllamaEmbeddings
from langchain_openai import OpenAIEmbeddings
import logging

logger = logging.getLogger(__name__)

def get_embedding_model(provider: str = 'ollama', model_name: str = 'nomic-embed-text'):
    """
    Synchronously retrieves the appropriate embedding model based on the provider.

    Args:
        provider (str): The name of the embedding provider (e.g., 'openai', 'huggingface', 'instructor', 'ollama').
        model_name (str, optional): The name of the model to use. Defaults to None.

    Returns:
        An instance of the embedding model.

    Raises:
        ValueError: If the provider is unsupported.
    """
    logger.debug(f"Retrieving embedding model for provider: {provider}")
    if provider == "openai":
        logger.info("Using OpenAI embeddings.")
        return OpenAIEmbeddings()
    
    elif provider == "huggingface":
        logger.info("Using HuggingFace embeddings.")
        return HuggingFaceEmbeddings(model_name=model_name or "all-MiniLM-L6-v2")
    
    elif provider == "instructor":
        logger.info("Using HuggingFace Instructor embeddings.")
        return HuggingFaceInstructEmbeddings(model_name=model_name or "hkunlp/instructor-large")
    
    elif provider == 'ollama':
        logger.info(f"Using Ollama embeddings.model_name: {model_name}")
        return OllamaEmbeddings(model=model_name or "nomic-embed-text")

    else:
        logger.error(f"Unsupported embedding provider: {provider}")
        raise ValueError(f"Unsupported embedding provider: {provider}")