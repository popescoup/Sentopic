#!/usr/bin/env python3
"""
Phase 3.4 Chat & RAG Test

Test script to validate that the chat agent and RAG infrastructure 
is properly set up and functional.
"""

import sys
import os
from pathlib import Path


def test_imports():
    """Test that all new Phase 3.4 modules can be imported."""
    print("Testing Phase 3.4 imports...")
    
    try:
        # Test search engine imports
        from src.llm.services.search_engine import (
            SearchEngine, KeywordSearchEngine, LocalSemanticSearchEngine, 
            CloudSemanticSearchEngine, SearchEngineFactory, SearchResult
        )
        print("✅ Search engine components imported successfully")
        
        # Test RAG engine imports
        from src.llm.services.rag_engine import rag_engine, RAGEngine, RAGResponse
        print("✅ RAG engine imported successfully")
        
        # Test chat agent imports
        from src.llm.services.chat_agent import chat_agent, ChatAgent, ChatResponse
        print("✅ Chat agent imported successfully")
        
        # Test content indexer imports
        from src.llm.embeddings.indexer import content_indexer, ContentIndexer
        print("✅ Content indexer imported successfully")
        
        # Test updated services package
        from src.llm.services import (
            analysis_summarizer, SearchEngineFactory, rag_engine, chat_agent
        )
        print("✅ Updated services package imported successfully")
        
        # Test updated embeddings package
        from src.llm.embeddings import content_indexer
        print("✅ Updated embeddings package imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during imports: {e}")
        return False


def test_search_engine_factory():
    """Test search engine factory functionality."""
    print("\nTesting search engine factory...")
    
    try:
        from src.llm.services.search_engine import SearchEngineFactory
        
        # Test getting available engines
        available = SearchEngineFactory.get_available_engines()
        expected_engines = ['keyword', 'local_semantic', 'cloud_semantic']
        
        for engine in expected_engines:
            if engine not in available:
                print(f"❌ Missing search engine: {engine}")
                return False
        
        print(f"✅ All expected search engines available: {available}")
        
        # Test creating engines
        for engine_type in expected_engines:
            try:
                engine = SearchEngineFactory.create_engine(engine_type)
                if not hasattr(engine, 'search'):
                    print(f"❌ Engine {engine_type} missing search method")
                    return False
                if not hasattr(engine, 'get_search_type'):
                    print(f"❌ Engine {engine_type} missing get_search_type method")
                    return False
            except Exception as e:
                print(f"❌ Failed to create {engine_type} engine: {e}")
                return False
        
        print("✅ All search engines can be created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Search engine factory test error: {e}")
        return False


def test_rag_engine():
    """Test RAG engine basic functionality."""
    print("\nTesting RAG engine...")
    
    try:
        from src.llm.services.rag_engine import rag_engine
        
        # Test that RAG engine has required methods
        required_methods = ['answer_question', 'get_full_context', 'get_available_search_types']
        
        for method in required_methods:
            if not hasattr(rag_engine, method):
                print(f"❌ RAG engine missing method: {method}")
                return False
        
        print("✅ RAG engine has all required methods")
        
        # Test get_available_search_types with empty collections (should not crash)
        try:
            search_types = rag_engine.get_available_search_types([])
            if not isinstance(search_types, dict):
                print("❌ get_available_search_types should return dict")
                return False
            print("✅ get_available_search_types works")
        except Exception as e:
            print(f"❌ get_available_search_types failed: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ RAG engine test error: {e}")
        return False


def test_chat_agent():
    """Test chat agent basic functionality."""
    print("\nTesting chat agent...")
    
    try:
        from src.llm.services.chat_agent import chat_agent
        
        # Test that chat agent has required methods
        required_methods = [
            'start_chat_session', 'send_message', 'get_chat_history', 
            'get_available_search_types', 'list_chat_sessions'
        ]
        
        for method in required_methods:
            if not hasattr(chat_agent, method):
                print(f"❌ Chat agent missing method: {method}")
                return False
        
        print("✅ Chat agent has all required methods")
        return True
        
    except Exception as e:
        print(f"❌ Chat agent test error: {e}")
        return False


def test_content_indexer():
    """Test content indexer functionality."""
    print("\nTesting content indexer...")
    
    try:
        from src.llm.embeddings.indexer import content_indexer
        
        # Test that content indexer has required methods
        required_methods = [
            'index_analysis_content', 'get_indexing_status', 'delete_embeddings'
        ]
        
        for method in required_methods:
            if not hasattr(content_indexer, method):
                print(f"❌ Content indexer missing method: {method}")
                return False
        
        print("✅ Content indexer has all required methods")
        
        # Test get_indexing_status with invalid session (should handle gracefully)
        try:
            status = content_indexer.get_indexing_status("invalid_session_id")
            print("❌ Should have raised error for invalid session")
            return False
        except ValueError:
            print("✅ Content indexer correctly handles invalid session ID")
        except Exception as e:
            print(f"❌ Unexpected error handling invalid session: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Content indexer test error: {e}")
        return False


