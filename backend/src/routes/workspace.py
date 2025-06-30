from fastapi import APIRouter, HTTPException, UploadFile, File, Form
import shutil
from typing import List
from pydantic import BaseModel

from ..models import WorkspaceUploadResponse, WorkspaceInfo
from ..services.singleton import file_system_service

router = APIRouter(prefix="/workspace", tags=["Workspace"])

class CreateWorkspaceRequest(BaseModel):
    name: str

@router.post("/create", response_model=dict)
async def create_workspace(request: CreateWorkspaceRequest):
    """Create a new empty workspace"""
    try:
        workspace_info = file_system_service.create_workspace(request.name)
        return {
            "workspace_id": workspace_info.workspace_id,
            "message": f"Workspace '{request.name}' created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create workspace: {str(e)}")

@router.post("/upload", response_model=WorkspaceUploadResponse)
async def upload_workspace(
    files: List[UploadFile] = File(...),
    workspace_name: str = Form(...)
):
    """Upload a folder to create a new workspace"""
    try:
        workspace_info = file_system_service.create_workspace(workspace_name)
        workspace_path = file_system_service.get_workspace_path(workspace_info.workspace_id)
        file_count = 0
        for uploaded_file in files:
            if uploaded_file.filename:
                file_path = workspace_path / uploaded_file.filename
                file_path.parent.mkdir(parents=True, exist_ok=True)
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(uploaded_file.file, buffer)
                file_count += 1
        workspace_info.file_count = file_count
        file_system_service.workspaces[workspace_info.workspace_id] = workspace_info
        return WorkspaceUploadResponse(
            workspace_id=workspace_info.workspace_id,
            message=f"Workspace '{workspace_name}' created with {file_count} files",
            file_count=file_count,
            workspace_path=str(workspace_path)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload workspace: {str(e)}")

@router.get("/{workspace_id}", response_model=WorkspaceInfo)
def get_workspace_info(workspace_id: str):
    """Get information about a workspace"""
    workspace_info = file_system_service.get_workspace_info(workspace_id)
    if not workspace_info:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return workspace_info

@router.get("/{workspace_id}/files")
async def list_workspace_files(workspace_id: str, path: str = ""):
    """List files in a workspace directory"""
    try:
        result = await file_system_service.list_files(workspace_id, path)
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list files: {str(e)}")

@router.delete("/{workspace_id}")
def delete_workspace(workspace_id: str):
    """Delete a workspace and all its files"""
    try:
        workspace_info = file_system_service.get_workspace_info(workspace_id)
        if not workspace_info:
            raise HTTPException(status_code=404, detail="Workspace not found")
        workspace_path = file_system_service.get_workspace_path(workspace_id)
        if workspace_path.exists():
            shutil.rmtree(workspace_path)
        del file_system_service.workspaces[workspace_id]
        return {"message": f"Workspace {workspace_id} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete workspace: {str(e)}")

@router.get("/", response_model=List[WorkspaceInfo])
def list_workspaces():
    """List all workspaces"""
    return list(file_system_service.workspaces.values()) 