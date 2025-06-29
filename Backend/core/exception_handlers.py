"""
Custom exception handlers for the Smart PDF QA API application.
"""

import logging
from fastapi import Request, status
from fastapi.responses import JSONResponse
from exceptions import *
from rag.exceptions import *

logger = logging.getLogger(__name__)

def _get_root_cause_detail(exc: Exception) -> str:
    """
    Finds the root cause of an exception and returns its string representation for detail.

    Args:
        exc (Exception): The exception to analyze.

    Returns:
        str: The root cause detail of the exception.
    """
    current_exc = exc
    while hasattr(current_exc, '__cause__') and current_exc.__cause__ is not None:
        current_exc = current_exc.__cause__
    return f"Root cause: {current_exc.__class__.__name__} - {str(current_exc)}"

async def resource_not_found_exception_handler(request: Request, exc: ResourceNotFoundError):
    """
    Handles ResourceNotFoundError exceptions.

    Args:
        request (Request): The incoming HTTP request.
        exc (ResourceNotFoundError): The exception instance.

    Returns:
        JSONResponse: The response with error details.
    """
    detail = f"The requested resource was not found: {_get_root_cause_detail(exc)}"
    logger.info(f"Client Error: Resource Not Found ({request.method} {request.url}): {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": detail},
    )

async def context_not_found_error_handler(request: Request, exc: ContextNotFoundError):
    """
    Handles ContextNotFoundError exceptions.

    Args:
        request (Request): The incoming HTTP request.
        exc (ContextNotFoundError): The exception instance.

    Returns:
        JSONResponse: The response with error details.
    """
    detail = f"The requested context was not found: {_get_root_cause_detail(exc)}"
    logger.info(f"Client Error: Context Not Found ({request.method} {request.url}): {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": detail},
    )

async def value_error_handler(request: Request, exc: ValueError):
    """
    Handles ValueError exceptions.

    Args:
        request (Request): The incoming HTTP request.
        exc (ValueError): The exception instance.

    Returns:
        JSONResponse: The response with error details.
    """
    # This handler will catch ValueError. If a service/repository wraps an original
    # ValueError, _get_root_cause_detail will extract it.
    detail = f"Invalid input provided: {_get_root_cause_detail(exc)}"
    logger.info(f"Client Error: Validation Error ({request.method} {request.url}): {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": detail},
    )

# 5xx Server Errors (often related to service unavailability or internal logic failures)
async def environment_error_handler(request: Request, exc: EnvironmentError):
    """
    Handles EnvironmentError exceptions.

    Args:
        request (Request): The incoming HTTP request.
        exc (EnvironmentError): The exception instance.

    Returns:
        JSONResponse: The response with error details.
    """
    # This indicates a server-side misconfiguration or missing dependency
    detail = f"Server configuration error: {_get_root_cause_detail(exc)}. Please contact support."
    logger.error(f"Server Error: Environment Configuration ({request.method} {request.url}): {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, # Misconfiguration is a server fault
        content={"detail": detail},
    )

async def database_operation_error_handler(request: Request, exc: DatabaseOperationError):
    """
    Handles DatabaseOperationError exceptions.

    Args:
        request (Request): The incoming HTTP request.
        exc (DatabaseOperationError): The exception instance.

    Returns:
        JSONResponse: The response with error details.
    """
    detail = f"A database operation failed: {_get_root_cause_detail(exc)}. Please try again later."
    logger.error(f"Server Error: Database Operation ({request.method} {request.url}): {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE, # Service unavailable due to DB issue
        content={"detail": detail},
    )

async def file_storage_error_handler(request: Request, exc: FileStorageError):
    """
    Handles FileStorageError exceptions.

    Args:
        request (Request): The incoming HTTP request.
        exc (FileStorageError): The exception instance.

    Returns:
        JSONResponse: The response with error details.
    """
    detail = f"A file storage service error occurred: {_get_root_cause_detail(exc)}. Please try again later."
    logger.error(f"Server Error: File Storage ({request.method} {request.url}): {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE, # Service unavailable due to storage issue
        content={"detail": detail},
    )

async def vectorstore_init_error_handler(request: Request, exc: VectorstoreInitError):
    """
    Handles VectorstoreInitError exceptions.

    Args:
        request (Request): The incoming HTTP request.
        exc (VectorstoreInitError): The exception instance.

    Returns:
        JSONResponse: The response with error details.
    """
    detail = f"Vectorstore initialization failed: {_get_root_cause_detail(exc)}. This is a server configuration issue."
    logger.error(f"Server Error: Vectorstore Initialization ({request.method} {request.url}): {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": detail},
    )

