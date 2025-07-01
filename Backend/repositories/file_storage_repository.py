"""
This module provides the FileStorageRepository class for handling file storage operations.

The FileStorageRepository class includes methods for creating, writing, and deleting files in the file system.
It ensures proper error handling and logging for file operations.
"""

import os, time, random
from pathlib import Path
import aiofiles
from exceptions import FileStorageError
import logging

logger = logging.getLogger(__name__)

class FileStorageRepository:
    """
    Handles file storage operations such as creating, writing, and deleting files.
    """

    @staticmethod
    async def create_and_write_file_async(content: str, filename: str, directory: str='data'):
        """
        Creates and writes a file asynchronously.

        Args:
            content (str): The content to write to the file.
            filename (str): The name of the file.
            directory (str): The directory where the file will be stored. Defaults to 'data'.

        Returns:
            tuple: A tuple containing the generated file name and its path.

        Raises:
            FileStorageError: If the file creation or writing fails.
        """
        logger.debug(f"Creating and writing file asynchronously: filename={filename}, directory={directory}")
        try:
            if not os.path.exists(directory):
                logger.info(f"Directory {directory} does not exist. Creating it.")
                os.makedirs(directory)
            
            safe_filename = Path(filename).name
            file_name = str(int(time.time())) + '-' + str(random.randint(0, int(1e9))) + '-' + safe_filename
            file_path = os.path.join(directory, file_name)

            logger.info(f"Generated file path: {file_path}")

            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(content)     # assuming content comes from UploadFile.read()
            
            logger.info(f"File written successfully: {file_path}")
            return file_name, file_path

        except Exception as e:
            logger.error(f"Failed to create or write file: {e}", exc_info=True)
            raise FileStorageError('Failed to create or write PDF file: ' + str(e))
        
    @staticmethod
    def delete_file(file_path: str):
        """
        Deletes a file from the file system.

        Args:
            file_path (str): The path of the file to delete.

        Raises:
            FileStorageError: If the file deletion fails.
        """
        logger.debug(f"Deleting file: {file_path}")
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"File deleted successfully: {file_path}")
            else:
                logger.warning(f"File does not exist: {file_path}")
        except Exception as e:
            logger.error(f"Failed to delete file: {e}", exc_info=True)
            raise FileStorageError(f'Failed to delete file: {e}')