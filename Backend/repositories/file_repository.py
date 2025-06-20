from models.db_models import FileModel
from bson.objectid import ObjectId
from typing import Optional
from exceptions import DatabaseOperationError, FileNotFoundError

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
        try:
            result = await self.collection.insert_one(file_doc.model_dump(exclude_unset=True, by_alias=True))

            if not result or not result.acknowledged or not result.inserted_id:
                raise DatabaseOperationError("Failed to insert file metadata into the database.")
            
            return str(result.inserted_id)
        except DatabaseOperationError:
            raise
        except Exception as e:
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
            FileNotFoundError: If no matching file is found.
            DatabaseOperationError: If the operation fails.
        """
        try:
            query = {"session_id": session_id}
            if file_id:
                query["_id"] = ObjectId(file_id)
                result = await self.collection.delete_one(query)
            else:
                result = await self.collection.delete_many(query)

            if result.deleted_count == 0:
                raise FileNotFoundError("File not found in the database.")
            
            return result.deleted_count
        except FileNotFoundError:
            raise 
        except Exception as e:
            raise DatabaseOperationError(f"An error occurred while deleting file metadata: {str(e)}")

    async def get_file_by_session_id(self, session_id: str):
        """
        Retrieves file metadata from the database by session ID.

        Args:
            session_id (str): The session identifier.

        Returns:
            list: A list of file metadata records.

        Raises:
            FileNotFoundError: If no files are found for the given session ID.
            DatabaseOperationError: If the operation fails.
        """
        try:
            files = await self.collection.find({"session_id": session_id}).to_list(length=None)
            if not files or len(files) == 0:
                raise FileNotFoundError("No files found for the given session ID.")
            return files
        except FileNotFoundError:
            raise
        except Exception as e:
            raise DatabaseOperationError(f"An error occurred while retrieving file metadata: {str(e)}")

