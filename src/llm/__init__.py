"""
LLM Integration Package

This package provides LLM capabilities for Sentopic, including:
- Multiple LLM provider support (Anthropic, OpenAI)
- Embeddings for semantic search
- Configuration management
- Vector storage for similarity search

Main entry points:
- llm_config: Configuration management
- LLMProviderFactory: Create LLM providers
- EmbeddingProviderFactory: Create embedding providers
- vector_storage: Vector storage for semantic search
"""

from .config import llm_config
from .providers import (
    LLMProvider, 
    LLMResponse, 
    LLMConfig, 
    LLMProviderFactory,
    AnthropicProvider,
    OpenAIProvider
)
from .embeddings import (
    EmbeddingProvider,
    EmbeddingProviderFactory,
    vector_storage
)

# Global instances for easy access
def get_llm_provider(provider_name: str = None):
    """
    Get an LLM provider instance.
    
    Args:
        provider_name: Specific provider to use, or None for default
    
    Returns:
        LLMProvider instance, or None if LLM is disabled
    """
    if not llm_config.is_enabled():
        return None
    
    factory = llm_config.get_factory()
    if factory is None:
        return None
    
    return factory.get_provider(provider_name)


def get_embedding_provider():
    """
    Get an embedding provider instance based on configuration.
    
    Returns:
        EmbeddingProvider instance, or None if LLM/embeddings disabled
    """
    if not llm_config.is_enabled() or not llm_config.is_feature_enabled('rag_search'):
        return None
    
    embeddings_config = llm_config.get_embeddings_config()
    
    # Add API key from LLM provider config if using OpenAI embeddings
    if embeddings_config.get('provider') == 'openai':
        openai_config = llm_config.get_provider_config('openai')
        if openai_config and openai_config.get('api_key'):
            embeddings_config['api_key'] = openai_config['api_key']
    
    try:
        return EmbeddingProviderFactory.create_provider(embeddings_config)
    except Exception:
        return None


def is_llm_available() -> bool:
    """
    Check if LLM features are available and working.
    
    Returns:
        True if at least one LLM provider is available
    """
    if not llm_config.is_enabled():
        return False
    
    available_providers = llm_config.get_available_providers()
    return len(available_providers) > 0


def is_embeddings_available() -> bool:
    """
    Check if embedding features are available.
    
    Returns:
        True if embeddings can be generated
    """
    if not llm_config.is_enabled() or not llm_config.is_feature_enabled('rag_search'):
        return False
    
    provider = get_embedding_provider()
    return provider is not None


__all__ = [
    'llm_config',
    'LLMProvider',
    'LLMResponse', 
    'LLMConfig',
    'LLMProviderFactory',
    'AnthropicProvider',
    'OpenAIProvider',
    'EmbeddingProvider',
    'EmbeddingProviderFactory',
    'vector_storage',
    'get_llm_provider',
    'get_embedding_provider',
    'is_llm_available',
    'is_embeddings_available'
]