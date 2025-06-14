"""
Analytics CLI

Command-line interface for Phase 2 analytics functionality.
"""

import json
from datetime import datetime
from typing import List
from ..analytics import analytics_engine
from ..database import db


def get_analysis_input():
    """Get analysis parameters from user input."""
    print("=== Sentopic Analytics Engine ===\n")
    
    # STEP 1: Show available collections FIRST
    collections = db.get_collections()
    if not collections:
        print("Error: No collections found. Please collect some data first.")
        return None
    
    print("Available collections:")
    for i, collection in enumerate(collections, 1):
        created_time = datetime.fromtimestamp(collection.created_at).strftime("%Y-%m-%d %H:%M")
        print(f"{i}. r/{collection.subreddit} ({collection.sort_method}) - {created_time}")
    
    # STEP 2: Get collection selection
    selection_input = input(f"\nSelect collections (comma-separated numbers, 1-{len(collections)}): ").strip()
    if not selection_input:
        print("Error: At least one collection must be selected")
        return None
    
    try:
        selected_indices = [int(i.strip()) for i in selection_input.split(',') if i.strip()]
        selected_collections = []
        
        for idx in selected_indices:
            if 1 <= idx <= len(collections):
                selected_collections.append(collections[idx - 1].id)
            else:
                print(f"Error: Invalid collection number: {idx}")
                return None
        
        if not selected_collections:
            print("Error: No valid collections selected")
            return None
        
    except ValueError:
        print("Error: Please enter valid collection numbers")
        return None
    
    # STEP 3: Get keywords
    keywords_input = input("\nEnter keywords (comma-separated): ").strip()
    if not keywords_input:
        print("Error: At least one keyword is required")
        return None
    
    keywords = [k.strip() for k in keywords_input.split(',') if k.strip()]
    if not keywords:
        print("Error: No valid keywords provided")
        return None
    
    # STEP 4: Get analysis name
    name = input("\nEnter analysis name: ").strip()
    if not name:
        print("Error: Analysis name is required")
        return None
    
    # STEP 5: Get matching type
    print("\nMatching type:")
    print("1. Exact matching (keyword must be a complete word)")
    print("2. Partial matching (keyword can be part of a larger word)")
    
    matching_choice = input("Choose matching type (1-2): ").strip()
    if matching_choice not in ['1', '2']:
        print("Error: Invalid matching type choice")
        return None
    
    partial_matching = matching_choice == '2'
    
    # STEP 6: Get context window size
    try:
        context_window = int(input("Context window size (words before/after keyword, default 20): ") or "20")
        if context_window < 1:
            print("Error: Context window must be at least 1")
            return None
    except ValueError:
        print("Error: Please enter a valid number for context window")
        return None
    
    return {
        'name': name,
        'keywords': keywords,
        'collection_ids': selected_collections,
        'partial_matching': partial_matching,
        'context_window_words': context_window
    }


def show_analysis_sessions():
    """Display all analysis sessions."""
    sessions = db.get_analysis_sessions()
    
    if not sessions:
        print("No analysis sessions found.")
        return
    
    print("\n=== Analysis Sessions ===")
    print(f"{'ID':<12} {'Name':<25} {'Keywords':<10} {'Collections':<12} {'Status':<12} {'Created':<20}")
    print("="*90)
    
    for session in sessions:
        keywords = json.loads(session.keywords)
        collection_ids = json.loads(session.collection_ids)
        created_time = datetime.fromtimestamp(session.created_at).strftime("%Y-%m-%d %H:%M")
        
        # Truncate long IDs for display
        display_id = session.id[:10] + ".." if len(session.id) > 12 else session.id
        display_name = session.name[:23] + ".." if len(session.name) > 25 else session.name
        
        print(f"{display_id:<12} {display_name:<25} {len(keywords):<10} {len(collection_ids):<12} "
              f"{session.status:<12} {created_time:<20}")
    
    print("="*90)


