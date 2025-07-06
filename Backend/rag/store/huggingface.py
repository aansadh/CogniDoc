from .interfaces import LLMModel
import requests
from ..exceptions import QueryProcessingError, EnvironmentError
import asyncio
import logging

logger = logging.getLogger(__name__)

class HuggingFace(LLMModel):
    """
    A class for interacting with the Hugging Face API to generate responses based on prompts.
    """

    def __init__(self, url: str, headers: dict = None, model: str = None, role: str = "user", **kwargs):
        """
        Initializes the HuggingFace instance.

        Args:
            url (str): The API endpoint URL.
            headers (dict, optional): HTTP headers for the API request. Defaults to None.
            model (str, optional): The model to use for generation. Defaults to "microsoft/phi-4".
            role (str, optional): The role of the user in the conversation. Defaults to "user".
            **kwargs: Additional parameters for the API request.
        """
        self.url = url.strip()
        self.headers = headers or { "Content-Type": "application/json" }
        self.model = model or "microsoft/phi-4"
        self.role = role
        self.json = {
            "model": self.model,
            "messages": [
                {"role": self.role, "content": ""}
            ],
            "stream": False,
            **kwargs
        }
        logger.info(f"HuggingFace instance initialized with model: {self.model}, role: {self.role}")

    async def generate_async(self, prompt: str) -> str:
        """
        Asynchronously generates a response from the Hugging Face API based on the given prompt.

        Args:
            prompt (str): The input prompt for the model.

        Returns:
            str: The generated response from the model.

        Raises:
            ValueError: If the prompt is empty or whitespace.
            QueryProcessingError: If there is an error during the API request.
        """
        logger.debug(f"Starting async generation for prompt: {prompt}")

        def blocking_generate():
            if not prompt.strip():
                logger.error("Prompt cannot be empty or whitespace.")
                raise ValueError("Prompt cannot be empty or whitespace.")
            json = self.json.copy()
            json['messages'][0]['content'] = prompt.strip() or ""
            try:
                logger.info("Sending request to Hugging Face API.")
                response = requests.post(self.url, headers=self.headers, json=json)
                response.raise_for_status()
                logger.info("Response received successfully from Hugging Face API.")
                return response.json()['choices'][0]['message']['content']
            except requests.HTTPError as e:
                logger.error(f"Model API error: {e.response.status_code} - {e.response.text}", exc_info=True)
                raise QueryProcessingError(f"Model API error: {e.response.status_code} - {e.response.text}")
            except requests.RequestException as e:
                logger.error(f"Request to model API failed: {str(e)}", exc_info=True)
                raise QueryProcessingError(f"Request to model API failed: {str(e)}")
            except Exception as e:
                logger.error(f"Unexpected error during query: {str(e)}", exc_info=True)
                raise QueryProcessingError(f"Unexpected error during query: {str(e)}")

        result = await asyncio.to_thread(blocking_generate)
        logger.debug("Async generation completed successfully.")
        return result
