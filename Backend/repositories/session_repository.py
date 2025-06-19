from exceptions import NotFoundError, DatabaseOperationError
from bson.objectid import ObjectId
from models.db_models import SessionModel

class SessionRepository:
    def __init__(self, db):
        self.db = db
        self.collection = self.db["Sessions"]

    async def insert_session(self, session_doc: SessionModel) -> str:
        """
        Adds a new session to the database.
        """
        try:
            session_data = session_doc.model_dump(exclude_unset=True, by_alias=True)
            result = await self.collection.insert_one(session_data)

            if not result or not result.acknowledged or not result.inserted_id:
                raise DatabaseOperationError(status_code=500, detail="Failed to insert session into the database.")

            return str(result.inserted_id)
        except Exception as e:
            raise DatabaseOperationError(status_code=500, detail=f"Error inserting session: {str(e)}")

    async def delete_session(self, session_id: str):
        """
        Deletes a session from the database by its ID.
        """
        try:
            result = await self.collectioon.delete_one({"_id": ObjectId(session_id)})
            if result.deleted_count == 0:
                raise NotFoundError(status_code=404, detail="Session not found")
            
        except Exception as e:
            raise DatabaseOperationError(status_code=500, detail=f"Error deleting session: {str(e)}")