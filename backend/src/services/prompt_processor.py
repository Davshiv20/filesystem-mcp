import logging
from typing import Dict, Any
from .llm_service import LLMService
from ..config import Settings

logger = logging.getLogger(__name__)

class PromptProcessor:
    """Process natural language prompts for file operations using LLM only"""
    
    def __init__(self):
        self.settings = Settings()
        self.llm_service = LLMService(self.settings)
    
    async def process_prompt(self, prompt: str, workspace_path: str = None) -> Dict[str, Any]:
        """
        Process a natural language prompt and return structured operations
        
        Args:
            prompt: Natural language prompt describing file operations
            workspace_path: Path to the workspace (optional)
            
        Returns:
            Dictionary with parsed operations and metadata
        """
        context = {"workspace_path": workspace_path} if workspace_path else {}
        
        try:
            # Process with LLM only
            result = await self.llm_service.process_prompt(prompt, context)
            return result
            
        except Exception as e:
            logger.error(f"Error processing prompt: {e}")
            return {
                "operations": [],
                "confidence": 0.0,
                "reasoning": f"Error processing prompt: {str(e)}",
                "method": "error"
            }
    
    async def is_llm_available(self) -> bool:
        """Check if LLM service is available"""
        return await self.llm_service.is_available() 