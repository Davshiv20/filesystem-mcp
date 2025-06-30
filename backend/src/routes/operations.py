from fastapi import APIRouter, HTTPException

from ..models import FileOperationRequest, FileOperationResponse
from ..services import FileSystemService

router = APIRouter(prefix="/operations", tags=["Operations"])

# Initialize service
file_system_service = FileSystemService()


@router.post("/", response_model=FileOperationResponse)
async def execute_file_operations(request: FileOperationRequest):
    """Execute file operations"""
    try:
        # Validate workspace exists
        workspace_info = file_system_service.get_workspace_info(request.workspace_id)
        if not workspace_info:
            raise HTTPException(status_code=404, detail="Workspace not found")
        
        # Execute operations
        results = await file_system_service.execute_operations(
            request.workspace_id, 
            request.operations
        )
        
        # Check for errors
        errors = [r["message"] for r in results if not r["success"]]
        success = len(errors) == 0
        
        return FileOperationResponse(
            success=success,
            message=f"Executed {len(request.operations)} operations",
            results=results,
            errors=errors
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to execute operations: {str(e)}") 