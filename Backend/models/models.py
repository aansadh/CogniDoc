from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Optional
from bson.objectid import ObjectId

def validate_not_empty(value: str, field_name: str = "Field") -> str:
    if not value.strip():
        raise ValueError(f"{field_name} cannot be empty.")
    return value

class QueryModel(BaseModel):
    query: str = Field(..., min_length=2)

class TextModel(BaseModel):
    text: str
    created_at: datetime = Field(default_factory=datetime.now(timezone.utc))
    file_name: str = Field(..., min_length=1, description="Title of the text content")

class ScrapeUrlModel(BaseModel):
    url: str = Field(..., min_length=1)

class SessionModel(BaseModel):
    session_id: Optional[str] = Field(None, description="Unique session identifier", alias="_id")
    user_id: str = Field(..., description="ID of the user associated with the session")
    created_at: datetime = Field(default_factory=datetime.now(timezone.utc))

    class Config:
        allow_population_by_field_name = True
        json_encoders = { ObjectId: str }
        

class FileModel(BaseModel):
    # _id: str = Field(..., description="Unique file identifier")
    file_name: str = Field(..., description="Name of the uploaded file")
    session_id: str = Field(..., description="ID of the session that uploaded the file")
    created_at: datetime = Field(default_factory=datetime.now(timezone.utc), description="Timestamp of file upload")