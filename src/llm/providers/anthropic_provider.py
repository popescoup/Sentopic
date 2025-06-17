"""
Anthropic Claude Provider

Implementation of the LLMProvider interface for Anthropic's Claude models.
Handles Claude-specific API format, authentication, and error handling.
"""

from typing import Dict, List, Any
import anthropic
from .base import LLMProvider, LLMResponse, LLMConfig


class AnthropicProvider(LLMProvider):
    """
    Anthropic Claude provider implementation.
    
    Supports Claude 3 models (Sonnet, Opus, Haiku) with proper
    message formatting and error handling.
    """
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
    
    def _initialize_client(self):
        """Initialize the Anthropic client."""
        try:
            self.client = anthropic.Anthropic(api_key=self.config.api_key)
        except Exception as e:
            raise Exception(f"Failed to initialize Anthropic client: {e}")
    
    def _make_request(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        """
        Make request to Anthropic Claude API.
        
        Args:
            messages: Conversation messages
            **kwargs: Additional parameters (temperature, etc.)
        
        Returns:
            LLMResponse with Claude's response
        """
        # Anthropic uses a different message format - extract system message if present
        system_message = None
        user_messages = []
        
        for message in messages:
            if message["role"] == "system":
                system_message = message["content"]
            else:
                user_messages.append(message)
        
        # Prepare request parameters
        request_params = {
            "model": self.config.model,
            "max_tokens": self.config.max_tokens,
            "temperature": kwargs.get("temperature", self.config.temperature),
            "messages": user_messages
        }
        
        # Add system message if present
        if system_message:
            request_params["system"] = system_message
        
        try:
            # Make the API call
            response = self.client.messages.create(**request_params)
            
            # Extract content from response
            content = ""
            if response.content and len(response.content) > 0:
                # Claude returns content as a list of content blocks
                content = "".join([block.text for block in response.content if hasattr(block, 'text')])
            
            # Calculate cost estimate
            tokens_used = response.usage.input_tokens + response.usage.output_tokens
            cost_estimate = self._calculate_cost(tokens_used, self.config.model)
            
            return LLMResponse(
                content=content,
                tokens_used=tokens_used,
                model=self.config.model,
                provider=self.get_provider_name(),
                cost_estimate=cost_estimate
            )
            
        except anthropic.AuthenticationError as e:
            raise Exception(f"Anthropic authentication failed: {e}")
        except anthropic.RateLimitError as e:
            raise Exception(f"Anthropic rate limit exceeded: {e}")
        except anthropic.APIError as e:
            raise Exception(f"Anthropic API error: {e}")
        except Exception as e:
            raise Exception(f"Unexpected error calling Anthropic API: {e}")
    
    def _calculate_cost(self, tokens_used: int, model: str) -> float:
        """
        Calculate estimated cost for Anthropic API usage.
        
        Args:
            tokens_used: Total tokens (input + output)
            model: Model name
        
        Returns:
            Estimated cost in USD
        """
        # Anthropic pricing (as of 2024) - simplified estimation
        # In practice, input and output tokens have different costs
        costs_per_token = {
            "claude-3-opus-20240229": 0.000075,      # $75 per 1M tokens (mixed)
            "claude-3-sonnet-20240229": 0.000015,    # $15 per 1M tokens (mixed)
            "claude-3-haiku-20240307": 0.000001,     # $1 per 1M tokens (mixed)
            "claude-3.5-sonnet": 0.000015,           # $15 per 1M tokens (mixed)
        }
        
        # Default cost if model not found
        cost_per_token = costs_per_token.get(model, 0.000015)
        
        return tokens_used * cost_per_token
    
    def get_provider_name(self) -> str:
        """Return the provider name."""
        return "anthropic"
    
    def count_tokens(self, text: str) -> int:
        """
        Estimate token count for Claude models.
        
        Claude doesn't provide a public tokenizer, so we use approximation.
        
        Args:
            text: Text to count tokens for
        
        Returns:
            Estimated token count
        """
        # Claude typically uses ~3.5 characters per token
        return int(len(text) / 3.5)
    
    def validate_config(self) -> tuple[bool, List[str]]:
        """
        Validate Anthropic-specific configuration.
        
        Returns:
            Tuple of (is_valid: bool, error_messages: List[str])
        """
        is_valid, errors = super().validate_config()
        
        # Validate Claude-specific model names
        valid_models = [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229", 
            "claude-3-haiku-20240307",
            "claude-3.5-sonnet",
            "claude-3-5-sonnet-20240620"
        ]
        
        if self.config.model not in valid_models:
            errors.append(f"Invalid Claude model: {self.config.model}. Valid models: {valid_models}")
        
        # Claude has specific max_tokens limits
        model_limits = {
            "claude-3-opus-20240229": 4096,
            "claude-3-sonnet-20240229": 4096,
            "claude-3-haiku-20240307": 4096,
            "claude-3.5-sonnet": 8192,
            "claude-3-5-sonnet-20240620": 8192
        }
        
        max_allowed = model_limits.get(self.config.model, 4096)
        if self.config.max_tokens > max_allowed:
            errors.append(f"max_tokens ({self.config.max_tokens}) exceeds limit for {self.config.model}: {max_allowed}")
        
        return len(errors) == 0, errors