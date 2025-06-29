"""
Data models for the Smart PDF QA API application.
"""

from pydantic import BaseModel, Field
from datetime import datetime, timezone

def validate_not_empty(value: str, field_name: str = "Field") -> str:
    """
    Validates that a string value is not empty.

    Args:
        value (str): The string value to validate.
        field_name (str): The name of the field being validated.

    Returns:
        str: The validated string value.

    Raises:
        ValueError: If the string value is empty.
    """
    if not value.strip():
        raise ValueError(f"{field_name} cannot be empty.")
    return value

class QueryModel(BaseModel):
    """
    Represents a query model for user input.

    Attributes:
        query (str): The query string provided by the user.
    """
    query: str = Field(..., min_length=2)

class TextModel(BaseModel):
    """
    Represents a text model for storing text content metadata.

    Attributes:
        text (str): The text content.
        created_at (datetime): The timestamp of text creation.
        file_name (str): The title of the text content.
    """
    text: str
    created_at: datetime = Field(default_factory=datetime.now(timezone.utc))
    file_name: str = Field(..., min_length=1, description="Title of the text content")

class ScrapeUrlModel(BaseModel):
    """
    Represents a model for storing URL metadata.

    Attributes:
        url (str): The URL to scrape.
    """
    url: str = Field(..., min_length=1)

class FileModel(BaseModel):
    """
    Represents a file model for storing file metadata.

    Attributes:
        file_name (str): The name of the uploaded file.
        session_id (str): The ID of the session that uploaded the file.
        created_at (datetime): The timestamp of file upload.
    """
    # _id: str = Field(..., description="Unique file identifier")
    file_name: str = Field(..., description="Name of the uploaded file")
    session_id: str = Field(..., description="ID of the session that uploaded the file")
    created_at: datetime = Field(default_factory=datetime.now(timezone.utc), description="Timestamp of file upload")