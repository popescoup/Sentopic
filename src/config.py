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


# Global config instance
config = Config()