from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import logging

from ..models.prompt import PromptRequest, PromptResponse
from ..services.prompt_processor import PromptProcessor
from ..services.singleton import file_system_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/prompt", tags=["prompt"])

def get_prompt_processor():
    return PromptProcessor()

@router.post("/process", response_model=PromptResponse)
async def process_prompt(
    request: PromptRequest,
    prompt_processor: PromptProcessor = Depends(get_prompt_processor)
):
    """
    Process a natural language prompt and execute file operations using LLM
    """
    try:
        logger.info(f"Processing prompt: {request.prompt} for workspace: {request.workspace_id}")
        
        workspace_info = file_system_service.get_workspace_info(request.workspace_id)
        if not workspace_info:
            raise HTTPException(status_code=404, detail="Workspace not found")
        
        workspace_path = file_system_service.get_workspace_path(request.workspace_id)
        logger.info(f"Workspace path: {workspace_path}")
        
        result = await prompt_processor.process_prompt(request.prompt, workspace_path)
        logger.info(f"LLM result: {result}")
        
        if result.get("method") == "none" or result.get("error"):
            raise HTTPException(
                status_code=503, 
                detail=f"LLM service unavailable: {result.get('error', 'Unknown error')}"
            )
        
        executed_operations = []
        errors = []
        created_files = []
        
        for operation in result.get("operations", []):
            try:
                op_type = operation.get("type")
                target = operation.get("target")
                logger.info(f"Processing operation: {op_type} -> {target}")
                
                if op_type == "create":
                    content = operation.get("content", "")
                    op_result = await file_system_service.create_file(request.workspace_id, target, content)
                    if op_result["success"]:
                        executed_operations.append(f"Created file: {target}")
                        # Get the full path of the created file
                        full_path = file_system_service.get_workspace_path(request.workspace_id) / target
                        created_files.append(str(full_path.absolute()))
                    else:
                        errors.append(f"Failed to create file: {target}")
                
                elif op_type == "edit":
                    content = operation.get("content", "")
                    op_result = await file_system_service.edit_file(request.workspace_id, target, content)
                    if op_result["success"]:
                        executed_operations.append(f"Edited file: {target}")
                        # Get the full path of the edited file
                        full_path = file_system_service.get_workspace_path(request.workspace_id) / target
                        created_files.append(str(full_path.absolute()))
                    else:
                        errors.append(f"Failed to edit file: {target}")
                
                elif op_type == "delete":
                    op_result = await file_system_service.delete_file(request.workspace_id, target)
                    if op_result["success"]:
                        executed_operations.append(f"Deleted file: {target}")
                    else:
                        errors.append(f"Failed to delete file: {target}")
                
                elif op_type == "rename":
                    new_name = operation.get("new_name")
                    if new_name:
                        op_result = await file_system_service.rename_file(request.workspace_id, target, new_name)
                        if op_result["success"]:
                            executed_operations.append(f"Renamed {target} to {new_name}")
                            # Get the full path of the renamed file
                            full_path = file_system_service.get_workspace_path(request.workspace_id) / new_name
                            created_files.append(str(full_path.absolute()))
                        else:
                            errors.append(f"Failed to rename {target} to {new_name}")
                    else:
                        errors.append(f"Missing new name for rename operation: {target}")
                
                elif op_type == "list":
                    files_result = await file_system_service.list_files(request.workspace_id)
                    if files_result["success"]:
                        executed_operations.append(f"Listed {len(files_result['files'])} files in workspace")
                    else:
                        errors.append(f"Failed to list files: {files_result['message']}")
                        
            except Exception as e:
                logger.error(f"Error executing operation {operation}: {str(e)}")
                errors.append(f"Error executing operation {operation}: {str(e)}")
        
        # Create success message and file path
        file_path = created_files[0] if created_files else ""
        success_message = ""
        
        if len(errors) == 0 and created_files:
            if len(created_files) == 1:
                success_message = f"✅ Successfully created file: {created_files[0]}"
            else:
                success_message = f"✅ Successfully created {len(created_files)} files"
        elif len(errors) == 0:
            success_message = "✅ Operation completed successfully"
        else:
            success_message = f"⚠️ Operation completed with {len(errors)} errors"
        
        response_data = {
            "success": len(errors) == 0,
            "operations": executed_operations,
            "errors": errors,
            "confidence": result.get("confidence", 0.0),
            "reasoning": result.get("reasoning", ""),
            "method": result.get("method", "unknown"),
            "file_path": file_path,
            "success_message": success_message
        }
        
        logger.info(f"Response data: {response_data}")
        
        return PromptResponse(**response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing prompt: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing prompt: {str(e)}")

@router.get("/health")
async def prompt_health(
    prompt_processor: PromptProcessor = Depends(get_prompt_processor)
):
    """
    Check if the LLM service is healthy
    """
    try:
        llm_available = await prompt_processor.is_llm_available()
        return {
            "status": "healthy" if llm_available else "unhealthy",
            "llm_available": llm_available,
            "method": "llm_only"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "llm_available": False,
            "method": "llm_only"
        }