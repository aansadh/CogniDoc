class DatabaseOperationError(Exception):
    """
    Custom exception for database operation CRUD errors.
    """
    pass

class NotFoundError(Exception):
    """
    Custom exception for not found errors in the database.
    """
    pass

class FileOperationError(Exception):
    """
    Custom exception for file operation errors.
    """
    pass