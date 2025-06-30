from pydantic import BaseModel


class WorkspaceInfo(BaseModel):
    """Information about a workspace"""
    workspace_id: str
    name: str
    path: str
    file_count: int
    created_at: str


class WorkspaceUploadResponse(BaseModel):
    """Response for workspace upload"""
    workspace_id: str
    message: str
    file_count: int
    workspace_path: str 