def show_session_results(session_id: str):
    """Display detailed results for an analysis session."""
    try:
        results = analytics_engine.get_session_results(session_id)
        
        print(f"\n=== Analysis Results: {results['name']} ===")
        print(f"Session ID: {session_id}")
        print(f"Status: {results['status']}")
        created_time = datetime.fromtimestamp(results['created_at']).strftime("%Y-%m-%d %H:%M:%S")
        print(f"Created: {created_time}")
        print(f"Collections: {len(results['collection_ids'])} | Keywords: {len(results['keywords'])}")
        print(f"Matching: {'Partial' if results['partial_matching'] else 'Exact'}")
        print(f"Context Window: {results['context_window_words']} words")
        print()
        
        # Overall statistics
        print("OVERALL STATISTICS")
        print(f"├─ Total Mentions: {results['total_mentions']}")
        sentiment_label = "Positive" if results['avg_sentiment'] > 0 else "Negative" if results['avg_sentiment'] < 0 else "Neutral"
        print(f"├─ Average Sentiment: {results['avg_sentiment']:.4f} ({sentiment_label})")
        
        # Count posts and comments
        total_posts = sum(kw['posts_found_in'] for kw in results['keywords_data'])
        total_comments = sum(kw['comments_found_in'] for kw in results['keywords_data'])
        print(f"├─ Posts Found In: {total_posts}")
        print(f"└─ Comments Found In: {total_comments}")
        print()
        
        # Keyword breakdown
        if results['keywords_data']:
            print("KEYWORD BREAKDOWN")
            print("┌─────────────────┬───────────┬─────────────┬──────────────┐")
            print("│ Keyword         │ Mentions  │ Sentiment   │ Trend        │")
            print("├─────────────────┼───────────┼─────────────┼──────────────┤")
            
            for kw in results['keywords_data'][:10]:  # Show top 10 keywords
                keyword_display = kw['keyword'][:15] + ".." if len(kw['keyword']) > 17 else kw['keyword']
                sentiment_display = f"{kw['avg_sentiment']:+.3f}"
                
                # Simple trend indication (could be enhanced with actual trend calculation)
                if kw['avg_sentiment'] > 0.1:
                    trend = "↗️ Positive"
                elif kw['avg_sentiment'] < -0.1:
                    trend = "↘️ Negative"
                else:
                    trend = "→ Neutral"
                
                print(f"│ {keyword_display:<15} │ {kw['total_mentions']:<9} │ {sentiment_display:<11} │ {trend:<12} │")
            
            print("└─────────────────┴───────────┴─────────────┴──────────────┘")
            print()
        
        # Top keywords by mentions
        if len(results['keywords_data']) > 1:
            print("TOP KEYWORDS BY MENTIONS")
            top_by_mentions = sorted(results['keywords_data'], key=lambda x: x['total_mentions'], reverse=True)[:5]
            for i, kw in enumerate(top_by_mentions, 1):
                print(f"{i}. {kw['keyword']}: {kw['total_mentions']} mentions")
            print()
            
            # Top keywords by sentiment
            print("TOP KEYWORDS BY SENTIMENT")
            top_by_sentiment = sorted(results['keywords_data'], key=lambda x: x['avg_sentiment'], reverse=True)[:5]
            for i, kw in enumerate(top_by_sentiment, 1):
                print(f"{i}. {kw['keyword']}: {kw['avg_sentiment']:+.4f} sentiment")
            print()
        
    except Exception as e:
        print(f"Error retrieving session results: {e}")


def show_trends_analysis(session_id: str):
    """Display trends analysis for a session."""
    try:
        # Get session details to show available keywords
        results = analytics_engine.get_session_results(session_id)
        
        print(f"\n=== Trends Analysis: {results['name']} ===")
        print(f"Available keywords: {', '.join(results['keywords'])}")
        
        # Get user input for trend analysis
        keywords_input = input("Enter keywords to analyze (comma-separated, max 5): ").strip()
        if not keywords_input:
            print("No keywords specified.")
            return
        
        selected_keywords = [k.strip() for k in keywords_input.split(',') if k.strip()]
        selected_keywords = selected_keywords[:5]  # Limit to 5
        
        # Validate keywords
        valid_keywords = []
        for kw in selected_keywords:
            if kw in results['keywords']:
                valid_keywords.append(kw)
            else:
                print(f"Warning: Keyword '{kw}' not found in analysis session")
        
        if not valid_keywords:
            print("No valid keywords selected.")
            return
        
        # Get time period
        print("\nTime periods:")
        print("1. Daily")
        print("2. Weekly")
        print("3. Monthly")
        
        period_choice = input("Choose time period (1-3): ").strip()
        period_map = {'1': 'daily', '2': 'weekly', '3': 'monthly'}
        
        if period_choice not in period_map:
            print("Invalid time period choice.")
            return
        
        time_period = period_map[period_choice]
        
        # Get trends data
        trends_data = analytics_engine.get_trends(session_id, valid_keywords, time_period)
        
        if not trends_data['trends']:
            print("No trends data available.")
            return
        
        # Display trends
        print(f"\n=== {time_period.title()} Trends ===")
        print(f"Keywords: {', '.join(valid_keywords)}")
        print()
        
        # Format trends for display
        formatted_trends = []
        all_periods = set()
        
        for keyword, periods in trends_data['trends'].items():
            all_periods.update(periods.keys())
        
        sorted_periods = sorted(list(all_periods))
        
        if sorted_periods:
            print("┌─────────────┬─" + "─┬─".join(["─────────────"] * len(valid_keywords)) + "─┐")
            header = "│ Period      │ "
            for kw in valid_keywords:
                header += f"{kw[:11]:<11} │ "
            print(header)
            
            print("│             │ " + " │ ".join(["Men   Sent"] * len(valid_keywords)) + " │")
            print("├─────────────┼─" + "─┼─".join(["─────────────"] * len(valid_keywords)) + "─┤")
            
            for period in sorted_periods[-10:]:  # Show last 10 periods
                row = f"│ {period:<11} │ "
                
                for kw in valid_keywords:
                    if kw in trends_data['trends'] and period in trends_data['trends'][kw]:
                        data = trends_data['trends'][kw][period]
                        mentions = data['mentions']
                        sentiment = data['avg_sentiment']
                        row += f"{mentions:>3} {sentiment:>+.2f} │ "
                    else:
                        row += "  0  0.00 │ "
                
                print(row)
            
            print("└─────────────┴─" + "─┴─".join(["─────────────"] * len(valid_keywords)) + "─┘")
            print("\nMen = Mentions, Sent = Sentiment")
        
    except Exception as e:
        print(f"Error retrieving trends data: {e}")


