"""
LLM Provider Factory

Factory class for creating and managing LLM providers.
Handles provider selection, configuration, and fallback logic.
"""

from typing import Dict, List, Optional, Any
from .base import LLMProvider, LLMConfig
from .anthropic_provider import AnthropicProvider
from .openai_provider import OpenAIProvider


class LLMProviderFactory:
    """
    Factory for creating and managing LLM providers.
    
    Handles provider selection based on configuration,
    validates providers, and manages fallback logic.
    """
    
    # Registry of available providers
    PROVIDERS = {
        "anthropic": AnthropicProvider,
        "openai": OpenAIProvider
    }
    
    def __init__(self, llm_config: Dict[str, Any]):
        """
        Initialize the factory with LLM configuration.
        
        Args:
            llm_config: Complete LLM configuration from config file
        """
        self.llm_config = llm_config
        self.default_provider = llm_config.get("default_provider", "anthropic")
        self.providers_config = llm_config.get("providers", {})
        self._provider_instances = {}  # Cache for provider instances
    
    def get_provider(self, provider_name: Optional[str] = None) -> LLMProvider:
        """
        Get a provider instance.
        
        Args:
            provider_name: Specific provider to use, or None for default
        
        Returns:
            Configured LLMProvider instance
        
        Raises:
            ValueError: If provider is not available or not configured
        """
        # Use default provider if none specified
        if provider_name is None:
            provider_name = self.default_provider
        
        # Check if provider is supported
        if provider_name not in self.PROVIDERS:
            available = list(self.PROVIDERS.keys())
            raise ValueError(f"Unknown provider '{provider_name}'. Available: {available}")
        
        # Check if provider is configured
        if provider_name not in self.providers_config:
            raise ValueError(f"Provider '{provider_name}' is not configured in config.json")
        
        # Return cached instance if available
        if provider_name in self._provider_instances:
            return self._provider_instances[provider_name]
        
        # Create new provider instance
        provider_config = self.providers_config[provider_name]
        
        # Create LLMConfig object
        config = LLMConfig(
            api_key=provider_config.get("api_key", ""),
            model=provider_config.get("model", ""),
            max_tokens=provider_config.get("max_tokens", 4000),
            temperature=provider_config.get("temperature", 0.1),
            max_retries=provider_config.get("max_retries", 3),
            retry_delay=provider_config.get("retry_delay", 1.0)
        )
        
        # Validate configuration
        provider_class = self.PROVIDERS[provider_name]
        temp_instance = provider_class(config)
        is_valid, errors = temp_instance.validate_config()
        
        if not is_valid:
            error_msg = f"Invalid configuration for {provider_name}: {'; '.join(errors)}"
            raise ValueError(error_msg)
        
        # Cache and return the instance
        self._provider_instances[provider_name] = temp_instance
        return temp_instance
    
    def get_available_providers(self) -> List[str]:
        """
        Get list of available and configured providers.
        
        Returns:
            List of provider names that are both supported and configured
        """
        available = []
        
        for provider_name in self.PROVIDERS.keys():
            if provider_name in self.providers_config:
                try:
                    # Test if the provider can be created (basic validation)
                    provider_config = self.providers_config[provider_name]
                    if provider_config.get("api_key") and provider_config.get("model"):
                        available.append(provider_name)
                except Exception:
                    # Skip providers that can't be configured
                    continue
        
        return available
    
    def test_provider(self, provider_name: str) -> tuple[bool, str]:
        """
        Test if a provider is working correctly.
        
        Args:
            provider_name: Name of provider to test
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            provider = self.get_provider(provider_name)
            return provider.test_connection()
        except Exception as e:
            return False, f"Provider setup failed: {str(e)}"
    
    def test_all_providers(self) -> Dict[str, tuple[bool, str]]:
        """
        Test all available providers.
        
        Returns:
            Dictionary mapping provider names to (success, message) tuples
        """
        results = {}
        
        for provider_name in self.get_available_providers():
            results[provider_name] = self.test_provider(provider_name)
        
        return results
    
    def get_provider_with_fallback(self, preferred_provider: Optional[str] = None) -> LLMProvider:
        """
        Get a provider with automatic fallback to alternatives if the preferred one fails.
        
        Args:
            preferred_provider: Preferred provider name, or None for default
        
        Returns:
            Working LLMProvider instance
        
        Raises:
            RuntimeError: If no providers are working
        """
        # Try preferred provider first
        if preferred_provider:
            try:
                provider = self.get_provider(preferred_provider)
                success, message = provider.test_connection()
                if success:
                    return provider
            except Exception:
                pass
        
        # Try default provider
        if preferred_provider != self.default_provider:
            try:
                provider = self.get_provider(self.default_provider)
                success, message = provider.test_connection()
                if success:
                    return provider
            except Exception:
                pass
        
        # Try all available providers as fallback
        for provider_name in self.get_available_providers():
            if provider_name in [preferred_provider, self.default_provider]:
                continue  # Already tried these
            
            try:
                provider = self.get_provider(provider_name)
                success, message = provider.test_connection()
                if success:
                    return provider
            except Exception:
                continue
        
        # No working providers found
        raise RuntimeError("No working LLM providers available. Please check your configuration and API keys.")
    
    def get_usage_summary(self) -> Dict[str, Any]:
        """
        Get usage summary for all provider instances.
        
        Returns:
            Dictionary with usage statistics for each provider
        """
        summary = {}
        
        for provider_name, provider in self._provider_instances.items():
            summary[provider_name] = provider.get_usage_stats()
        
        return summary
    
    def validate_configuration(self) -> tuple[bool, List[str]]:
        """
        Validate the complete LLM configuration.
        
        Returns:
            Tuple of (is_valid: bool, error_messages: List[str])
        """
        errors = []
        
        # Check if default provider is valid
        if self.default_provider not in self.PROVIDERS:
            available = list(self.PROVIDERS.keys())
            errors.append(f"Invalid default_provider '{self.default_provider}'. Available: {available}")
        
        # Check if any providers are configured
        if not self.providers_config:
            errors.append("No LLM providers configured")
        
        # Validate each configured provider
        for provider_name, provider_config in self.providers_config.items():
            if provider_name not in self.PROVIDERS:
                errors.append(f"Unknown provider '{provider_name}' in configuration")
                continue
            
            # Check required fields
            required_fields = ["api_key", "model"]
            for field in required_fields:
                if not provider_config.get(field):
                    errors.append(f"Missing required field '{field}' for provider '{provider_name}'")
            
            # Validate provider-specific configuration
            try:
                config = LLMConfig(
                    api_key=provider_config.get("api_key", ""),
                    model=provider_config.get("model", ""),
                    max_tokens=provider_config.get("max_tokens", 4000),
                    temperature=provider_config.get("temperature", 0.1)
                )
                
                provider_class = self.PROVIDERS[provider_name]
                temp_instance = provider_class(config)
                is_valid, provider_errors = temp_instance.validate_config()
                
                if not is_valid:
                    for error in provider_errors:
                        errors.append(f"Provider '{provider_name}': {error}")
                        
            except Exception as e:
                errors.append(f"Provider '{provider_name}' configuration error: {str(e)}")
        
        return len(errors) == 0, errors