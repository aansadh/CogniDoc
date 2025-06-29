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

class ResourceNotFoundError(RepositoryError):
    """
    Custom exception for resource not found errors.
    Raised by repositories when a resource is not found.
    """
    def __init__(self, resource_type: str="Resource", resource_id: str=None):
        """
        Initializes the ResourceNotFoundError.

        Args:
            resource_type (str): The type of the resource that was not found.
            resource_id (str, optional): The ID of the resource that was not found.
        """
        self.resource_type = resource_type
        self.resource_id = resource_id
        super().__init__(f"{resource_type} with ID '{resource_id}' not found." if resource_id else f"{resource_type} not found.")

class FileOperationError(RepositoryError):
    """
    Custom exception for file operation errors.
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

