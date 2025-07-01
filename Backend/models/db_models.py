from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Optional, ClassVar

class FileModel(BaseModel):
    """
    Represents the metadata of a file stored in the database.

    Attributes:
        file_id (Optional[str]): Unique identifier for the file, used as the primary key.
        file_name (str): Name of the uploaded file.
        session_id (str): Identifier for the session that uploaded the file.
        created_at (datetime): Timestamp indicating when the file was uploaded.
    """
    file_id: Optional[str] = Field(default=None, description="Unique file identifier", alias="_id")
    file_name: str = Field(..., description="Name of the uploaded file")
    session_id: str = Field(..., description="ID of the session that uploaded the file")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Timestamp of file upload")

    modelConfig: ClassVar[dict] = {"validate_by_name": True}

class VectorstoreModel(BaseModel):
    """
    Represents the metadata schema for vectorstore entries in the database.

    Attributes:
        file_id (str): Identifier for the file associated with the vectorstore.
        file_name (str): Name of the file associated with the vectorstore.
        session_id (str): Identifier for the session that owns the vectorstore.
        created_at (datetime): Timestamp indicating when the vectorstore entry was created.

    Note:
        This model is associated with Chroma vectorstore and is used solely for metadata storage.
    """
    file_id: str = Field(..., description="ID of the file associated with the vectorstore")
    file_name: str = Field(..., description="Name of the file associated with the vectorstore")
    session_id: str = Field(..., description="ID of the session that owns the vectorstore")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Timestamp of vectorstore creation")

class SessionModel(BaseModel):
    """
    Represents a user session stored in the database.

    Attributes:
        session_id (Optional[str]): Unique identifier for the session, used as the primary key.
        session_name (Optional[str]): Name of the session, can be used for identification.
        user_id (str): Identifier for the user associated with the session.
        created_at (datetime): Timestamp indicating when the session was created.

    Config:
        - Allows population of fields by their names.
        - Encodes ObjectId fields as strings for JSON serialization.
    """
    session_id: Optional[str] = Field(default=None, description="Unique session identifier", alias="_id")
    session_name: Optional[str] = Field(default=None, description="Name of the session")
    user_id: str = Field(..., description="ID of the user associated with the session")
    created_at: datetime = Field(default_factory= lambda: datetime.now(timezone.utc), description="Timestamp of session creation")

    modelConfig: ClassVar[dict] = {"validate_by_name": True}
    