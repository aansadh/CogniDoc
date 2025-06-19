from models.db_models import FileModel
from bson.objectid import ObjectId
from typing import Optional
from exceptions import DatabaseOperationError, NotFoundError

class FileRepository:
    def __init__(self, db):
        self.db = db
        self.collection = self.db["Files"]

    async def insert_file_metadata(self, file_doc: FileModel) -> str:        
        """
        Adds file metadata to the database.
        """
        try:
            # file_doc = FileModel(
            #     file_name=file_name,
            #     session_id=session_id,
            #     created_at=datetime.now(timezone.utc)
            # )
            result = await self.collection.insert_one(file_doc.model_dump(exclude_unset=True, by_alias=True))

            if not result or not result.acknowledged or not result.inserted_id:
                raise DatabaseOperationError("Failed to insert file metadata into the database.")
            
            return str(result.inserted_id)
        except DatabaseOperationError:
            raise
        except Exception as e:
            raise DatabaseOperationError(f"An error occurred while adding file metadata: {str(e)}")


    async def delete_file_metadata(self, session_id: str, file_id: Optional[str] = None):
        try:
            query = {"session_id": session_id}
            if file_id:
                query["_id"] = ObjectId(file_id)
                result = await self.collection.delete_one(query)
            else:
                result = await self.collection.delete_many(query)

            if result.deleted_count == 0:
                raise NotFoundError("File not found in the database.")
            
            return result.deleted_count
        except NotFoundError:
            raise
        except Exception as e:
            raise DatabaseOperationError(f"An error occurred while deleting file metadata: {str(e)}")
