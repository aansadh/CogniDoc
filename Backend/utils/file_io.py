import os, time, random
from fastapi import HTTPException
from pathlib import Path
import aiofiles

async def create_and_write_file_async(content: str, filename: str, directory: str='data'):
    if not content or not filename:
        raise HTTPException(status_code=400, detail="Content and filename cannot be empty.")
    
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
        raise HTTPException(status_code=500, detail='Failed to create or write PDF file: ' + str(e))
