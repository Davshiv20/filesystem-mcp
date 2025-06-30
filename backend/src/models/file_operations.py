from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Literal
from enum import Enum


class FileOperationType(str, Enum):
    """Supported file operation types"""
    CREATE = "create"
    EDIT = "edit"
    DELETE = "delete" 
    APPEND = "append"
    RENAME = "rename"
    LIST = "list"


class FileOperation(BaseModel):
    """Represents a file operation command"""
    operation: FileOperationType
    path: str = Field(..., description="File path relative to workspace")
    content: Optional[str] = Field(None, description="File content for create/edit/append operations")
    new_path: Optional[str] = Field(None, description="New path for rename operations")
    
    @validator('path')
    def validate_path(cls, v):
        """Validate path to prevent path traversal attacks"""
        if not v or v.startswith('/') or '..' in v or v.startswith('~'):
            raise ValueError("Invalid path: cannot use absolute paths, parent directory references, or home directory")
        return v.strip('/')
    
    @validator('new_path')
    def validate_new_path(cls, v):
        """Validate new path for rename operations"""
        if v is not None:
            if v.startswith('/') or '..' in v or v.startswith('~'):
                raise ValueError("Invalid new path: cannot use absolute paths, parent directory references, or home directory")
            return v.strip('/')
        return v


class FileOperationRequest(BaseModel):
    """Request for file operations"""
    workspace_id: str
    operations: List[FileOperation]


class FileOperationResponse(BaseModel):
    """Response from file operations"""
    success: bool
    message: str
    results: List[Dict[str, Any]]
    errors: List[str] = [] 