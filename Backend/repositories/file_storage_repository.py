import os, time, random
from pathlib import Path
import aiofiles
from exceptions import FileOperationError

class FileStorageRepository:

    @staticmethod
    async def create_and_write_file_async(content: str, filename: str, directory: str='data'):        
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
            raise FileOperationError('Failed to create or write PDF file: ' + str(e))