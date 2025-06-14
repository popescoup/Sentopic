#!/usr/bin/env python3

import sys
from src.cli.collection import handle_collection_commands
from src.cli.analytics import handle_analytics_commands


def show_help():
    """Display help information."""
    print("Sentopic - Reddit Analytics Tool")
    print()
    print("Collection Commands:")
    print("  python main.py                    - Start interactive data collection")
    print("  python main.py --list             - Show collection history")
    print()
    print("Analytics Commands:")
    print("  python main.py --analyze          - Start new analysis (interactive)")
    print("  python main.py --sessions         - List analysis sessions")
    print("  python main.py --results <id>     - View session results")
    print("  python main.py --trends <id>      - View trend analysis for session")
    print("  python main.py --delete-session <id> - Delete analysis session")
    print()
    print("General:")
    print("  python main.py --help             - Show this help")


def main():
    """Main CLI interface."""
    # Check for help flag anywhere in arguments (FIRST PRIORITY)
    if "--help" in sys.argv or "-h" in sys.argv:
        show_help()
        return 0
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        # Collection commands
        if command in ["--list"]:
            return handle_collection_commands(sys.argv[1:])
        
        # Analytics commands
        if command in ["--analyze", "--sessions", "--results", "--trends", "--delete-session"]:
            return handle_analytics_commands(sys.argv[1:])
        
        # Unknown command
        print(f"Unknown command: {command}")
        print("Use 'python main.py --help' for available commands")
        return 1
    
    # No arguments - default to interactive collection
    return handle_collection_commands([])


if __name__ == "__main__":
    exit(main())