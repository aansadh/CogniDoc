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
import logging
from rag.services.rag_services import RagServices

logger = logging.getLogger(__name__)

class SessionServices:
    """
    Provides services for managing user sessions, including creation and deletion.
    """

    def __init__(self, db, rag_services: RagServices):
        """
        Initializes the SessionServices instance.

        Args:
            vectorstore (Chroma): The vectorstore instance for document storage.
            db: The database connection instance.
        """
        self.db = db
        self.session_repository = SessionRepository(self.db)
        self.file_repository = FileRepository(self.db)
        self.rag_services = rag_services

    async def create_session(self, user_id: str, session_name: str) -> str:
        """
        Creates a new session for the user.

        Args:
            user_id (str): The ID of the user.
            session_name (str): The name of the session to be created.

        Returns:
            str: The ID of the created session.

        Raises:
            SessionServiceError: If the session creation fails.
        """
        logger.debug(f"Creating session: user_id={user_id}, session_name={session_name}")
        try:
            session_doc = SessionModel(user_id=user_id, session_name=session_name)
            session_id = await self.session_repository.add_session(session_doc)
            logger.info(f"Session created successfully: session_id={session_id}")
            return session_id
        except Exception as e:
            logger.error(f"Failed to create session: {e}", exc_info=True)
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
        logger.debug(f"Deleting session: session_id={session_id}")
        try:
            await self.rag_services.delete_doc_async({"session_id": session_id})
            logger.info(f"Vectorstore entries deleted for session_id={session_id}")

            await self.file_repository.delete_file_metadata(session_id=session_id)
            logger.info(f"File metadata deleted for session_id={session_id}")

            await self.session_repository.delete_session(session_id=session_id)
            logger.info(f"Session deleted successfully: session_id={session_id}")
        except Exception as e:
            logger.error(f"Failed to delete session: {e}", exc_info=True)
            raise SessionServiceError(f"Failed to delete session: {str(e)}")
        
    async def get_session(self, session_id: str) -> SessionModel:
        """
        Retrieves a session by its ID.

        Args:
            session_id (str): The ID of the session to retrieve.

        Returns:
            SessionModel: The session document.

        Raises:
            SessionServiceError: If the session retrieval fails.
        """
        logger.debug(f"Retrieving session: session_id={session_id}")
        try:
            session = await self.session_repository.get_session_by_id(session_id)
            if not session:
                logger.warning(f"Session not found: session_id={session_id}")
                raise SessionServiceError("Session not found")
            logger.info(f"Session retrieved successfully: session_id={session_id}")
            return session
        except Exception as e:
            logger.error(f"Failed to retrieve session: {e}", exc_info=True)
            raise SessionServiceError(f"Failed to retrieve session: {str(e)}")
