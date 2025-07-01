"""
Service layer for handling file-related operations in the Smart PDF QA API application.
"""

from langchain_chroma import Chroma
from repositories.file_repository import FileRepository
from rag.vectorstore_repository import VectorstoreRepository
from repositories.file_storage_repository import FileStorageRepository
from models.db_models import FileModel, VectorstoreModel
from exceptions import FileServiceError, ResourceNotFoundError
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
        logger.debug(f"Processing file upload: session_id={session_id}, file_name={file_name}")
        file_path = None
        try:
            file_doc = FileModel(file_name=file_name, session_id=session_id)
            file_id = await self.file_repository.add_file_metadata(file_doc)

            logger.info(f"File metadata added successfully: file_id={file_id}")

            _, file_path = await FileStorageRepository.create_and_write_file_async(
                content, str(file_id)
            )

            logger.info(f"File written to storage: file_path={file_path}")

            file_metadata = VectorstoreModel(
                file_id=file_id,
                file_name=file_name,
                session_id=session_id,
            )
            await self.vectorstore_repository.add_pdf_async(
                file_path, file_metadata.model_dump(exclude_unset=True)
            )

            logger.info(f"File added to vectorstore: file_id={file_id}")
            return file_id
        except Exception as e:
            logger.error(f"Error during file upload processing: {e}", exc_info=True)
            await self._rollback_add_file_metadata(session_id, file_id)
            raise FileServiceError(f"Failed to process file upload: {file_name}:  {e}")
        finally:
            self._cleanup_file(file_path)

    async def process_content_upload(
        self,
        session_id: str,
        content: str,
        file_name: str,
    ):
        logger.debug(f"Processing content upload: session_id={session_id}, file_name={file_name}")
        if not content.strip():
            logger.warning("Content is empty. Raising ValueError.")
            raise ValueError("Content cannot be empty.")

        file_id = None
        try:
            file_doc = FileModel(file_name=file_name, session_id=session_id)
            file_id = await self.file_repository.add_file_metadata(file_doc)

            logger.info(f"File metadata added successfully: file_id={file_id}")

            file_metadata = VectorstoreModel(
                file_id=file_id,
                file_name=file_name,
                session_id=session_id,
            )
            await self.vectorstore_repository.add_content_async(
                content.strip(), file_metadata.model_dump(exclude_unset=True)
            )

            logger.info(f"Content added to vectorstore: file_id={file_id}")
            return file_id
        except Exception as e:
            logger.error(f"Error during content upload processing: {e}", exc_info=True)
            await self._rollback_add_file_metadata(session_id, file_id)
            raise FileServiceError(
                f"Failed to process content upload: {file_name}: {e}"
            )

    async def process_file_deletion(
        self, session_id: str, file_id: str = None
    ):
        logger.debug(f"Processing file deletion: session_id={session_id}, file_id={file_id}")
        try:
            filter_criteria = {"$and": [{"file_id": file_id}, {"session_id": session_id}]}
            await self.vectorstore_repository.delete_doc_async(
                filter_criteria=filter_criteria
            )
            logger.info(f"Vectorstore entry deleted: file_id={file_id}")

            await self.file_repository.delete_file_metadata(session_id, file_id)
            logger.info(f"File metadata deleted: file_id={file_id}")
        except ResourceNotFoundError as e:
            logger.warning(f"Resource not found during file deletion: {e}")
            raise
        except Exception as e:
            logger.error(f"Error during file deletion processing: {e}", exc_info=True)
            raise FileServiceError(
                f"Failed to delete file: {file_id} for session {session_id}: {e}"
            )

    async def _rollback_add_file_metadata(self, session_id: str, file_id: str):
        logger.debug(f"Rolling back file metadata addition: session_id={session_id}, file_id={file_id}")
        if file_id:
            try:
                await self.file_repository.delete_file_metadata(session_id, file_id)
                logger.info(f"Rollback successful: file_id={file_id}")
            except Exception as e:
                logger.error(
                    f"Failed to roll back file metadata for session {session_id} and file {file_id}: {e}",
                    exc_info=True,
                )

    @staticmethod
    def _cleanup_file(file_path: str):
        logger.debug(f"Cleaning up file: file_path={file_path}")
        try:
            FileStorageRepository.delete_file(file_path)
            logger.info(f"File cleanup successful: file_path={file_path}")
        except Exception as e:
            logger.error(f"Failed to clean up temporary file: {e}", exc_info=True)
