"""
OpenAI Provider

Implementation of the LLMProvider interface for OpenAI's GPT models.
Handles OpenAI-specific API format, authentication, and error handling.
"""

from typing import Dict, List, Any
import openai
from .base import LLMProvider, LLMResponse, LLMConfig


class OpenAIProvider(LLMProvider):
    """
    OpenAI GPT provider implementation.
    
    Supports GPT-4, GPT-3.5, and other OpenAI models with proper
    message formatting and error handling.
    """
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
    
    def _initialize_client(self):
        """Initialize the OpenAI client."""
        try:
            self.client = openai.OpenAI(api_key=self.config.api_key)
        except Exception as e:
            raise Exception(f"Failed to initialize OpenAI client: {e}")
    
    def _make_request(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        """
        Make request to OpenAI API.
        
        Args:
            messages: Conversation messages in OpenAI format
            **kwargs: Additional parameters (temperature, etc.)
        
        Returns:
            LLMResponse with GPT's response
        """
        # Prepare request parameters
        request_params = {
            "model": self.config.model,
            "messages": messages,
            "max_tokens": self.config.max_tokens,
            "temperature": kwargs.get("temperature", self.config.temperature)
        }
        
        try:
            # Make the API call
            response = self.client.chat.completions.create(**request_params)
            
            # Extract content from response
            content = ""
            if response.choices and len(response.choices) > 0:
                content = response.choices[0].message.content or ""
            
            # Get token usage
            tokens_used = 0
            if response.usage:
                tokens_used = response.usage.total_tokens
            
            # Calculate cost estimate
            cost_estimate = self._calculate_cost(tokens_used, self.config.model)
            
            return LLMResponse(
                content=content,
                tokens_used=tokens_used,
                model=self.config.model,
                provider=self.get_provider_name(),
                cost_estimate=cost_estimate
            )
            
        except openai.AuthenticationError as e:
            raise Exception(f"OpenAI authentication failed: {e}")
        except openai.RateLimitError as e:
            raise Exception(f"OpenAI rate limit exceeded: {e}")
        except openai.APIError as e:
            raise Exception(f"OpenAI API error: {e}")
        except Exception as e:
            raise Exception(f"Unexpected error calling OpenAI API: {e}")
    
    def _calculate_cost(self, tokens_used: int, model: str) -> float:
        """
        Calculate estimated cost for OpenAI API usage.
        
        Args:
            tokens_used: Total tokens (input + output)
            model: Model name
        
        Returns:
            Estimated cost in USD
        """
        # OpenAI pricing (as of 2024) - simplified estimation
        # In practice, input and output tokens have different costs
        costs_per_token = {
            "gpt-4": 0.00006,                    # $60 per 1M tokens (mixed)
            "gpt-4-turbo": 0.00003,              # $30 per 1M tokens (mixed)
            "gpt-4-turbo-preview": 0.00003,      # $30 per 1M tokens (mixed)
            "gpt-4o": 0.000025,                  # $25 per 1M tokens (mixed)
            "gpt-4o-mini": 0.000015,             # $15 per 1M tokens (mixed)
            "gpt-3.5-turbo": 0.000002,           # $2 per 1M tokens (mixed)
            "gpt-3.5-turbo-16k": 0.000004,       # $4 per 1M tokens (mixed)
        }
        
        # Default cost if model not found
        cost_per_token = costs_per_token.get(model, 0.00003)
        
        return tokens_used * cost_per_token
    
    def get_provider_name(self) -> str:
        """Return the provider name."""
        return "openai"
    
    def count_tokens(self, text: str) -> int:
        """
        Estimate token count for OpenAI models.
        
        OpenAI provides tiktoken for accurate counting, but for simplicity
        we use approximation here. Can be enhanced later with tiktoken.
        
        Args:
            text: Text to count tokens for
        
        Returns:
            Estimated token count
        """
        # OpenAI typically uses ~4 characters per token
        return int(len(text) / 4)
    
    def validate_config(self) -> tuple[bool, List[str]]:
        """
        Validate OpenAI-specific configuration.
        
        Returns:
            Tuple of (is_valid: bool, error_messages: List[str])
        """
        is_valid, errors = super().validate_config()
        
        # Validate OpenAI-specific model names
        valid_models = [
            "gpt-4",
            "gpt-4-turbo",
            "gpt-4-turbo-preview",
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-16k",
            "gpt-3.5-turbo-1106",
            "gpt-4-1106-preview"
        ]
        
        if self.config.model not in valid_models:
            errors.append(f"Invalid OpenAI model: {self.config.model}. Valid models: {valid_models}")
        
        # OpenAI has specific max_tokens limits
        model_limits = {
            "gpt-4": 8192,
            "gpt-4-turbo": 4096,
            "gpt-4-turbo-preview": 4096,
            "gpt-4o": 4096,
            "gpt-4o-mini": 16384,
            "gpt-3.5-turbo": 4096,
            "gpt-3.5-turbo-16k": 16384,
            "gpt-3.5-turbo-1106": 4096,
            "gpt-4-1106-preview": 4096
        }
        
        max_allowed = model_limits.get(self.config.model, 4096)
        if self.config.max_tokens > max_allowed:
            errors.append(f"max_tokens ({self.config.max_tokens}) exceeds limit for {self.config.model}: {max_allowed}")
        
        return len(errors) == 0, errors