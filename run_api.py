"""
Development server runner for Sentopic API

Run this script to start the API server in development mode.
Supports dynamic port assignment via PORT environment variable.
"""

import uvicorn
import signal
import sys
import os
import shutil
from pathlib import Path

def get_user_data_dir():
    """
    Get the appropriate user data directory based on the operating system.
    
    Returns:
        Path object pointing to the user data directory
    """
    app_name = "Sentopic"
    
    if sys.platform == "darwin":  # macOS
        base_dir = Path.home() / "Library" / "Application Support"
    elif sys.platform == "win32":  # Windows
        base_dir = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    else:  # Linux and other Unix-like systems
        base_dir = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    
    return base_dir / app_name


def setup_user_data_directory(user_data_dir):
    """
    Set up the user data directory with necessary files.
    
    Args:
        user_data_dir: Path to the user data directory
        
    Returns:
        Tuple of (success: bool, error_message: str)
    """
    try:
        # Create directory if it doesn't exist
        user_data_dir.mkdir(parents=True, exist_ok=True)
        print(f"📁 User data directory: {user_data_dir}")
        
        # Check if config.json exists
        config_path = user_data_dir / "config.json"
        config_example_path = user_data_dir / "config.example.json"
        
        # In bundled mode, config.example.json should be in the bundle
        # Get the bundle directory (where the executable is)
        if getattr(sys, 'frozen', False):
            # Running in PyInstaller bundle
            bundle_dir = Path(sys._MEIPASS)
            bundled_example = bundle_dir / "config.example.json"
            
            # Copy config.example.json to user data directory if not already there
            if bundled_example.exists() and not config_example_path.exists():
                shutil.copy2(bundled_example, config_example_path)
                print(f"📋 Copied config.example.json to user data directory")
        
        # Check if config.json needs to be created
        if not config_path.exists():
            if config_example_path.exists():
                # Copy example to create config
                shutil.copy2(config_example_path, config_path)
                print(f"✅ Created config.json from example")
                print(f"⚠️  Please configure your API keys in: {config_path}")
            else:
                # This shouldn't happen, but handle it gracefully
                print(f"⚠️  Warning: config.example.json not found")
                return False, "config.example.json not found in bundle or user data directory"
        else:
            print(f"✅ Using existing config.json")
        
        return True, ""
        
    except Exception as e:
        return False, f"Failed to setup user data directory: {str(e)}"

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
    
    # Set up data directory based on mode
    if is_bundled:
        # Production mode - use user data directory
        user_data_dir = get_user_data_dir()
        
        print("-" * 60)
        print("DEBUG: User data directory setup")
        print(f"  User data dir: {user_data_dir}")
        print("-" * 60)
        
        success, error = setup_user_data_directory(user_data_dir)
        
        if not success:
            print(f"❌ Failed to setup user data directory: {error}")
            sys.exit(1)
        
        # Set environment variable so other modules can find it
        os.environ['SENTOPIC_DATA_DIR'] = str(user_data_dir)
        print(f"📂 Data directory: {user_data_dir}")
        
        # DEBUG: Verify config file exists and is readable
        config_file = user_data_dir / "config.json"
        print("-" * 60)
        print("DEBUG: Verifying config file")
        print(f"  Config path: {config_file}")
        print(f"  Exists: {config_file.exists()}")
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    import json
                    config_content = json.load(f)
                    print(f"  Reddit config present: {'reddit' in config_content}")
                    if 'reddit' in config_content:
                        reddit_cfg = config_content['reddit']
                        print(f"    client_id present: {bool(reddit_cfg.get('client_id'))}")
                        print(f"    client_id length: {len(reddit_cfg.get('client_id', ''))}")
                        print(f"    client_secret present: {bool(reddit_cfg.get('client_secret'))}")
                        print(f"    client_secret length: {len(reddit_cfg.get('client_secret', ''))}")
                        print(f"    user_agent present: {bool(reddit_cfg.get('user_agent'))}")
                        print(f"    user_agent length: {len(reddit_cfg.get('user_agent', ''))}")
            except Exception as e:
                print(f"  ERROR reading config: {e}")
        print("-" * 60)
    else:
        # Development mode - use current directory (backward compatible)
        print(f"📂 Data directory: {os.getcwd()} (development mode)")
    
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