from typing import Protocol, List, Dict, Any
from abc import abstractmethod
import logging

logger = logging.getLogger(__name__)

class EmbeddingModel(Protocol):
    """
    Protocol for embedding models that convert text into numerical representations.
    """

    def embed(self, text: str) -> list[float]:
        """
        Embeds the given text and returns a list of floats.

        Args:
            text (str): The text to embed.

        Returns:
            list[float]: A list of numerical values representing the embedded text.
        """
        pass

class LLMModel(Protocol):
    """
    Protocol for large language models (LLMs) that generate text based on prompts.
    """

    @abstractmethod
    async def generate_async(self, messages: List[Dict[str, str]]) -> Dict[str, Any]: 
        """
        Generates text based on the given messages.

        Args:
            messages (List[Dict[str, str]]): A list of messages for the model.

        Returns:
            Dict[str, Any]: The generated response from the model, typically {'content': '...'}.
        """
        pass 