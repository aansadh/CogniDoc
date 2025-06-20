from langchain_chroma import Chroma
from repositories.file_repository import FileRepository
from rag.vectorstore_repository import VectorstoreRepository
from repositories.file_storage_repository import FileStorageRepository
from models.db_models import FileModel, VectorstoreModel
from exceptions import FileServiceError
import logging

logger = logging.getLogger(__name__)

class FileServices:
    """
    Provides services for file and content operations, including upload, deletion, and vectorstore interactions.
    """

    def __init__(self, vectorstore: Chroma, db):
        """
        Initializes the FileServices instance.

        Args:
            vectorstore (Chroma): The vectorstore instance for document storage.
            db: The database connection instance.
        """
        self.vectorstore = vectorstore
        self.db = db
        self.file_repository = FileRepository(self.db)
        self.vectorstore_repository = VectorstoreRepository(self.vectorstore)

    async def process_file_upload(
        self,
        session_id: str,
        content: bytes,
        file_name: str,
    ):
        """
        Processes file upload by storing metadata and adding the file to the vectorstore.

        Args:
            session_id (str): The session identifier.
            content: The file content.
            file_name (str): The name of the file.

        Returns:
            str: The file ID.

        Raises:
            FileServiceError: If the file upload fails.
        """
        file_path = None
        try:
            file_doc = FileModel(file_name=file_name, session_id=session_id)
            file_id = await self.file_repository.add_file_metadata(file_doc)

            _, file_path = await FileStorageRepository.create_and_write_file_async(
                content, str(file_id)
            )

            file_metadata = VectorstoreModel(
                file_id=file_id,
                file_name=file_name,
                session_id=session_id,
            )
            await self.vectorstore_repository.add_pdf_async(
                file_path, file_metadata.model_dump(exclude_unset=True)
            )

            return file_id
        except Exception as e:
            await self._rollback_add_file_metadata(session_id, file_id)
            raise FileServiceError(f"Failed to process file upload: {file_name}:  {e}")
        finally:
            self._cleanup_temp_file(file_path)

    async def process_content_upload(
        self,
        session_id: str,
        content: str,
        file_name: str,
    ):
        """
        Processes content upload by storing metadata and adding the content to the vectorstore.

        Args:
            session_id (str): The session identifier.
            content (str): The content to upload.
            file_name (str): The name of the content file.

        Returns:
            str: The file ID.

        Raises:
            FileServiceError: If the content upload fails.
        """
        if not content.strip():
            raise ValueError("Content cannot be empty.")

        file_id = None
        try:
            file_doc = FileModel(file_name=file_name, session_id=session_id)
            file_id = await self.file_repository.add_file_metadata(file_doc)

            file_metadata = VectorstoreModel(
                file_id=file_id,
                file_name=file_name,
                session_id=session_id,
            )
            await self.vectorstore_repository.add_content_async(
                content.strip(), file_metadata.model_dump(exclude_unset=True)
            )

            return file_id
        except Exception as e:
            await self._rollback_add_file_metadata(session_id, file_id)
            raise FileServiceError(
                f"Failed to process content upload: {file_name}: {e}"
            )

    async def process_file_deletion(
        self, session_id: str, file_id: str = None
    ):
        """
        Deletes a file and its associated vectorstore entry.

        Args:
            session_id (str): The session identifier.
            file_id (str, optional): The file ID to delete.
        """
        try:
            filter_criteria = {"file_id": file_id, "session_id": session_id}
            await self.vectorstore_repository.delete_doc_async(
                filter_criteria=filter_criteria
            )
            await self.file_repository.delete_file_metadata(session_id, file_id)
        except Exception as e:
            raise FileServiceError(
                f"Failed to delete file: {file_id} for session {session_id}: {e}"
            )

    ### helper internal methods --------------------------------------------------

    async def _rollback_add_file_metadata(self, session_id: str, file_id: str):
        if file_id:
            try:
                await self.file_repository.delete_file_metadata(session_id, file_id)
            except Exception as e:
                logger.error(
                    f"Failed to roll back file metadata for session {session_id} and file {file_id}: {e}",
                    exc_info=True,
                )

    def _cleanup_file(file_path: str):
        try:
            FileStorageRepository.delete_file(file_path)
        except Exception as e:
            logger.error(f"Failed to clean up temporary file.", exc_info=True)
