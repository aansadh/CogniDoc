import os, time, random
from pathlib import Path
import aiofiles
from exceptions import FileStorageError

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
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)
            
            safe_filename = Path(filename).name
            file_name = str(int(time.time())) + '-' + str(random.randint(0, int(1e9))) + '-' + safe_filename
            file_path = os.path.join(directory, file_name)

            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(content)     # assuming content comes from UploadFile.read()
            
            return file_name, file_path

        except Exception as e:
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
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            raise FileStorageError(f'Failed to delete file: {e}')