async def document_processing_error_handler(request: Request, exc: DocumentProcessingError):
    """
    Handles DocumentProcessingError exceptions.

    Args:
        request (Request): The incoming HTTP request.
        exc (DocumentProcessingError): The exception instance.

    Returns:
        JSONResponse: The response with error details.
    """
    detail = f"Document processing failed: {_get_root_cause_detail(exc)}. Please check the content format."
    logger.error(f"Server Error: Document Processing ({request.method} {request.url}): {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": detail},
    )

async def query_processing_error_handler(request: Request, exc: QueryProcessingError):
    """
    Handles QueryProcessingError exceptions.

    Args:
        request (Request): The incoming HTTP request.
        exc (QueryProcessingError): The exception instance.

    Returns:
        JSONResponse: The response with error details.
    """
    detail = f"Failed to process query: {_get_root_cause_detail(exc)}. Please try again."
    logger.error(f"Server Error: Query Processing ({request.method} {request.url}): {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": detail},
    )

# Generic handlers for broader categories (caught if no more specific handler matches)
async def file_operation_error_handler(request: Request, exc: FileOperationError):
    """
    Handles FileOperationError exceptions.

    Args:
        request (Request): The incoming HTTP request.
        exc (FileOperationError): The exception instance.

    Returns:
        JSONResponse: The response with error details.
    """
    detail = f"A generic file operation error occurred: {_get_root_cause_detail(exc)}"
    logger.error(f"Server Error: File Operation Generic ({request.method} {request.url}): {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": detail},
    )

async def repository_error_handler(request: Request, exc: RepositoryError):
    """
    Handles RepositoryError exceptions.

    Args:
        request (Request): The incoming HTTP request.
        exc (RepositoryError): The exception instance.

    Returns:
        JSONResponse: The response with error details.
    """
    detail = f"A generic repository error occurred: {_get_root_cause_detail(exc)}"
    logger.error(f"Server Error: Repository Generic ({request.method} {request.url}): {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": detail},
    )

async def file_service_error_handler(request: Request, exc: FileServiceError):
    """
    Handles FileServiceError exceptions.

    Args:
        request (Request): The incoming HTTP request.
        exc (FileServiceError): The exception instance.

    Returns:
        JSONResponse: The response with error details.
    """
    detail = f"A file service error occurred: {_get_root_cause_detail(exc)}. This indicates an issue with file processing logic."
    logger.error(f"Server Error: File Service Generic ({request.method} {request.url}): {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": detail},
    )

async def vectorstore_error_handler(request: Request, exc: VectorstoreError):
    """
    Handles VectorstoreError exceptions.

    Args:
        request (Request): The incoming HTTP request.
        exc (VectorstoreError): The exception instance.

    Returns:
        JSONResponse: The response with error details.
    """
    detail = f"A generic vectorstore error occurred: {_get_root_cause_detail(exc)}. This indicates an issue with the vector storage system."
    logger.error(f"Server Error: Vectorstore Generic ({request.method} {request.url}): {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": detail},
    )

# The ultimate catch-all for your custom BaseError hierarchy
async def base_error_handler(request: Request, exc: BaseError):
    """
    Handles BaseError exceptions.

    Args:
        request (Request): The incoming HTTP request.
        exc (BaseError): The exception instance.

    Returns:
        JSONResponse: The response with error details.
    """
    detail = f"An unexpected application error occurred: {_get_root_cause_detail(exc)}. Please contact support."
    logger.error(f"Server Error: Base Error Fallback ({request.method} {request.url}): {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": detail},
    )

# Final catch-all for ANY Python Exception not explicitly handled by FastAPI's defaults or your custom handlers
async def unhandled_exception_handler(request: Request, exc: Exception):
    """
    Handles unhandled exceptions.

    Args:
        request (Request): The incoming HTTP request.
        exc (Exception): The exception instance.

    Returns:
        JSONResponse: The response with error details.
    """
    logger.exception(f"CRITICAL: Unhandled system exception for {request.method} {request.url}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected internal server error occurred. Please try again later"},
    )


EXCEPTION_HANDLERS = [
    (ResourceNotFoundError, resource_not_found_exception_handler),
    (ContextNotFoundError, context_not_found_error_handler),
    (ValueError, value_error_handler), 

    (EnvironmentError, environment_error_handler),
    (DatabaseOperationError, database_operation_error_handler),
    (FileStorageError, file_storage_error_handler),
    (VectorstoreInitError, vectorstore_init_error_handler),
    (DocumentProcessingError, document_processing_error_handler),
    (QueryProcessingError, query_processing_error_handler),

    (FileOperationError, file_operation_error_handler),
    (RepositoryError, repository_error_handler), 
    (FileServiceError, file_service_error_handler),
    (VectorstoreError, vectorstore_error_handler), 
    (BaseError, base_error_handler),
    (Exception, unhandled_exception_handler),
]