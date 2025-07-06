class RagError(Exception):
    """Base class for all RAG-related errors."""
    pass

class EnvironmentError(RagError):
    """Raised when a required environment variable or config is missing."""
    pass

class VectorstoreError(RagError):
    """Base class for vectorstore-related errors."""
    pass

class VectorstoreInitError(VectorstoreError):
    """Raised when vectorstore instance is None."""
    pass

class DocumentProcessingError(VectorstoreError):
    """Raised when document loading/splitting fails."""
    pass

class ContextNotFoundError(VectorstoreError):
    """Raised when a context is not found in the vectorstore."""
    pass

class QueryProcessingError(Exception):
    """Raised when query processing fails."""
    pass

class LLMGenerationError(Exception):
    """Raised when LLM generation fails."""
    pass