from pydantic import BaseModel
from typing import Optional


class FileInfo(BaseModel):
    """Information about a file"""
    name: str
    path: str
    is_directory: bool
    size: Optional[int] = None
    modified_at: Optional[str] = None


class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str
    detail: Optional[str] = None 