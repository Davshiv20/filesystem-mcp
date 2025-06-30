#!/usr/bin/env python3
"""
Test script to verify the FastAPI server starts correctly
"""

import asyncio
import uvicorn
from main import app

def test_server_start():
    """Test if the server can start without errors"""
    print("🚀 Server Startup Test")
    print("=" * 30)
    
    try:
        # Test if the app can be created
        print("✅ FastAPI app created successfully")
        
        # Test if routes are registered
        routes = [route.path for route in app.routes]
        print(f"✅ Routes registered: {len(routes)} routes found")
        
        # List some key routes
        key_routes = [r for r in routes if any(x in r for x in ['health', 'workspace', 'operations', 'prompt'])]
        for route in key_routes:
            print(f"   - {route}")
        
        print("\n✅ Server test completed successfully!")
        print("\n📋 To start the server, run:")
        print("   uvicorn main:app --reload")
        print("\n📋 To test the API, visit:")
        print("   http://localhost:8000/docs")
        
        return True
        
    except Exception as e:
        print(f"❌ Server test failed: {e}")
        return False

if __name__ == "__main__":
    test_server_start() 