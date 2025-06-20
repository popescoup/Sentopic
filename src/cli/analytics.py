"""
Analytics CLI

Command-line interface for Phase 2 analytics functionality.
Enhanced with Phase 3.3 summarization and Phase 3.4 chat features.
"""

import json
from datetime import datetime
from typing import List
from ..analytics import analytics_engine
from ..database import db
from ..llm import is_llm_available


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
    
    # STEP 7: AI Summary options (if LLM available)
    generate_summary = False
    user_query = None
    
    if is_llm_available():
        print("\n🤖 AI Summary Options:")
        print("Generate an AI summary of analysis findings? This will provide")
        print("intelligent insights about sentiment patterns, trends, and key discoveries.")
        
        summary_choice = input("\nGenerate AI summary? (y/N): ").strip().lower()
        if summary_choice == 'y':
            generate_summary = True
            
            print("\nOptional: Describe what you're researching or investigating.")
            print("This helps the AI provide more relevant insights.")
            user_query = input("Research description (press Enter to skip): ").strip()
            if not user_query:
                user_query = None
    else:
        print("\n💡 AI Summary: Not available (LLM not configured)")
        print("   Enable LLM features in config.json to use AI summaries")
    
    return {
        'name': name,
        'keywords': keywords,
        'collection_ids': selected_collections,
        'partial_matching': partial_matching,
        'context_window_words': context_window,
        'generate_summary': generate_summary,
        'user_query': user_query
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
        # Get results with summary if available
        results = analytics_engine.get_session_results_with_summary(session_id)
        
        print(f"\n=== Analysis Results: {results['name']} ===")
        print(f"Session ID: {session_id}")
        print(f"Status: {results['status']}")
        created_time = datetime.fromtimestamp(results['created_at']).strftime("%Y-%m-%d %H:%M:%S")
        print(f"Created: {created_time}")
        print(f"Collections: {len(results['collection_ids'])} | Keywords: {len(results['keywords'])}")
        print(f"Matching: {'Partial' if results['partial_matching'] else 'Exact'}")
        print(f"Context Window: {results['context_window_words']} words")
        
        # Display AI Summary if available
        if 'summary' in results and results['summary']:
            summary = results['summary']
            print(f"\n🤖 AI SUMMARY")
            print("=" * 50)
            print(summary['summary'])
            print("=" * 50)
            
            # Show summary metadata
            metadata = summary.get('metadata', {})
            print(f"Generated: {metadata.get('generated_at', 'Unknown')}")
            print(f"Provider: {metadata.get('provider', 'Unknown')} ({metadata.get('model', 'Unknown')})")
            if metadata.get('tokens_used'):
                print(f"Tokens used: {metadata['tokens_used']}")
            if metadata.get('cost_estimate'):
                print(f"Cost estimate: ${metadata['cost_estimate']:.4f}")
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
        
        # Chat availability notice
        if is_llm_available():
            print("💬 INTERACTIVE CHAT")
            print("Ask questions about your data with:")
            print(f"   python main.py --chat {session_id}")
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
            
            for period in sorted_periods:  # Show all periods
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


def show_session_summary(session_id: str):
    """Display summary for an analysis session."""
    try:
        summary = analytics_engine.get_session_summary(session_id)
        
        if not summary:
            print(f"No AI summary found for session {session_id}")
            print("Generate a summary with: python main.py --generate-summary <session_id>")
            return 1
        
        print(f"\n🤖 AI SUMMARY FOR SESSION: {session_id}")
        print("=" * 60)
        print(summary['summary'])
        print("=" * 60)
        
        metadata = summary.get('metadata', {})
        print(f"Generated: {metadata.get('generated_at', 'Unknown')}")
        print(f"Provider: {metadata.get('provider', 'Unknown')} ({metadata.get('model', 'Unknown')})")
        if metadata.get('tokens_used'):
            print(f"Tokens used: {metadata['tokens_used']}")
        if metadata.get('cost_estimate'):
            print(f"Cost estimate: ${metadata['cost_estimate']:.4f}")
        
        if summary.get('user_query'):
            print(f"\nOriginal research query: \"{summary['user_query']}\"")
        
        return 0
        
    except Exception as e:
        print(f"Error retrieving summary: {e}")
        return 1


def generate_session_summary(session_id: str):
    """Generate or regenerate summary for a session."""
    try:
        if not is_llm_available():
            print("❌ LLM not available. Cannot generate summaries.")
            print("Enable LLM features in config.json to use summaries.")
            return 1
        
        # Check if session exists
        session = db.get_analysis_session(session_id)
        if not session:
            print(f"Analysis session not found: {session_id}")
            return 1
        
        if session.status != 'completed':
            print(f"Analysis session not completed: {session.status}")
            print("Complete the analysis before generating summary.")
            return 1
        
        # Get optional user query
        print("Optional: Describe what you were researching or investigating.")
        print("This helps the AI provide more relevant insights.")
        user_query = input("Research description (press Enter to skip): ").strip()
        if not user_query:
            user_query = None
        
        print("\n🤖 Generating AI summary...")
        
        # Check if summary already exists
        existing_summary = analytics_engine.get_session_summary(session_id)
        if existing_summary:
            print("⚠️  A summary already exists for this session.")
            regenerate = input("Regenerate summary? (y/N): ").strip().lower()
            if regenerate != 'y':
                print("Summary generation cancelled.")
                return 0
        
        # Generate summary
        summary_result = analytics_engine.regenerate_session_summary(session_id, user_query)
        
        print("✅ Summary generated successfully!")
        print(f"Tokens used: {summary_result['metadata']['tokens_used']}")
        print(f"Cost estimate: ${summary_result['metadata']['cost_estimate']:.4f}")
        
        # Show the summary
        show_session_summary(session_id)
        
        return 0
        
    except Exception as e:
        print(f"Error generating summary: {e}")
        return 1


def run_chat_session(session_id: str):
    """Run interactive chat session."""
    try:
        if not is_llm_available():
            print("❌ LLM not available. Cannot start chat session.")
            print("Enable LLM features in config.json to use chat.")
            return 1
        
        # Import chat agent
        from ..llm.services.chat_agent import chat_agent
        from ..llm.embeddings.indexer import content_indexer
        
        # Validate analysis session
        analysis_session = db.get_analysis_session(session_id)
        if not analysis_session:
            print(f"Analysis session not found: {session_id}")
            return 1
        
        if analysis_session.status != 'completed':
            print(f"Analysis session not completed: {analysis_session.status}")
            print("Complete the analysis before starting chat.")
            return 1
        
        print(f"🚀 Starting chat for analysis: {analysis_session.name}")
        
        # Check indexing status
        indexing_status = content_indexer.get_indexing_status(session_id)
        search_capabilities = indexing_status['search_capabilities']
        
        print(f"\n🔍 Search capabilities:")
        print(f"   Keyword search: {'✅ Available' if search_capabilities['keyword'] else '❌ Not available'}")
        print(f"   Local semantic: {'✅ Available' if search_capabilities['local_semantic'] else '⚠️  Requires indexing'}")
        print(f"   Cloud semantic: {'✅ Available' if search_capabilities['cloud_semantic'] else '⚠️  Requires indexing'}")
        
        # Check if any chat sessions exist
        existing_sessions = chat_agent.list_chat_sessions(session_id)
        
        if existing_sessions:
            print(f"\n💬 Found {len(existing_sessions)} existing chat session(s):")
            for i, session_info in enumerate(existing_sessions, 1):
                created_time = datetime.fromtimestamp(session_info['created_at']).strftime("%Y-%m-%d %H:%M")
                print(f"   {i}. {session_info['preview']} (Created: {created_time})")
            
            print(f"\n0. Start new chat session")
            choice = input("Choose session (0 for new): ").strip()
            
            if choice == '0':
                chat_session_id = chat_agent.start_chat_session(session_id)
                print(f"✅ New chat session started: {chat_session_id}")
            else:
                try:
                    session_index = int(choice) - 1
                    if 0 <= session_index < len(existing_sessions):
                        chat_session_id = existing_sessions[session_index]['session_id']
                        print(f"✅ Resuming chat session: {chat_session_id}")
                    else:
                        print("Invalid session choice. Starting new session.")
                        chat_session_id = chat_agent.start_chat_session(session_id)
                except ValueError:
                    print("Invalid input. Starting new session.")
                    chat_session_id = chat_agent.start_chat_session(session_id)
        else:
            chat_session_id = chat_agent.start_chat_session(session_id)
            print(f"✅ Chat session started: {chat_session_id}")
        
        # Show initial chat history
        history = chat_agent.get_chat_history(chat_session_id, limit=10)
        for message in history[-5:]:  # Show last 5 messages
            role_icon = "🤖" if message['role'] == 'assistant' else "👤"
            print(f"\n{role_icon} {message['role'].title()}: {message['content']}")
        
        # Start interactive chat loop
        current_search_type = 'keyword'
        print(f"\n{'='*60}")
        print("💬 Chat started! Type your questions or commands:")
        print("   'switch to local' - Use local semantic search")
        print("   'switch to cloud' - Use cloud semantic search") 
        print("   'switch to keyword' - Use keyword search")
        print("   'index local' - Index content for local semantic search")
        print("   'index cloud' - Index content for cloud semantic search")
        print("   'exit' or 'quit' - End chat session")
        print(f"   Current search mode: {current_search_type}")
        print(f"{'='*60}")
        
        while True:
            try:
                user_input = input("\n👤 You: ").strip()
                
                if not user_input:
                    continue
                
                # Handle exit commands
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    print("👋 Chat session ended. Your conversation has been saved.")
                    break
                
                # Handle search mode switching
                if user_input.lower().startswith('switch to '):
                    new_mode = user_input.lower().replace('switch to ', '').strip()
                    if new_mode in ['keyword', 'local', 'cloud']:
                        search_mode_map = {
                            'keyword': 'keyword',
                            'local': 'local_semantic', 
                            'cloud': 'cloud_semantic'
                        }
                        current_search_type = search_mode_map[new_mode]
                        print(f"🔍 Switched to {new_mode} search mode")
                        continue
                    else:
                        print("❌ Invalid search mode. Use: keyword, local, or cloud")
                        continue
                
                # Handle indexing commands
                if user_input.lower() in ['index local', 'index cloud']:
                    provider_type = 'local' if 'local' in user_input.lower() else 'openai'
                    
                    print(f"🔍 Starting {provider_type} indexing...")
                    if provider_type == 'local':
                        print("   This is free but may take 2-3 minutes")
                    else:
                        print("   This uses OpenAI API tokens and costs money")
                    
                    confirm = input("Continue? (y/N): ").strip().lower()
                    if confirm == 'y':
                        try:
                            result = content_indexer.index_analysis_content(session_id, provider_type)
                            print(f"✅ {result['message']}")
                            if result.get('cost_estimate', 0) > 0:
                                print(f"💰 Cost: ${result['cost_estimate']:.4f}")
                        except Exception as e:
                            print(f"❌ Indexing failed: {e}")
                    continue
                
                # Send message to chat agent
                print("🤖 Assistant: ", end="", flush=True)
                
                response = chat_agent.send_message(chat_session_id, user_input, current_search_type)
                print(response.message)
                
                # Show sources if available
                if response.sources:
                    print(f"\n📚 Sources ({len(response.sources)} found):")
                    for i, source in enumerate(response.sources[:3], 1):  # Show top 3 sources
                        content_type = source['content_type'].title()
                        author = source.get('author', 'Unknown')
                        print(f"   {i}. {content_type} by {author} (ID: {source['content_id']}) - {source['preview']}")
                    
                    if len(response.sources) > 3:
                        print(f"   ... and {len(response.sources) - 3} more sources")
                
                # Show cost info if significant
                if response.cost_estimate > 0.001:
                    print(f"\n💰 Tokens: {response.tokens_used}, Cost: ${response.cost_estimate:.4f}")
                
            except KeyboardInterrupt:
                print("\n\n👋 Chat session ended.")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                continue
        
        return 0
        
    except Exception as e:
        print(f"Error starting chat: {e}")
        return 1


def index_content_for_session(session_id: str):
    """Index content for semantic search."""
    try:
        if not is_llm_available():
            print("❌ LLM not available. Cannot index content.")
            return 1
        
        from ..llm.embeddings.indexer import content_indexer
        
        # Check if session exists
        session = db.get_analysis_session(session_id)
        if not session:
            print(f"Analysis session not found: {session_id}")
            return 1
        
        if session.status != 'completed':
            print(f"Analysis session not completed: {session.status}")
            return 1
        
        # Show current indexing status
        status = content_indexer.get_indexing_status(session_id)
        print(f"\n📊 Indexing Status for: {session.name}")
        print(f"   Total content items: {status['total_content_items']}")
        print(f"   Local embeddings: {status['local_indexed']}")
        print(f"   Cloud embeddings: {status['cloud_indexed']}")
        
        # Choose indexing type
        print("\n🔍 Indexing Options:")
        print("1. Local indexing (free, uses sentence-transformers)")
        print("2. Cloud indexing (paid, uses OpenAI embeddings)")
        
        choice = input("Choose indexing type (1-2): ").strip()
        
        if choice == '1':
            provider_type = 'local'
            print("\n🆓 Local indexing selected - this is free but may take 2-3 minutes")
        elif choice == '2':
            provider_type = 'openai'
            print("\n💰 Cloud indexing selected - this uses OpenAI API tokens")
        else:
            print("Invalid choice.")
            return 1
        
        # Confirm indexing
        confirm = input("Start indexing? (y/N): ").strip().lower()
        if confirm != 'y':
            print("Indexing cancelled.")
            return 0
        
        # Run indexing
        result = content_indexer.index_analysis_content(session_id, provider_type)
        
        print(f"\n✅ {result['message']}")
        if result.get('cost_estimate', 0) > 0:
            print(f"💰 Total cost: ${result['cost_estimate']:.4f}")
        
        return 0
        
    except Exception as e:
        print(f"Error indexing content: {e}")
        return 1


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
        
        # Run analysis with optional summary
        if params.get('generate_summary', False):
            results = analytics_engine.run_analysis_with_summary(
                session_id, 
                params.get('user_query'),
                generate_summary=True
            )
        else:
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
    
    elif command == "--show-summary":
        if len(args) < 2:
            print("Error: Session ID required for --show-summary")
            return 1
        
        session_id = args[1]
        return show_session_summary(session_id)
    
    elif command == "--generate-summary":
        if len(args) < 2:
            print("Error: Session ID required for --generate-summary")
            return 1
        
        session_id = args[1]
        return generate_session_summary(session_id)
    
    elif command == "--chat":
        if len(args) < 2:
            print("Error: Session ID required for --chat")
            return 1
        
        session_id = args[1]
        return run_chat_session(session_id)
    
    elif command == "--index-content":
        if len(args) < 2:
            print("Error: Session ID required for --index-content")
            return 1
        
        session_id = args[1]
        return index_content_for_session(session_id)
    
    else:
        print(f"Unknown analytics command: {command}")
        return 1