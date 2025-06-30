import os
import re
import logging
from typing import Optional, Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential
from together import Together
from dotenv import load_dotenv

from ..config import Settings

load_dotenv()

logger = logging.getLogger(__name__)

class LLMService:
    """Service for LLM operations using Together AI"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = None
        self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize the LLM with Together AI"""
        try:
            api_key = os.getenv("TOGETHER_API_KEY")
            if not api_key:
                logger.warning("TOGETHER_API_KEY not found. LLM features will be disabled.")
                return
            
            self.client = Together(api_key=api_key)
            logger.info(f"LLM service initialized with Together AI using model: {self.settings.llm_model}")
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            self.client = None
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def process_prompt(self, prompt: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process a natural language prompt and return structured operations
        
        Args:
            prompt: Natural language prompt describing file operations
            context: Additional context (workspace path, etc.)
            
        Returns:
            Dictionary with parsed operations and confidence
        """
        if not self.client:
            return self._fallback_processing(prompt, context)
        
        try:
            # Create a structured prompt for the LLM
            structured_prompt = f"""
            You are a file system assistant. Parse this user request and extract file operations:
            
            User Request: "{prompt}"
            Workspace Path: {context.get('workspace_path', 'unknown')}
            
            Respond in this exact JSON format:
            {{
                "operations": [
                    {{
                        "type": "create|edit|delete|rename|list",
                        "target": "filename or pattern",
                        "content": "file content (for create/edit)",
                        "new_name": "new filename (for rename)",
                        "description": "what this operation does"
                    }}
                ],
                "confidence": 0.0-1.0,
                "reasoning": "why these operations were chosen"
            }}
            
            Only include operations that are clearly requested. Be conservative.
            """
            
            response = self.client.chat.completions.create(
                model=self.settings.llm_model,
                messages=[
                    {
                        "role": "user",
                        "content": structured_prompt
                    }
                ],
                temperature=self.settings.llm_temperature,
                max_tokens=self.settings.llm_max_tokens
            )
            
            result_content = response.choices[0].message.content
            
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', result_content, re.DOTALL)
            if json_match:
                import json
                try:
                    result = json.loads(json_match.group())
                    result["method"] = "llm"
                    return result
                except json.JSONDecodeError:
                    pass
            
            # If JSON parsing fails, return error
            return {
                "operations": [],
                "confidence": 0.0,
                "reasoning": "Failed to parse LLM response as JSON",
                "method": "llm",
                "error": "Invalid JSON response from LLM"
            }
            
        except Exception as e:
            logger.error(f"LLM processing failed: {e}")
            return self._fallback_processing(prompt, context)
    
    def _fallback_processing(self, prompt: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Fallback when LLM is not available"""
        return {
            "operations": [],
            "confidence": 0.0,
            "reasoning": "LLM service not available",
            "method": "none",
            "error": "LLM service unavailable"
        }
    
    async def is_available(self) -> bool:
        """Check if LLM service is available"""
        if not self.client:
            return False
        
        try:
            # Simple health check
            response = self.client.chat.completions.create(
                model=self.settings.llm_model,
                messages=[
                    {
                        "role": "user",
                        "content": "Hello"
                    }
                ],
                max_tokens=10
            )
            return bool(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"LLM health check failed: {e}")
            return False 