"""
This module provides services for managing user sessions, including creation and deletion.
It interacts with the database, vectorstore, and file repository to ensure session data is handled efficiently.
"""

from langchain_chroma import Chroma
from models.db_models import SessionModel
from repositories.session_repository import SessionRepository
from exceptions import SessionServiceError
from rag.vectorstore_repository import VectorstoreRepository
from repositories.file_repository import FileRepository

class SessionServices:
    """
    Provides services for managing user sessions, including creation and deletion.
    """

    def __init__(self, vectorstore: Chroma, db):
        """
        Initializes the SessionServices instance.

        Args:
            vectorstore (Chroma): The vectorstore instance for document storage.
            db: The database connection instance.
        """
        self.vectorstore = vectorstore
        self.db = db
        self.session_repository = SessionRepository(self.db)
        self.vectorstore_repository = VectorstoreRepository(self.vectorstore)
        self.file_repository = FileRepository(self.db)

    async def create_session(self, user_id: str) -> str:
        """
        Creates a new session for the user.

        Args:
            user_id (str): The ID of the user.

        Returns:
            str: The ID of the created session.

        Raises:
            SessionServiceError: If the session creation fails.
        """
        try:
            session_doc = SessionModel(user_id=user_id)
            session_id = await self.session_repository.add_session(session_doc)
            return session_id
        except Exception as e:
            raise SessionServiceError(f"Failed to create session: {str(e)}")
        
    async def delete_session(self, session_id: str):
        """
        Deletes a session and its associated data.

        Args:
            session_id (str): The ID of the session to delete.

        Raises:
            SessionServiceError: If the session deletion fails.

        Note:
            Future consideration: Implement transactional delete to make this operation atomic.
        """
        try:
            await self.vectorstore_repository.delete_doc_async({"session_id": session_id})
            await self.file_repository.delete_file_metadata(session_id)
            await self.session_repository.delete_session(session_id)
        except Exception as e:
            raise SessionServiceError(f"Failed to delete session: {str(e)}")
