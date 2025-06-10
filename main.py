#!/usr/bin/env python3

import sys
from src.collector import collector, CollectionParameters
from src.database import db


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
    print(f"{'ID':<36} {'Subreddit':<15} {'Sort':<12} {'Posts':<6} {'Status':<10}")
    print("-" * 85)
    
    for collection in collections:
        print(f"{collection.id:<36} "
              f"r/{collection.subreddit:<14} "
              f"{collection.sort_method:<12} "
              f"{collection.posts_requested:<6} "
              f"{collection.status:<10}")


def main():
    """Main CLI interface."""
    if len(sys.argv) > 1:
        if sys.argv[1] == "--list":
            show_collections()
            return
        elif sys.argv[1] == "--help":
            print("Usage:")
            print("  python main.py          - Start interactive collection")
            print("  python main.py --list   - Show collection history")
            print("  python main.py --help   - Show this help")
            return
    
    try:
        # Get collection parameters from user
        params = get_user_input()
        if params is None:
            return
        
        print("\n" + "="*50)
        
        # Start collection
        collection_id = collector.collect_data(params)
        
        print(f"\nCollection saved with ID: {collection_id}")
        print("Use 'python main.py --list' to see all collections")
        
    except KeyboardInterrupt:
        print("\n\nCollection interrupted by user")
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
    except Exception as e:
        print(f"\nError: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())