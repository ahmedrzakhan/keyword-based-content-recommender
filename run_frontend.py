#!/usr/bin/env python3
"""
Content Recommender Frontend Startup Script
Run this script to start the Streamlit frontend application.
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Start the Streamlit frontend application."""
    print("🎨 Starting Content Recommender Frontend...")
    print("   URL: http://localhost:8501")
    print("   Press Ctrl+C to stop")
    print("-" * 50)
    
    # Get project root
    project_root = Path(__file__).parent
    frontend_app = project_root / "frontend" / "app.py"
    
    if not frontend_app.exists():
        print("❌ Frontend app not found!")
        sys.exit(1)
    
    # Check if backend is running
    print("💡 Make sure the backend is running on http://localhost:8000")
    print("   Run 'python run_backend.py' in another terminal if needed")
    print("-" * 50)
    
    try:
        # Run streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            str(frontend_app),
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Frontend application stopped")
    except Exception as e:
        print(f"❌ Failed to start frontend: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()