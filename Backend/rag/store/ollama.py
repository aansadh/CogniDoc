from .interfaces import LLMModel
import requests
from ..exceptions import LLMGenerationError
from ..utils import run_in_threadpool, log_duration
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class Ollama(LLMModel):
    """
    A class for interacting with the Ollama API to generate responses based on prompts.
    """

    def __init__(self, url: str, headers: dict = None, model: str = None, **kwargs):
        """
        Initializes the Ollama instance.

        Args:
            url (str): The API endpoint URL.
            headers (dict, optional): HTTP headers for the API request. Defaults to None.
            model (str, optional): The model to use for generation. Defaults to "phi3:mini".
            **kwargs: Additional parameters for the API request.
        """
        self.url = url.strip() if url else "http://localhost:11434/api/chat"
        self.headers = headers or { "Content-Type": "application/json" }
        self.model = model or "phi3:mini"
        self.default_params = kwargs
        logger.info(f"Ollama instance initialized with model: {self.model}")

    @log_duration
    @run_in_threadpool
    def _make_ollama_request(self, json: dict):
        """
        Makes a request to the Ollama API with the given JSON payload.

        Args:
            json (dict): The JSON payload for the API request.

        Returns:
            dict: The JSON response from the API.

        Raises:
            LLMGenerationError: If there is an error during the API request.
        """
        try:
            logger.debug(f"Sending request to Ollama API with payload: {json}")
            response = requests.post(self.url, headers=self.headers, json=json)
            response.raise_for_status()
            logger.info("Response received successfully from Ollama API.")
            return response.json()
        except requests.HTTPError as e:
            logger.error(f"Model API error: {e.response.status_code} - {e.response.text}", exc_info=True)
            raise LLMGenerationError(f"Model API error: {e.response.status_code} - {e.response.text}")
        except requests.RequestException as e:
            logger.error(f"Request to model API failed: {str(e)}", exc_info=True)
            raise LLMGenerationError(f"Request to model API failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during query: {str(e)}", exc_info=True)
            raise LLMGenerationError(f"Unexpected error during query: {str(e)}")

    @log_duration
    async def generate_async(self, messages: List[Dict[str, str]]) -> Dict[str, Any]: # Updated signature to match protocol
        """
        Generates a response from the Ollama chat model using a list of messages.
        This method is synchronous but executed in a thread pool via the decorator.

        Args:
            messages (List[Dict[str, str]]): A list of messages for the conversation.

        Returns:
            Dict[str, Any]: A dictionary containing the generated response.
        """
        logger.debug(f"Invoking Ollama model: {self.model} with messages: {messages[:1]}...")
        
        json = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            **self.default_params
        }
        ollama_response = await self._make_ollama_request(json=json)

        if ollama_response and 'message' in ollama_response:
            logger.debug(f"Ollama response received: {ollama_response}")
            response_content = ollama_response['message']['content']
            logger.info("Ollama response generated successfully.")
            return {"content": response_content} 
        else:
            logger.error(f"Unexpected Ollama response format: {ollama_response}")
            raise LLMGenerationError(f"Unexpected Ollama response format: {ollama_response}")
