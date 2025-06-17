from langchain_community.embeddings import (
    HuggingFaceInstructEmbeddings
)
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import OpenAIEmbeddings

def get_embedding_model(provider: str, model_name: str = None):
    if provider == "openai":
        return OpenAIEmbeddings()
    
    elif provider == "huggingface":
        return HuggingFaceEmbeddings(model_name=model_name or "all-MiniLM-L6-v2")
    
    elif provider == "instructor":
        return HuggingFaceInstructEmbeddings(model_name=model_name or "hkunlp/instructor-large")
    
    else:
        raise ValueError(f"Unsupported embedding provider: {provider}")