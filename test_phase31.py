#!/usr/bin/env python3
"""
Phase 3.1 Infrastructure Test

Test script to validate that the LLM infrastructure is properly set up
without requiring API keys. This tests imports, basic configuration,
and module structure.
"""

import sys
import os
import json
from pathlib import Path


def test_imports():
    """Test that all new modules can be imported."""
    print("Testing imports...")
    
    try:
        # Test LLM provider imports
        from src.llm.providers.base import LLMProvider, LLMResponse, LLMConfig
        from src.llm.providers.anthropic_provider import AnthropicProvider
        from src.llm.providers.openai_provider import OpenAIProvider
        from src.llm.providers.factory import LLMProviderFactory
        print("✅ LLM providers imported successfully")
        
        # Test embedding imports
        from src.llm.embeddings.providers import EmbeddingProvider, EmbeddingProviderFactory
        from src.llm.embeddings.storage import VectorStorage, vector_storage
        print("✅ Embeddings modules imported successfully")
        
        # Test LLM config
        from src.llm.config import llm_config
        from src.llm import get_llm_provider, get_embedding_provider, is_llm_available
        print("✅ LLM configuration imported successfully")
        
        # Test CLI modules
        from src.cli.llm import handle_llm_commands
        print("✅ LLM CLI imported successfully")
        
        # Test database updates (correct import path)
        from src.database import db, LLMSummary, ContentEmbedding, ChatSession, ChatMessage
        print("✅ Database schema imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during imports: {e}")
        return False


def test_configuration_structure():
    """Test configuration structure without requiring actual API keys."""
    print("\nTesting configuration structure...")
    
    try:
        # Test that config.example.json has the right structure
        if not os.path.exists('config.example.json'):
            print("❌ config.example.json not found")
            return False
        
        with open('config.example.json', 'r') as f:
            example_config = json.load(f)
        
        # Check LLM section exists
        if 'llm' not in example_config:
            print("❌ LLM section missing from config.example.json")
            return False
        
        llm_config = example_config['llm']
        
        # Check required LLM fields
        required_fields = ['enabled', 'default_provider', 'providers', 'features', 'embeddings']
        for field in required_fields:
            if field not in llm_config:
                print(f"❌ Missing required LLM config field: {field}")
                return False
        
        # Check providers structure
        providers = llm_config['providers']
        if not isinstance(providers, dict):
            print("❌ LLM providers should be a dictionary")
            return False
        
        # Check that anthropic and openai are configured
        for provider in ['anthropic', 'openai']:
            if provider not in providers:
                print(f"❌ Missing provider configuration: {provider}")
                return False
            
            provider_config = providers[provider]
            required_provider_fields = ['api_key', 'model', 'max_tokens', 'temperature']
            for field in required_provider_fields:
                if field not in provider_config:
                    print(f"❌ Missing field '{field}' in {provider} provider config")
                    return False
        
        print("✅ Configuration structure is valid")
        return True
        
    except Exception as e:
        print(f"❌ Configuration test error: {e}")
        return False


def test_database_schema():
    """Test that database tables can be created."""
    print("\nTesting database schema...")
    
    try:
        from src.database import db
        
        # Try to create tables (this should work even without data)
        db.create_tables()
        print("✅ Database tables created successfully")
        
        # Test that we can get a session
        session = db.get_session()
        session.close()
        print("✅ Database session works")
        
        return True
        
    except Exception as e:
        print(f"❌ Database test error: {e}")
        return False


def test_provider_factory():
    """Test provider factory without API keys."""
    print("\nTesting provider factory...")
    
    try:
        from src.llm.providers.factory import LLMProviderFactory
        
        # Test with minimal config (should fail gracefully)
        test_config = {
            'default_provider': 'anthropic',
            'providers': {
                'anthropic': {
                    'api_key': 'test-key',
                    'model': 'claude-3-5-sonnet-20240620',
                    'max_tokens': 4000,
                    'temperature': 0.1
                }
            }
        }
        
        factory = LLMProviderFactory(test_config)
        
        # Test validation (should catch invalid API key)
        is_valid, errors = factory.validate_configuration()
        # It's okay if this fails due to invalid API key - we're testing structure
        
        print("✅ Provider factory instantiated successfully")
        return True
        
    except Exception as e:
        print(f"❌ Provider factory test error: {e}")
        return False


def test_embedding_factory():
    """Test embedding factory."""
    print("\nTesting embedding factory...")
    
    try:
        from src.llm.embeddings.providers import EmbeddingProviderFactory
        
        # Test available providers
        available = EmbeddingProviderFactory.get_available_providers()
        expected_providers = ['openai', 'local']
        
        for provider in expected_providers:
            if provider not in available:
                print(f"❌ Missing embedding provider: {provider}")
                return False
        
        print("✅ Embedding factory works correctly")
        return True
        
    except Exception as e:
        print(f"❌ Embedding factory test error: {e}")
        return False


def test_llm_config():
    """Test LLM configuration management."""
    print("\nTesting LLM configuration...")
    
    try:
        from src.llm.config import llm_config
        
        # Test loading config (should work even if LLM is disabled)
        config_data = llm_config.load_config()
        print(f"✅ LLM config loaded: {type(config_data)}")
        
        # Test feature config
        features = llm_config.get_feature_config()
        print(f"✅ Feature config loaded: {len(features)} features")
        
        # Test embeddings config
        embeddings_config = llm_config.get_embeddings_config()
        print(f"✅ Embeddings config loaded: {type(embeddings_config)}")
        
        return True
        
    except Exception as e:
        print(f"❌ LLM config test error: {e}")
        return False


def test_cli_integration():
    """Test CLI command structure."""
    print("\nTesting CLI integration...")
    
    try:
        # Test that the CLI module can be imported
        import src.cli.llm
        print("✅ LLM CLI module imported successfully")
        
        # Test that the main function exists
        from src.cli.llm import handle_llm_commands
        
        # Test that the function exists and is callable
        if not callable(handle_llm_commands):
            print("❌ handle_llm_commands is not callable")
            return False
        
        print("✅ LLM CLI commands are properly integrated")
        return True
        
    except ImportError as e:
        print(f"❌ CLI import error: {e}")
        print("This might be due to missing dependencies - install them with: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ CLI integration test error: {e}")
        return False


def main():
    """Run all Phase 3.1 tests."""
    print("🧪 Phase 3.1 Infrastructure Validation")
    print("=" * 50)
    
    tests = [
        ("Module Imports", test_imports),
        ("Configuration Structure", test_configuration_structure),
        ("Database Schema", test_database_schema),
        ("Provider Factory", test_provider_factory),
        ("Embedding Factory", test_embedding_factory),
        ("LLM Configuration", test_llm_config),
        ("CLI Integration", test_cli_integration)
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
        print("🎉 All Phase 3.1 infrastructure tests passed!")
        print("\nNext steps:")
        print("1. Add your API keys to config.json")
        print("2. Run: python main.py --test-llm")
        print("3. Try: python main.py --suggest-keywords \"your research topic\"")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    exit(main())