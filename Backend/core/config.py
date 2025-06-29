from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional 

class Settings(BaseSettings):
    """
    Configuration settings for the Smart PDF QA API application.

    Attributes:
        app_name (str): The name of the application.
        api_version (str): The version of the API.
        log_level (str): The logging level for the application.
        uploads_folder (str): The folder where uploaded files are stored.

        openai_api_key (Optional[str]): The API key for OpenAI integration.
        embedding_provider (str): The provider for embedding models.
        embedding_model (str): The embedding model to use.
        huggingface_api_key (Optional[str]): The API key for Hugging Face integration.
        hf_inference_api_url (Optional[str]): The URL for Hugging Face inference API.

        mongodb_uri (str): The URI for connecting to MongoDB.
        mongodb_db (str): The name of the MongoDB database.

        clerk_secret_key (str): The secret key for Clerk authentication.
        clerk_jwks_url (Optional[str]): The JWKS URL for Clerk authentication.
        clerk_frontend_api_url (Optional[str]): The frontend API URL for Clerk.
        clerk_backend_api_url (Optional[str]): The backend API URL for Clerk.

        jwt_secret (str): The secret key for JWT authentication.
        jwt_algorithm (str): The algorithm used for JWT authentication.

        model_config (SettingsConfigDict): Configuration for the settings model.
    """
    app_name: str = "Smart PDF QA API"
    api_version: str = "0.1.0"
    log_level: str = "INFO"  # Options: INFO, DEBUG, WARNING, ERROR, CRITICAL
    uploads_folder: str = "data" 

    openai_api_key: Optional[str] = None 
    embedding_provider: str = "huggingface"
    embedding_model: str = "intfloat/e5-small-v2"
    huggingface_api_key: Optional[str] = None 
    hf_inference_api_url: Optional[str] = None 

    mongodb_uri: str
    mongodb_db: str

    clerk_secret_key: str
    clerk_jwks_url: Optional[str] = None 
    clerk_frontend_api_url: Optional[str] = None
    clerk_backend_api_url: Optional[str] = None

    jwt_secret: str
    jwt_algorithm: str = "HS256"

    model_config = SettingsConfigDict(
        env_file=".env",             
        env_file_encoding='utf-8',   
        case_sensitive=False,       
        extra='ignore',             
        # env_prefix='MYAPP_'        
    )

settings = Settings()
"""
Global instance of the `Settings` class for accessing application configuration.
"""