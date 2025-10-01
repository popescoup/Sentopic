import json
import os
import shutil
from typing import Dict, Any, Tuple, List
from datetime import datetime


class Config:
    def __init__(self, config_path: str = "config.json", config_dir: str = None):
        """
        Initialize configuration.
        
        Args:
            config_path: Name of the config file (default: "config.json")
            config_dir: Directory containing config file (default: current directory)
        """
        self.config_dir = config_dir or os.getcwd()
        self.config_path = os.path.join(self.config_dir, config_path)
        self.example_config_path = os.path.join(self.config_dir, "config.example.json")
        self._config = None
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file, creating from example if needed."""
        if self._config is None:
            # Check if config exists, if not create from example
            if not os.path.exists(self.config_path):
                print(f"⚠️  Config file not found at: {self.config_path}")
                print(f"📝 Creating from example: {self.example_config_path}")
                
                success, error = self._create_config_from_example()
                if not success:
                    raise FileNotFoundError(
                        f"Configuration file '{self.config_path}' not found and could not be created. "
                        f"Error: {error}"
                    )
                print(f"✅ Created config file at: {self.config_path}")
            
            with open(self.config_path, 'r') as f:
                self._config = json.load(f)
        
        return self._config
    
    def _create_config_from_example(self) -> Tuple[bool, str]:
        """
        Create config.json from config.example.json.
        
        Returns:
            Tuple of (success: bool, error_message: str)
        """
        try:
            # Check if example config exists
            if not os.path.exists(self.example_config_path):
                return False, f"Example config not found at: {self.example_config_path}"
            
            # Ensure config directory exists
            os.makedirs(self.config_dir, exist_ok=True)
            
            # Copy example to actual config
            shutil.copy2(self.example_config_path, self.config_path)
            
            return True, ""
            
        except Exception as e:
            return False, f"Failed to create config from example: {str(e)}"
    
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
    
    # ============================================================================
    # NEW METHODS FOR CONFIGURATION MANAGEMENT
    # ============================================================================
    
    def update_reddit_config(self, reddit_config: Dict[str, str]) -> Tuple[bool, List[str]]:
        """
        Update Reddit API configuration.
        
        Args:
            reddit_config: Dictionary with client_id, client_secret, user_agent
            
        Returns:
            Tuple of (success: bool, error_messages: List[str])
        """
        errors = []
        
        # Validate required fields
        required_fields = ['client_id', 'client_secret', 'user_agent']
        for field in required_fields:
            if not reddit_config.get(field) or not reddit_config[field].strip():
                errors.append(f"Missing or empty required field: {field}")
        
        if errors:
            return False, errors
        
        try:
            # Load current config
            current_config = self.load_config()
            
            # Update Reddit section
            current_config['reddit'] = {
                'client_id': reddit_config['client_id'].strip(),
                'client_secret': reddit_config['client_secret'].strip(), 
                'user_agent': reddit_config['user_agent'].strip()
            }
            
            # Save to file
            success, save_errors = self._save_config(current_config)
            if not success:
                return False, save_errors
            
            # Reload cached config
            self.reload_config()
            
            return True, []
            
        except Exception as e:
            return False, [f"Failed to update Reddit configuration: {str(e)}"]
    
    def update_llm_config(self, llm_config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Update LLM configuration.
        
        Args:
            llm_config: Dictionary with LLM configuration
            
        Returns:
            Tuple of (success: bool, error_messages: List[str])
        """
        errors = []
        
        try:
            # Validate the LLM config structure
            if not isinstance(llm_config, dict):
                return False, ["LLM configuration must be an object"]
            
            # Validate enabled field
            enabled = llm_config.get('enabled', False)
            if not isinstance(enabled, bool):
                errors.append("'enabled' field must be a boolean")
            
            if enabled:
                # Validate providers if LLM is enabled
                providers = llm_config.get('providers', {})
                if not isinstance(providers, dict) or not providers:
                    errors.append("'providers' must be a non-empty object when LLM is enabled")
                
                # Validate default provider
                default_provider = llm_config.get('default_provider')
                if not default_provider:
                    errors.append("'default_provider' is required when LLM is enabled")
                elif default_provider not in providers:
                    errors.append(f"Default provider '{default_provider}' must be configured in providers")
                
                # Validate each provider
                for provider_name, provider_config in providers.items():
                    if not isinstance(provider_config, dict):
                        errors.append(f"Provider '{provider_name}' configuration must be an object")
                        continue
                    
                    # Check API key
                    api_key = provider_config.get('api_key')
                    if not api_key or not api_key.strip():
                        errors.append(f"Provider '{provider_name}' requires a valid API key")
                    
                    # Check model
                    model = provider_config.get('model')
                    if not model or not model.strip():
                        errors.append(f"Provider '{provider_name}' requires a model specification")
            
            if errors:
                return False, errors
            
            # Load current config
            current_config = self.load_config()
            
            # Update LLM section
            current_config['llm'] = llm_config
            
            # Save to file
            success, save_errors = self._save_config(current_config)
            if not success:
                return False, save_errors
            
            # Reload cached config and LLM config
            self.reload_config()
            
            # Reload LLM config as well
            try:
                from src.llm.config import llm_config as llm_config_instance
                llm_config_instance.reload_config()
            except ImportError:
                # LLM module might not be available
                pass
            
            return True, []
            
        except Exception as e:
            return False, [f"Failed to update LLM configuration: {str(e)}"]
    
    def test_reddit_connection(self) -> Tuple[bool, str]:
        """
        Test Reddit API connection with current configuration.
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            print("=" * 60)
            print("DEBUG: test_reddit_connection called")
            print(f"  config.config_dir: {self.config_dir}")
            print(f"  config.config_path: {self.config_path}")
            print(f"  config file exists: {os.path.exists(self.config_path)}")
            print("=" * 60)
            
            reddit_config = self.get_reddit_config()
            
            print("DEBUG: Reddit config loaded")
            print(f"  client_id present: {bool(reddit_config.get('client_id'))}")
            print(f"  client_id length: {len(reddit_config.get('client_id', ''))}")
            print(f"  client_id value: {reddit_config.get('client_id', '')[:10]}...")
            print(f"  client_secret present: {bool(reddit_config.get('client_secret'))}")
            print(f"  client_secret length: {len(reddit_config.get('client_secret', ''))}")
            print(f"  user_agent present: {bool(reddit_config.get('user_agent'))}")
            print(f"  user_agent value: {reddit_config.get('user_agent', '')}")
            print("=" * 60)
            
            # Import here to avoid circular imports
            from src.reddit_client import get_reddit_client, reset_reddit_client
            
            print("DEBUG: Resetting Reddit client...")
            # Reset the global client to force reinitialization with current config
            reset_reddit_client()
            
            print("DEBUG: Getting Reddit client instance...")
            # Get the global client instance (will be initialized with current config)
            reddit_client = get_reddit_client()
            
            print("DEBUG: Testing connection...")
            result = reddit_client.test_connection()
            print(f"DEBUG: Connection test result: {result}")
            print("=" * 60)
            
            return result
            
        except ValueError as e:
            print(f"DEBUG: ValueError in test_reddit_connection: {e}")
            print("=" * 60)
            return False, str(e)
        except Exception as e:
            print(f"DEBUG: Exception in test_reddit_connection: {e}")
            import traceback
            print(f"DEBUG: Traceback:\n{traceback.format_exc()}")
            print("=" * 60)
            return False, f"Reddit connection test failed: {str(e)}"
    
    def test_llm_providers(self) -> Dict[str, Tuple[bool, str]]:
        """
        Test all configured LLM providers.
        
        Returns:
            Dictionary mapping provider names to (success, message) tuples
        """
        if not self.is_llm_enabled():
            return {}
        
        try:
            from src.llm.config import llm_config
            return llm_config.test_providers()
        except Exception as e:
            return {"error": (False, f"Failed to test LLM providers: {str(e)}")}
    
    def get_configuration_status(self) -> Dict[str, Any]:
        """
        Get comprehensive configuration status.
        
        Returns:
            Dictionary with configuration status for all components
        """
        status = {
            "timestamp": datetime.utcnow().isoformat(),
            "reddit": {"configured": False, "connected": False, "error": None},
            "llm": {"enabled": False, "providers": {}, "features": {}, "error": None}
        }
        
        # Test Reddit configuration
        try:
            reddit_config = self.get_reddit_config()
            status["reddit"]["configured"] = True
            status["reddit"]["current_config"] = {
                "client_id": reddit_config.get("client_id", ""),
                "client_secret": reddit_config.get("client_secret", ""),
                "user_agent": reddit_config.get("user_agent", "")
            }
            
            # Test connection
            reddit_success, reddit_message = self.test_reddit_connection()
            status["reddit"]["connected"] = reddit_success
            if not reddit_success:
                status["reddit"]["error"] = reddit_message
                
        except Exception as e:
            status["reddit"]["error"] = str(e)
        
        # Test LLM configuration
        try:
            if self.is_llm_enabled():
                status["llm"]["enabled"] = True
                
                # Get current LLM configuration
                llm_config_data = self.get_llm_config()
                status["llm"]["current_config"] = {
                    "default_provider": llm_config_data.get("default_provider", "anthropic"),
                    "providers": {}
                }
                
                # Include provider configurations (with API keys for local use)
                providers = llm_config_data.get("providers", {})
                for provider_name, provider_config in providers.items():
                    status["llm"]["current_config"]["providers"][provider_name] = {
                        "api_key": provider_config.get("api_key", ""),
                        "model": provider_config.get("model", ""),
                        "max_tokens": provider_config.get("max_tokens", 4000),
                        "temperature": provider_config.get("temperature", 0.1)
                    }
                
                # Get provider test results
                provider_tests = self.test_llm_providers()
                for provider_name, (success, message) in provider_tests.items():
                    status["llm"]["providers"][provider_name] = {
                        "configured": True,  # If it's being tested, it's configured
                        "connected": success,
                        "error": message if not success else None
                    }
                
                # Get feature configuration
                from src.llm.config import llm_config
                status["llm"]["features"] = llm_config.get_feature_config()
                
        except Exception as e:
            status["llm"]["error"] = str(e)
        
        return status
    
    def clear_all_data(self) -> Tuple[bool, str]:
        """
        Clear all application data (projects, collections, chat history).
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            from src.database import db
            from src.analytics import analytics_engine
            
            # Get all analysis sessions
            analysis_sessions = db.get_analysis_sessions()
            
            # Delete each analysis session (this now cascades to chat sessions automatically)
            for session in analysis_sessions:
                analytics_engine.delete_session(session.id)
            
            # Get all collections
            collections = db.get_collections()
            
            # Delete each collection (this now cascades to posts, comments, and embeddings automatically)
            session = db.get_session()
            try:
                for collection in collections:
                    session.delete(collection)
                session.commit()
            finally:
                session.close()
            
            return True, f"Successfully cleared all data: {len(analysis_sessions)} projects and {len(collections)} collections deleted (with full cascade deletion)"
            
        except Exception as e:
            return False, f"Failed to clear data: {str(e)}"
    
    def reset_configuration(self) -> Tuple[bool, str]:
        try:
            # Load example config structure
            example_path = "config.example.json"
            if not os.path.exists(example_path):
                return False, "config.example.json not found - cannot reset to defaults"
            
            with open(example_path, 'r') as f:
                default_config = json.load(f)
            
            # Save default config
            success, errors = self._save_config(default_config)
            if not success:
                return False, f"Failed to save default configuration: {', '.join(errors)}"
            
            # Reload configs
            self.reload_config()
            try:
                from src.llm.config import llm_config
                llm_config.reload_config()
            except ImportError:
                pass
            
            return True, "Configuration reset to defaults successfully"
            
        except Exception as e:
            return False, f"Failed to reset configuration: {str(e)}"
    
    def _save_config(self, config_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        try:
            # Ensure config directory exists
            os.makedirs(self.config_dir, exist_ok=True)
            
            # Write new config with proper formatting
            with open(self.config_path, 'w') as f:
                json.dump(config_data, f, indent=4, sort_keys=False)
            
            # Verify the file was written correctly by loading it
            with open(self.config_path, 'r') as f:
                loaded_config = json.load(f)
            
            return True, []
            
        except Exception as e:
            return False, [f"Failed to save configuration: {str(e)}"]


# Global config instance
# The config_dir will be set by the application entry point (run_api.py)
# In development mode, it defaults to current directory
# In packaged mode, it will be set to the user data directory
config = Config()