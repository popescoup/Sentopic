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
    
    Supports Claude 3 and Claude 4 models (Sonnet, Opus, Haiku) with proper
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
            
            # Calculate cost estimate with separate input/output token pricing
            tokens_used = response.usage.input_tokens + response.usage.output_tokens
            cost_estimate = self._calculate_cost(
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
                model=self.config.model
            )
            
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
    
    def _calculate_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
        """
        Calculate estimated cost for Anthropic API usage.
        
        Uses official Anthropic pricing with separate input/output token costs.
        Prices are per million tokens.
        
        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            model: Model name
        
        Returns:
            Estimated cost in USD
        """
        # Anthropic pricing (official rates as of December 2024)
        # Format: (input_cost_per_1M, output_cost_per_1M)
        pricing = {
            # Claude 3 models (legacy - deprecated/retired)
            "claude-3-opus-20240229": (15.00, 75.00),
            "claude-3-sonnet-20240229": (3.00, 15.00),
            "claude-3-haiku-20240307": (0.25, 1.25),
            "claude-3.5-sonnet": (3.00, 15.00),
            "claude-3-5-sonnet-20240620": (3.00, 15.00),
            "claude-3-5-sonnet-20241022": (3.00, 15.00),
            
            # Claude 4 models (current)
            "claude-sonnet-4-20250514": (3.00, 15.00),
            "claude-sonnet-4-5-20250929": (3.00, 15.00),
            "claude-haiku-4-5-20251001": (0.80, 4.00),
        }
        
        # Default to Claude Sonnet pricing if model not found
        input_cost_per_1m, output_cost_per_1m = pricing.get(model, (3.00, 15.00))
        
        # Calculate cost
        input_cost = (input_tokens / 1_000_000) * input_cost_per_1m
        output_cost = (output_tokens / 1_000_000) * output_cost_per_1m
        
        return input_cost + output_cost
    
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
        
        # Basic validation - let the Anthropic SDK handle model name validation
        # This prevents hardcoding models that may become outdated
        if not self.config.model or not isinstance(self.config.model, str):
            errors.append("Model name must be a non-empty string")
        
        # Validate max_tokens against official model limits (output generation limits)
        # These are the maximum OUTPUT tokens the model can generate
        model_output_limits = {
            # Claude 3 models
            "claude-3-opus-20240229": 4096,
            "claude-3-sonnet-20240229": 4096,
            "claude-3-haiku-20240307": 4096,
            "claude-3.5-sonnet": 8192,
            "claude-3-5-sonnet-20240620": 8192,
            "claude-3-5-sonnet-20241022": 8192,
            
            # Claude 4 models
            "claude-sonnet-4-20250514": 8192,
            "claude-sonnet-4-5-20250929": 8192,
            "claude-haiku-4-5-20251001": 8192,
        }
        
        # Get the limit for this model, default to conservative 4096 for unknown models
        max_allowed = model_output_limits.get(self.config.model, 4096)
        
        if self.config.max_tokens > max_allowed:
            errors.append(
                f"max_tokens ({self.config.max_tokens}) exceeds output limit for {self.config.model}: {max_allowed}. "
                f"Note: This is the output generation limit, not the context window limit."
            )
        
        return len(errors) == 0, errors