from pydantic import BaseModel, Field
from typing import List
from .file_operations import FileOperation


class PromptRequest(BaseModel):
    """Request to process a natural language prompt"""
    workspace_id: str
    prompt: str = Field(..., min_length=1, max_length=10000)


class PromptResponse(BaseModel):
    """Response from prompt processing"""
    success: bool
    operations: List[str]  
    errors: List[str]
    confidence: float
    reasoning: str  # AI reasoning about the prompt
    method: str  
    file_path: str = ""  
    success_message: str = ""  # Human-readable success message 