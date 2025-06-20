class BaseError(Exception):
    """
    Base class for all custom exceptions.
    """
    pass

### File Service Layer Exceptions ######################################

class FileServiceError(BaseError):
    """
    Custom exception for file service errors.
    Raised by FileServices.
    """
    pass

class SessionServiceError(BaseError):
    """
    Custom exception for session service errors.
    Raised by SessionServices.
    """
    pass

### Repository Layer Exceptions #######################################

class RepositoryError(BaseError):
    """
    Base class for repository-related errors.
    """
    pass

class FileOperationError(RepositoryError):
    """
    Custom exception for file operation errors.
    """
    pass

class FileNotFoundError(FileOperationError):
    """
    Custom exception for file not found errors.
    Raised by FileRepository.
    """
    pass

class FileStorageError(RepositoryError):
    """
    Custom exception for file storage errors. 
    Raised by FileStorageRepository.
    """
    pass

class DatabaseOperationError(RepositoryError):
    """
    Custom exception for database operation CRUD errors.
    Raised by FileRepository.
    """
    pass

# Note: For vectorstore-related exceptions, refer to `rag.exceptions` module.

