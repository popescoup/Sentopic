"""
LLM Configuration Management

Handles configuration for LLM providers, validation, and integration
with the existing Sentopic configuration system.
"""

from typing import Dict, Any, Optional, List, Tuple
from ..config import config as sentopic_config
from .providers import LLMProviderFactory


class LLMConfig:
    """
    LLM configuration manager that integrates with Sentopic's config system.
    
    Handles loading, validation, and management of LLM provider configurations.
    """
    
    def __init__(self):
        self._config = None
        self._factory = None
        self._is_enabled = False
    
    def load_config(self) -> Dict[str, Any]:
        """
        Load LLM configuration from the main config file.
        
        Returns:
            LLM configuration dictionary
        """
        if self._config is None:
            try:
                main_config = sentopic_config.load_config()
                self._config = main_config.get('llm', {})
                self._is_enabled = self._config.get('enabled', False)
            except Exception as e:
                # If config fails to load, use empty config (LLM disabled)
                self._config = {}
                self._is_enabled = False
        
        return self._config
    
    def is_enabled(self) -> bool:
        """
        Check if LLM features are enabled.
        
        Returns:
            True if LLM features should be available
        """
        self.load_config()
        return self._is_enabled
    
    def get_factory(self) -> Optional[LLMProviderFactory]:
        """
        Get the LLM provider factory.
        
        Returns:
            LLMProviderFactory instance, or None if LLM is disabled
        """
        if not self.is_enabled():
            return None
        
        if self._factory is None:
            llm_config = self.load_config()
            self._factory = LLMProviderFactory(llm_config)
        
        return self._factory
    
    def validate_configuration(self) -> Tuple[bool, List[str]]:
        """
        Validate the complete LLM configuration.
        
        Returns:
            Tuple of (is_valid: bool, error_messages: List[str])
        """
        errors = []
        
        if not self.is_enabled():
            return True, []  # Valid to have LLM disabled
        
        try:
            factory = self.get_factory()
            if factory is None:
                errors.append("LLM is enabled but factory could not be created")
                return False, errors
            
            is_valid, factory_errors = factory.validate_configuration()
            errors.extend(factory_errors)
            
            # Check if at least one provider is available
            available_providers = factory.get_available_providers()
            if not available_providers:
                errors.append("No LLM providers are properly configured")
            
        except Exception as e:
            errors.append(f"LLM configuration error: {str(e)}")
        
        return len(errors) == 0, errors
    
    def get_available_providers(self) -> List[str]:
        """
        Get list of available and configured providers.
        
        Returns:
            List of provider names, empty if LLM is disabled
        """
        if not self.is_enabled():
            return []
        
        factory = self.get_factory()
        if factory is None:
            return []
        
        return factory.get_available_providers()
    
    def test_providers(self) -> Dict[str, Tuple[bool, str]]:
        """
        Test all configured providers.
        
        Returns:
            Dictionary mapping provider names to (success, message) tuples
        """
        if not self.is_enabled():
            return {}
        
        factory = self.get_factory()
        if factory is None:
            return {}
        
        return factory.test_all_providers()
    
    def get_default_provider(self) -> Optional[str]:
        """
        Get the default provider name.
        
        Returns:
            Default provider name, or None if LLM is disabled
        """
        if not self.is_enabled():
            return None
        
        llm_config = self.load_config()
        return llm_config.get('default_provider', 'anthropic')
    
    def get_provider_config(self, provider_name: str) -> Optional[Dict[str, Any]]:
        """
        Get configuration for a specific provider.
        
        Args:
            provider_name: Name of the provider
        
        Returns:
            Provider configuration dictionary, or None if not found
        """
        if not self.is_enabled():
            return None
        
        llm_config = self.load_config()
        providers_config = llm_config.get('providers', {})
        return providers_config.get(provider_name)
    
    def get_feature_config(self) -> Dict[str, bool]:
        """
        Get LLM feature enable/disable settings.
        
        Returns:
            Dictionary of feature flags
        """
        if not self.is_enabled():
            return {
                'keyword_suggestion': False,
                'summarization': False,
                'rag_search': False,
                'chat_agent': False
            }
        
        llm_config = self.load_config()
        features = llm_config.get('features', {})
        
        return {
            'keyword_suggestion': features.get('keyword_suggestion', True),
            'summarization': features.get('summarization', True),
            'rag_search': features.get('rag_search', True),
            'chat_agent': features.get('chat_agent', True)
        }
    
    def is_feature_enabled(self, feature_name: str) -> bool:
        """
        Check if a specific LLM feature is enabled.
        
        Args:
            feature_name: Name of the feature to check
        
        Returns:
            True if the feature is enabled
        """
        features = self.get_feature_config()
        return features.get(feature_name, False)
    
    def get_embeddings_config(self) -> Dict[str, Any]:
        """
        Get embeddings configuration for semantic search.
        
        Returns:
            Embeddings configuration dictionary
        """
        if not self.is_enabled():
            return {}
        
        llm_config = self.load_config()
        return llm_config.get('embeddings', {
            'provider': 'openai',
            'model': 'text-embedding-ada-002',
            'storage': 'sqlite'
        })
    
    def get_usage_summary(self) -> Dict[str, Any]:
        """
        Get usage summary for all providers.
        
        Returns:
            Dictionary with usage statistics
        """
        if not self.is_enabled():
            return {}
        
        factory = self.get_factory()
        if factory is None:
            return {}
        
        return factory.get_usage_summary()
    
    def reload_config(self):
        """Force reload of configuration from file."""
        self._config = None
        self._factory = None
        self._is_enabled = False


# Global LLM config instance
llm_config = LLMConfig()