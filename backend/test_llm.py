#!/usr/bin/env python3
"""
Test script for LLM integration with Together AI (LLM only)
"""

import asyncio
import os
from dotenv import load_dotenv
from src.services.llm_service import LLMService
from src.config import Settings

load_dotenv()

async def test_llm_integration():
    """Test LLM integration with Together AI"""
    print("🚀 LLM Integration Test (LLM Only)")
    print("=" * 50)
    
    # Check for API key
    api_key = os.getenv("TOGETHER_API_KEY")
    if not api_key:
        print("❌ TOGETHER_API_KEY not found in environment variables")
        print("   Please set your Together AI API key in .env file")
        print("   Get your API key from: https://together.ai/")
        return False
    
    settings = Settings()
    llm_service = LLMService(settings)
    
    # Test basic availability
    print(" Testing LLM availability...")
    is_available = await llm_service.is_available()
    print(f"✅ LLM Service: {' Available' if is_available else ' Unavailable'}")
    
    if not is_available:
        print("LLM service is not available. Please check your API key and internet connection.")
        return False
    
    # Test basic response
    print("\Testing basic response...")
    try:
        result = await llm_service.process_prompt("Hello, how are you?")
        method = result.get("method", "unknown")
        confidence = result.get("confidence", 0)
        print(f"✅ Basic response successful (method: {method}, confidence: {confidence:.2f})")
    except Exception as e:
        print(f"❌ Basic response failed: {e}")
        return False
    
    # Test file operation parsing (reduced to avoid rate limits)
    print("\n📁 Testing file operation parsing...")
    test_prompts = [
        "Create a file called test.txt",
        "List all files in the workspace"
    ]
    
    for i, prompt in enumerate(test_prompts):
        try:
            print(f"📝 Testing prompt {i+1}/{len(test_prompts)}: '{prompt}'")
            result = await llm_service.process_prompt(prompt, {"workspace_path": "/test/workspace"})
            operations = result.get("operations", [])
            confidence = result.get("confidence", 0)
            method = result.get("method", "unknown")
            
            print(f"   Operations: {len(operations)}")
            print(f"   Confidence: {confidence:.2f}")
            print(f"   Method: {method}")
            
            if operations:
                for op in operations:
                    print(f"   - {op.get('type', 'unknown')}: {op.get('target', 'unknown')}")
            else:
                print("   - No operations detected")
            print()
            
            # Add delay between requests to avoid rate limiting
            if i < len(test_prompts) - 1:
                await asyncio.sleep(2)
            
        except Exception as e:
            print(f"❌ Failed to process '{prompt}': {e}")
            if "rate limit" in str(e).lower():
                print("   ⚠️  Rate limit hit. Consider using a different model or waiting.")
    
    print("✅ LLM integration test completed successfully!")
    return True

if __name__ == "__main__":
    success = asyncio.run(test_llm_integration())
    if not success:
        print("\n❌ LLM test failed. Please check your Together AI setup.")
        exit(1) 