def run_interactive_analysis():
    """Run interactive analysis creation."""
    try:
        # Get analysis parameters from user
        params = get_analysis_input()
        if params is None:
            return 1
        
        print("\n" + "="*50)
        print("Creating analysis session...")
        
        # Create analysis session
        session_id = analytics_engine.create_session(
            name=params['name'],
            keywords=params['keywords'],
            collection_ids=params['collection_ids'],
            partial_matching=params['partial_matching'],
            context_window_words=params['context_window_words']
        )
        
        print(f"Analysis session created: {session_id}")
        print("Starting analysis...")
        
        # Run analysis
        results = analytics_engine.run_analysis(session_id)
        
        print(f"\nAnalysis completed!")
        print(f"Session ID: {session_id}")
        print(f"Total mentions: {results['total_mentions']}")
        print(f"Average sentiment: {results['avg_sentiment']:.4f}")
        
        # Show brief results
        show_session_results(session_id)
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\nAnalysis interrupted by user")
        return 1
    except Exception as e:
        print(f"\nError: {e}")
        return 1


def delete_analysis_session(session_id: str):
    """Delete an analysis session."""
    try:
        # Check if session exists
        session = db.get_analysis_session(session_id)
        if not session:
            print(f"Analysis session not found: {session_id}")
            return 1
        
        # Confirm deletion
        print(f"Session: {session.name}")
        print(f"Created: {datetime.fromtimestamp(session.created_at).strftime('%Y-%m-%d %H:%M:%S')}")
        
        confirm = input("Are you sure you want to delete this session? (y/N): ").strip().lower()
        if confirm != 'y':
            print("Deletion cancelled.")
            return 0
        
        # Delete session
        if analytics_engine.delete_session(session_id):
            print(f"Analysis session deleted: {session_id}")
            return 0
        else:
            print(f"Failed to delete session: {session_id}")
            return 1
        
    except Exception as e:
        print(f"Error deleting session: {e}")
        return 1


def handle_analytics_commands(args):
    """
    Handle analytics-related CLI commands.
    
    Args:
        args: List of command-line arguments (excluding the program name)
    
    Returns:
        Exit code (0 for success, 1 for error)
    """
    if not args:
        print("Error: Analytics command required")
        return 1
    
    command = args[0]
    
    if command == "--analyze":
        return run_interactive_analysis()
    
    elif command == "--sessions":
        show_analysis_sessions()
        return 0
    
    elif command == "--results":
        if len(args) < 2:
            print("Error: Session ID required for --results")
            return 1
        
        session_id = args[1]
        show_session_results(session_id)
        return 0
    
    elif command == "--trends":
        if len(args) < 2:
            print("Error: Session ID required for --trends")
            return 1
        
        session_id = args[1]
        show_trends_analysis(session_id)
        return 0
    
    elif command == "--delete-session":
        if len(args) < 2:
            print("Error: Session ID required for --delete-session")
            return 1
        
        session_id = args[1]
        return delete_analysis_session(session_id)
    
    else:
        print(f"Unknown analytics command: {command}")
        return 1