#!/usr/bin/env python3
"""
Content Recommender Demo Startup Script
This script starts both backend and frontend for a complete demo.
"""

import os
import sys
import time
import subprocess
import threading
from pathlib import Path

project_root = Path(__file__).parent

def validate_google_api_key():
    """Validate Google API key before starting demo."""
    try:
        import google.generativeai as genai
        from dotenv import load_dotenv
        
        # Load environment variables
        load_dotenv()
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            return False, "Google API key not found in environment"
        
        # Configure and test the API
        genai.configure(api_key=api_key)
        
        # Test with a simple embedding call
        response = genai.embed_content(
            model="models/text-embedding-004",
            content="test"
        )
        
        if response and 'embedding' in response:
            return True, "Google API key validated successfully"
        else:
            return False, "Invalid response from Google API"
            
    except ImportError:
        return False, "google-generativeai package not installed"
    except Exception as e:
        return False, f"Google API validation failed: {e}"

def run_backend():
    """Run the backend server."""
    print("🚀 Starting backend server...")
    subprocess.run([sys.executable, str(project_root / "run_backend.py")])

def run_frontend():
    """Run the frontend application."""
    print("🎨 Starting frontend application...")
    time.sleep(3)  # Wait for backend to start
    subprocess.run([sys.executable, str(project_root / "run_frontend.py")])

def main():
    """Start both backend and frontend."""
    print("🌟 Content Recommender Demo (Powered by Google Gemini)")
    print("=" * 60)
    print("This will start both the backend API and frontend interface")
    print("Backend: http://localhost:8000")
    print("Frontend: http://localhost:8501")
    print("Press Ctrl+C to stop both services")
    print("=" * 60)
    
    # Check environment
    env_file = project_root / ".env"
    if not env_file.exists():
        print("⚠️  Setup Required:")
        print("   1. Copy .env.example to .env")
        print("   2. Add your Google API key for full functionality")
        print("   3. Get your free API key from: https://ai.google.dev/")
        print("   4. The demo will work with limited features without API keys")
        input("   Press Enter to continue...")
    else:
        # Validate Google API key if .env exists
        print("🔑 Validating Google API key...")
        is_valid, message = validate_google_api_key()
        if is_valid:
            print(f"✅ {message}")
        else:
            print(f"⚠️  {message}")
            print("   The demo will work with limited functionality")
            print("   Get your free API key from: https://ai.google.dev/")
            input("   Press Enter to continue...")
    
    try:
        # Start backend in a thread
        backend_thread = threading.Thread(target=run_backend, daemon=True)
        backend_thread.start()
        
        # Give backend time to start
        print("⏳ Waiting for backend to initialize...")
        time.sleep(5)
        
        # Start frontend
        run_frontend()
        
    except KeyboardInterrupt:
        print("\n🛑 Demo stopped")
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()