"""
This module provides the FileRepository class for handling database operations related to file metadata.

The FileRepository class includes methods for adding, deleting, and retrieving file records from the database.
It interacts with the database collection named "Files" and ensures proper error handling for database operations.
"""

from models.db_models import FileModel
from bson.objectid import ObjectId
from typing import Optional, List
from exceptions import DatabaseOperationError, ResourceNotFoundError
import logging

logger = logging.getLogger(__name__)

class FileRepository:
    """
    Handles database operations for file metadata, including adding, deleting, and retrieving file records.
    """

    def __init__(self, db):
        """
        Initializes the FileRepository instance.

        Args:
            db: The database connection instance.
        """
        self.db = db
        self.collection = self.db["Files"]


    async def add_file_metadata(self, file_doc: FileModel) -> str:
        """
        Adds file metadata to the database.

        Args:
            file_doc (FileModel): The file metadata to add.

        Returns:
            str: The ID of the inserted file record.

        Raises:
            DatabaseOperationError: If the operation fails.
        """
        logger.debug("Adding file metadata to the database")
        try:
            result = await self.collection.insert_one(file_doc.model_dump(exclude_unset=True, by_alias=True))

            if not result or not result.acknowledged or not result.inserted_id:
                logger.error("Failed to insert file metadata into the database")
                raise DatabaseOperationError("Failed to insert file metadata into the database.")

            logger.info(f"File metadata added successfully with ID: {result.inserted_id}")
            return str(result.inserted_id)
        except DatabaseOperationError as e:
            logger.error(f"Database operation error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"An error occurred while adding file metadata: {str(e)}")
            raise DatabaseOperationError(f"An error occurred while adding file metadata: {str(e)}")


    async def delete_file_metadata(self, session_id: str, file_id: Optional[str] = None):
        """
        Deletes file metadata from the database by session ID and optionally by file ID.

        Args:
            session_id (str): The session identifier.
            file_id (Optional[str]): The file ID to delete. Defaults to None.

        Returns:
            int: The number of deleted records.

        Raises:
            ResourceNotFoundError: If no matching file is found.
            DatabaseOperationError: If the operation fails.
        """
        logger.debug(f"Deleting file metadata for session_id: {session_id}, file_id: {file_id}")
        try:
            query = {"session_id": session_id}
            if file_id:
                query["_id"] = ObjectId(file_id)
                result = await self.collection.delete_one(query)
            else:
                result = await self.collection.delete_many(query)

            if file_id and result.deleted_count == 0:
                logger.warning(f"No files found for session_id: {session_id} and file_id: {file_id}")
                raise ResourceNotFoundError(resource_type='File', resource_id=file_id or session_id)

            logger.info(f"Deleted {result.deleted_count} file(s) for session_id: {session_id}, file_id: {file_id}")
            return result.deleted_count
        except ResourceNotFoundError as e:
            logger.warning(f"Resource not found: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"An error occurred while deleting file metadata: {str(e)}")
            raise DatabaseOperationError(f"An error occurred while deleting file metadata: {str(e)}")


    async def get_files_by_session_id(self, session_id: str) -> List[dict]:
        """
        Retrieves file metadata from the database by session ID.

        Args:
            session_id (str): The session identifier.

        Returns:
            list: A list of file metadata records.

        Raises:
            DatabaseOperationError: If the operation fails.
        """
        logger.debug(f"Retrieving files for session_id: {session_id}")
        try:
            files = await self.collection.find({"session_id": session_id}).to_list(length=None)

            for file in files:
                if '_id' in file and isinstance(file['_id'], ObjectId):
                    file["file_id"] = str(file["_id"])
                    del file["_id"]

            logger.info(f"Retrieved {len(files)} file(s) for session_id: {session_id}")
            return files
        except Exception as e:
            logger.error(f"An error occurred while retrieving file metadata: {str(e)}")
            raise DatabaseOperationError(f"An error occurred while retrieving file metadata: {str(e)}")