"""
Development server runner for Sentopic API

Run this script to start the API server in development mode.
Supports dynamic port assignment via PORT environment variable.
"""

import uvicorn
import signal
import sys
import os

def signal_handler(sig, frame):
    print("\n🛑 Graceful shutdown initiated...")
    print("⏳ Waiting for background tasks to complete...")
    sys.exit(0)

if __name__ == "__main__":
    # Detect if running in PyInstaller bundle
    is_bundled = getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')
    
    # Get port from environment variable or default to 8000
    port = int(os.environ.get('PORT', 8000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    if is_bundled:
        print("🚀 Starting Sentopic API Production Server...")
        print("📦 Running in PyInstaller bundle mode")
    else:
        print("🚀 Starting Sentopic API Development Server...")
        print("🔄 Auto-reload enabled - server will restart when code changes")
    
    print(f"🌐 Host: {host}")
    print(f"🔌 Port: {port}")
    print(f"📚 API Documentation: http://localhost:{port}/docs")
    print(f"🏥 Health Check: http://localhost:{port}/health")
    print("⏹️  Press Ctrl+C to stop the server")
    
    # Show environment info for debugging
    if 'PORT' in os.environ:
        print(f"✅ Using PORT from environment: {port}")
    else:
        print(f"⚠️  No PORT environment variable set, using default: {port}")
    
    print("-" * 60)

    # Handle graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        if is_bundled:
            # In PyInstaller bundle, import the app directly
            from api import app
            uvicorn.run(
                app,  # Pass app object directly
                host=host,
                port=port,
                reload=False,
                log_level="info"
            )
        else:
            # In development, use string import for auto-reload
            uvicorn.run(
                "api:app",  # String import works in development
                host=host,
                port=port,
                reload=True,
                log_level="info"
            )
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ ERROR: Port {port} is already in use!")
            print(f"💡 Try a different port by setting PORT environment variable:")
            print(f"   PORT=8001 python run_api.py")
            sys.exit(1)
        else:
            print(f"❌ ERROR starting server: {e}")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)