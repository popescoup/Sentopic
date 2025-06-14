"""
Collection CLI

Command-line interface for Reddit data collection functionality.
Refactored from the original main.py implementation.
"""

from datetime import datetime
from ..collector import collector, CollectionParameters
from ..database import db, Post


def get_user_input():
    """Get collection parameters from user input."""
    print("=== Sentopic Reddit Data Collector ===\n")
    
    # Get subreddit
    subreddit = input("Enter subreddit name (without r/): ").strip()
    if not subreddit:
        print("Error: Subreddit name is required")
        return None
    
    # Get sort method
    print("\nSort methods:")
    print("1. hot")
    print("2. new") 
    print("3. rising")
    print("4. top")
    print("5. controversial")
    
    sort_choice = input("Choose sort method (1-5): ").strip()
    sort_methods = {'1': 'hot', '2': 'new', '3': 'rising', '4': 'top', '5': 'controversial'}
    
    if sort_choice not in sort_methods:
        print("Error: Invalid sort method choice")
        return None
    
    sort_method = sort_methods[sort_choice]
    time_period = None
    
    # Get time period if needed
    if sort_method in ['top', 'controversial']:
        print("\nTime periods:")
        print("1. hour")
        print("2. day")
        print("3. week")
        print("4. month")
        print("5. year")
        print("6. all")
        
        time_choice = input("Choose time period (1-6): ").strip()
        time_periods = {'1': 'hour', '2': 'day', '3': 'week', '4': 'month', '5': 'year', '6': 'all'}
        
        if time_choice not in time_periods:
            print("Error: Invalid time period choice")
            return None
        
        time_period = time_periods[time_choice]
    
    # Get numeric parameters
    try:
        posts_count = int(input("\nNumber of posts to collect: "))
        root_comments = int(input("Max root comments per post: "))
        replies_per_root = int(input("Max replies per root comment: "))
        min_upvotes = int(input("Minimum upvotes for comments: "))
    except ValueError:
        print("Error: Please enter valid numbers")
        return None
    
    try:
        params = CollectionParameters(
            subreddit=subreddit,
            sort_method=sort_method,
            time_period=time_period,
            posts_count=posts_count,
            root_comments=root_comments,
            replies_per_root=replies_per_root,
            min_upvotes=min_upvotes
        )
        return params
    except ValueError as e:
        print(f"Error: {e}")
        return None


def show_collections():
    """Display all collections in the database."""
    collections = db.get_collections()
    
    if not collections:
        print("No collections found in database.")
        return
    
    print("\n=== Collection History ===")
    print(f"{'ID':<12} {'Subreddit':<15} {'Sort':<12} {'Posts':<8} {'Status':<12} {'Created':<20}")
    print("="*80)
    
    session = db.get_session()
    try:
        for collection in collections:
            # Count actual posts collected using new schema
            post_count = session.query(Post).filter_by(collection_id=collection.id).count()
            
            # Format creation time
            created_time = datetime.fromtimestamp(collection.created_at).strftime("%Y-%m-%d %H:%M")
            
            # Truncate long IDs for display
            display_id = collection.id[:10] + ".." if len(collection.id) > 12 else collection.id
            
            print(f"{display_id:<12} r/{collection.subreddit:<14} {collection.sort_method:<12} "
                  f"{post_count:<8} {collection.status:<12} {created_time:<20}")
    finally:
        session.close()
    
    print("="*80)


def run_interactive_collection():
    """Run interactive collection process."""
    try:
        # Get collection parameters from user
        params = get_user_input()
        if params is None:
            return 1
        
        print("\n" + "="*50)
        
        # Start collection
        collection_id = collector.collect_data(params)
        
        print(f"\nCollection saved with ID: {collection_id}")
        print("Use 'python main.py --list' to see all collections")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\nCollection interrupted by user")
        return 1
    except FileNotFoundError as e:
        print(f"\nConfiguration Error: {e}")
        print("\nPlease ensure config.json exists with your Reddit API credentials:")
        print("""
{
    "reddit": {
        "client_id": "YOUR_CLIENT_ID_HERE",
        "client_secret": "YOUR_CLIENT_SECRET_HERE", 
        "user_agent": "Sentopic:v1.0 (by u/yourusername)"
    }
}
        """)
        return 1
    except Exception as e:
        print(f"\nError: {e}")
        return 1


def handle_collection_commands(args):
    """
    Handle collection-related CLI commands.
    
    Args:
        args: List of command-line arguments (excluding the program name)
    
    Returns:
        Exit code (0 for success, 1 for error)
    """
    if not args:
        # No arguments - run interactive collection
        return run_interactive_collection()
    
    command = args[0]
    
    if command == "--list":
        show_collections()
        return 0
    
    # Unknown collection command
    print(f"Unknown collection command: {command}")
    return 1