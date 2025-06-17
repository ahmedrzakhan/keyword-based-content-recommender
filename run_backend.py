#!/usr/bin/env python3
"""
Content Recommender Backend Startup Script
Run this script to start the FastAPI backend server.
"""

import os
import sys
import uvicorn
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import after adding to path
from config.settings import settings

def main():
    """Start the FastAPI backend server."""
    print("🚀 Starting Content Recommender Backend (Powered by Google Gemini)...")
    print(f"   Host: {settings.api_host}")
    print(f"   Port: {settings.api_port}")
    print("   Press Ctrl+C to stop")
    print("-" * 50)
    
    # Check if .env file exists
    env_file = project_root / ".env"
    if not env_file.exists():
        print("⚠️  WARNING: .env file not found!")
        print("   Copy .env.example to .env and configure your Google API key")
        print("   Get your free API key from: https://ai.google.dev/")
        print("   The system will work with limited functionality without API keys")
        print("-" * 50)
    else:
        # Check Google API key
        if settings.google_api_key:
            print("✅ Google API key configured")
        else:
            print("⚠️  Google API key not configured - limited functionality")
        print("-" * 50)
    
    try:
        uvicorn.run(
            "backend.main:app",
            host=settings.api_host,
            port=settings.api_port,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 Backend server stopped")
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()