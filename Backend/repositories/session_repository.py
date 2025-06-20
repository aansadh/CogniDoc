from exceptions import NotFoundError, DatabaseOperationError
from bson.objectid import ObjectId
from models.db_models import SessionModel

class SessionRepository:
    """
    Handles database operations for user sessions, including adding and deleting session records.
    """

    def __init__(self, db):
        """
        Initializes the SessionRepository instance.

        Args:
            db: The database connection instance.
        """
        self.db = db
        self.collection = self.db["Sessions"]

    async def add_session(self, session_doc: SessionModel) -> str:
        """
        Adds a new session to the database.

        Args:
            session_doc (SessionModel): The session metadata to add.

        Returns:
            str: The ID of the inserted session record.

        Raises:
            DatabaseOperationError: If the operation fails.
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

        Args:
            session_id (str): The ID of the session to delete.

        Raises:
            NotFoundError: If the session is not found.
            DatabaseOperationError: If the operation fails.
        """
        try:
            result = await self.collectioon.delete_one({"_id": ObjectId(session_id)})
            if result.deleted_count == 0:
                raise NotFoundError(status_code=404, detail="Session not found")
            
        except Exception as e:
            raise DatabaseOperationError(status_code=500, detail=f"Error deleting session: {str(e)}")
        
    async def get_sessions_by_user_id(self, user_id: str) -> list[SessionModel]:
        """
        Retrieves all sessions for a given user ID.

        Args:
            user_id (str): The ID of the user whose sessions are to be retrieved.

        Returns:
            list: A list of session documents for the specified user.

        Raises:
            DatabaseOperationError: If the operation fails.
        """
        try:
            list_sessions = await self.collection.find({"user_id": user_id}).to_list(length=None)

            sessions = [session.model_validate(session) for session in list_sessions]

            return sessions
        except Exception as e:
            raise DatabaseOperationError(status_code=500, detail=f"Error retrieving sessions: {str(e)}")