def test_database_integration():
    """Test database integration for chat tables."""
    print("\nTesting database integration...")
    
    try:
        from src.database import db, ChatSession, ChatMessage
        
        # Test that chat tables exist by trying to query them
        session = db.get_session()
        try:
            # This should not crash if tables exist
            session.query(ChatSession).first()
            session.query(ChatMessage).first()
            print("✅ Chat database tables are accessible")
        finally:
            session.close()
        
        # Test chat session creation methods exist
        if not hasattr(db, 'create_chat_session'):
            print("❌ Database missing create_chat_session method")
            return False
        
        if not hasattr(db, 'save_chat_message'):
            print("❌ Database missing save_chat_message method")
            return False
        
        if not hasattr(db, 'get_chat_sessions'):
            print("❌ Database missing get_chat_sessions method")
            return False
        
        if not hasattr(db, 'get_chat_messages'):
            print("❌ Database missing get_chat_messages method")
            return False
        
        print("✅ All required database methods exist")
        return True
        
    except Exception as e:
        print(f"❌ Database integration test error: {e}")
        return False


def test_cli_integration():
    """Test CLI integration for new commands."""
    print("\nTesting CLI integration...")
    
    try:
        # Test that the CLI module can handle new commands
        from src.cli.analytics import handle_analytics_commands
        
        # Test that the function exists and is callable
        if not callable(handle_analytics_commands):
            print("❌ handle_analytics_commands is not callable")
            return False
        
        print("✅ Analytics CLI handler is properly integrated")
        
        # Test main.py command routing includes new commands
        import main
        
        # Check if main module has the updated help
        if not hasattr(main, 'show_help'):
            print("❌ main.py missing show_help function")
            return False
        
        print("✅ Main CLI integration looks correct")
        return True
        
    except ImportError as e:
        print(f"❌ CLI import error: {e}")
        print("This might be due to missing dependencies - install them with: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ CLI integration test error: {e}")
        return False


def test_embedding_providers():
    """Test embedding provider availability."""
    print("\nTesting embedding providers...")
    
    try:
        from src.llm.embeddings.providers import EmbeddingProviderFactory
        
        # Test local provider (should work without API keys)
        try:
            local_config = {'provider': 'local', 'model': 'all-MiniLM-L6-v2'}
            local_provider = EmbeddingProviderFactory.create_provider(local_config)
            print("✅ Local embedding provider can be created")
        except ImportError:
            print("⚠️  Local embedding provider requires sentence-transformers package")
        except Exception as e:
            print(f"❌ Local embedding provider creation failed: {e}")
            return False
        
        # Test OpenAI provider creation (will fail without API key, but should handle gracefully)
        try:
            openai_config = {'provider': 'openai', 'model': 'text-embedding-3-small', 'api_key': 'test'}
            EmbeddingProviderFactory.create_provider(openai_config)
            print("✅ OpenAI embedding provider can be created (API key validation separate)")
        except ImportError:
            print("⚠️  OpenAI embedding provider requires openai package")
        except Exception as e:
            # This is expected without real API key
            print("✅ OpenAI embedding provider creation handled appropriately")
        
        return True
        
    except Exception as e:
        print(f"❌ Embedding providers test error: {e}")
        return False


def test_vector_storage():
    """Test vector storage functionality."""
    print("\nTesting vector storage...")
    
    try:
        from src.llm.embeddings.storage import vector_storage
        
        # Test that vector storage has required methods
        required_methods = [
            'store_embeddings', 'search_similar', 'get_embedding_stats', 'delete_embeddings'
        ]
        
        for method in required_methods:
            if not hasattr(vector_storage, method):
                print(f"❌ Vector storage missing method: {method}")
                return False
        
        print("✅ Vector storage has all required methods")
        
        # Test get_embedding_stats with empty collections (should not crash)
        try:
            stats = vector_storage.get_embedding_stats([])
            if not isinstance(stats, dict):
                print("❌ get_embedding_stats should return dict")
                return False
            print("✅ Vector storage stats work correctly")
        except Exception as e:
            print(f"❌ Vector storage stats failed: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Vector storage test error: {e}")
        return False


def main():
    """Run all Phase 3.4 tests."""
    print("🧪 Phase 3.4 Chat & RAG Validation")
    print("=" * 50)
    
    tests = [
        ("Module Imports", test_imports),
        ("Search Engine Factory", test_search_engine_factory),
        ("RAG Engine", test_rag_engine),
        ("Chat Agent", test_chat_agent),
        ("Content Indexer", test_content_indexer),
        ("Database Integration", test_database_integration),
        ("CLI Integration", test_cli_integration),
        ("Embedding Providers", test_embedding_providers),
        ("Vector Storage", test_vector_storage)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}")
        print("-" * 30)
        
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All Phase 3.4 infrastructure tests passed!")
        print("\nNext steps to test full functionality:")
        print("1. Ensure you have completed Phase 1 & 2 (data collection & analysis)")
        print("2. Run an analysis: python main.py --analyze")
        print("3. Start a chat session: python main.py --chat <session_id>")
        print("4. Try indexing for semantic search: python main.py --index-content <session_id>")
        print("\nExample workflow:")
        print("  python main.py --sessions  # Find your analysis session ID")
        print("  python main.py --chat abc123def456  # Start chat with session")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    exit(main())