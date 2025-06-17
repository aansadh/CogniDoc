from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional 

class Settings(BaseSettings):
    app_name: str = "Smart PDF QA API"
    api_version: str = "0.1.0"
    log_level: str = "INFO"
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