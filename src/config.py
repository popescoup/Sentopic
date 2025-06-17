import json
import os
from typing import Dict, Any


class Config:
    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self._config = None
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        if self._config is None:
            if not os.path.exists(self.config_path):
                raise FileNotFoundError(
                    f"Configuration file '{self.config_path}' not found. "
                    "Please create it with your Reddit API credentials."
                )
            
            with open(self.config_path, 'r') as f:
                self._config = json.load(f)
        
        return self._config
    
    def get_reddit_config(self) -> Dict[str, str]:
        """Get Reddit API configuration."""
        config = self.load_config()
        reddit_config = config.get('reddit', {})
        
        required_fields = ['client_id', 'client_secret', 'user_agent']
        for field in required_fields:
            if not reddit_config.get(field):
                raise ValueError(f"Missing required Reddit configuration field: {field}")
        
        return reddit_config
    
    def get_llm_config(self) -> Dict[str, Any]:
        """
        Get LLM configuration.
        
        Returns:
            LLM configuration dictionary, empty if not configured
        """
        config = self.load_config()
        return config.get('llm', {})
    
    def is_llm_enabled(self) -> bool:
        """
        Check if LLM features are enabled in configuration.
        
        Returns:
            True if LLM features should be available
        """
        llm_config = self.get_llm_config()
        return llm_config.get('enabled', False)
    
    def validate_llm_config(self) -> tuple[bool, list[str]]:
        """
        Validate LLM configuration.
        
        Returns:
            Tuple of (is_valid: bool, error_messages: List[str])
        """
        errors = []
        
        if not self.is_llm_enabled():
            return True, []  # Valid to have LLM disabled
        
        llm_config = self.get_llm_config()
        
        # Check default provider
        default_provider = llm_config.get('default_provider')
        if not default_provider:
            errors.append("Missing default_provider in LLM configuration")
        
        # Check providers configuration
        providers = llm_config.get('providers', {})
        if not providers:
            errors.append("No LLM providers configured")
        
        # Validate each provider
        for provider_name, provider_config in providers.items():
            if not isinstance(provider_config, dict):
                errors.append(f"Provider '{provider_name}' configuration must be an object")
                continue
            
            # Check required fields
            required_fields = ['api_key', 'model']
            for field in required_fields:
                if not provider_config.get(field):
                    errors.append(f"Missing required field '{field}' for provider '{provider_name}'")
        
        # Check if default provider is configured
        if default_provider and default_provider not in providers:
            errors.append(f"Default provider '{default_provider}' is not configured in providers")
        
        return len(errors) == 0, errors
    
    def reload_config(self):
        """Force reload of configuration from file."""
        self._config = None


# Global config instance
config = Config()