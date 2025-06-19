from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Optional
from bson.objectid import ObjectId

class FileModel(BaseModel):
    """
    Represents the file model in the database.
    """
    file_id: Optional[str] = Field(None, description="Unique file identifier", alias="_id")
    file_name: str = Field(..., description="Name of the uploaded file")
    session_id: str = Field(..., description="ID of the session that uploaded the file")
    created_at: datetime = Field(datetime.now(timezone.utc), description="Timestamp of file upload")

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}


