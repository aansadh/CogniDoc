import logging

logger = logging.getLogger(__name__)

def get_llm(provider: str = 'ollama', model: str = 'phi3:mini', url: str = 'http://localhost:11434/api/generate', headers: dict = None, **kwargs):
    """
    Synchronously retrieves the appropriate LLM model based on the provider.

    Args:
        provider (str): The name of the LLM provider (e.g., 'ollama', 'huggingface').
        model (str): The model name to use.
        url (str, optional): The URL for the LLM API.
        headers (dict, optional): Optional headers for the API request.
        **kwargs: Additional keyword arguments for the model initialization.

    Returns:
        An instance of the LLMModel.

    Raises:
        ValueError: If the provider is unsupported.
    """
    logger.debug(f"Retrieving LLM for provider: {provider}, model: {model}")
    if provider == 'ollama':
        from .ollama import Ollama
        logger.info("Using Ollama LLM.")
        return Ollama(url=url, headers=headers, model=model, **kwargs)
    elif provider == 'huggingface':
        from .huggingface import HuggingFace
        logger.info("Using HuggingFace LLM.")
        return HuggingFace(url=url, headers=headers, model=model, **kwargs)
    else:
        logger.error(f"Unsupported LLM provider: {provider}")
        raise ValueError(f"Unsupported LLM provider: {provider}")