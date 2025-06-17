"""
Base LLM Provider Interface

Abstract base class that defines the common interface all LLM providers must implement.
This ensures consistent behavior across different AI services (Anthropic, OpenAI, etc.).
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import time


@dataclass
class LLMResponse:
    """Standard response format for all LLM providers."""
    content: str
    tokens_used: int
    model: str
    provider: str
    cost_estimate: float = 0.0
    latency_ms: int = 0


@dataclass
class LLMConfig:
    """Configuration for LLM providers."""
    api_key: str
    model: str
    max_tokens: int = 4000
    temperature: float = 0.1
    max_retries: int = 3
    retry_delay: float = 1.0


class LLMProvider(ABC):
    """
    Abstract base class for all LLM providers.
    
    Each provider (Anthropic, OpenAI) must implement these methods
    to ensure consistent behavior across the application.
    """
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.client = None
        self._total_tokens_used = 0
        self._total_cost = 0.0
        self._initialize_client()
    
    @abstractmethod
    def _initialize_client(self):
        """Initialize the provider-specific client."""
        pass
    
    @abstractmethod
    def _make_request(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        """Make the actual API request to the provider."""
        pass
    
    @abstractmethod
    def _calculate_cost(self, tokens_used: int, model: str) -> float:
        """Calculate the estimated cost for the API call."""
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Return the name of this provider."""
        pass
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> LLMResponse:
        """
        Generate text using this LLM provider.
        
        Args:
            prompt: The user prompt/question
            system_prompt: Optional system context/instructions
            **kwargs: Additional provider-specific parameters
        
        Returns:
            LLMResponse with generated content and metadata
        """
        # Prepare messages in a common format
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        # Make request with retry logic
        return self._make_request_with_retry(messages, **kwargs)
    
    def generate_with_conversation(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        """
        Generate text with full conversation context.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            **kwargs: Additional provider-specific parameters
        
        Returns:
            LLMResponse with generated content and metadata
        """
        return self._make_request_with_retry(messages, **kwargs)
    
    def _make_request_with_retry(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        """
        Make request with retry logic for handling rate limits and transient errors.
        
        Args:
            messages: Conversation messages
            **kwargs: Additional parameters
        
        Returns:
            LLMResponse from successful request
        
        Raises:
            Exception: After all retries are exhausted
        """
        last_exception = None
        
        for attempt in range(self.config.max_retries + 1):
            try:
                start_time = time.time()
                response = self._make_request(messages, **kwargs)
                end_time = time.time()
                
                # Add latency information
                response.latency_ms = int((end_time - start_time) * 1000)
                
                # Track usage statistics
                self._total_tokens_used += response.tokens_used
                self._total_cost += response.cost_estimate
                
                return response
                
            except Exception as e:
                last_exception = e
                
                # Don't retry on authentication errors
                if "authentication" in str(e).lower() or "api_key" in str(e).lower():
                    raise e
                
                # Wait before retrying (exponential backoff)
                if attempt < self.config.max_retries:
                    wait_time = self.config.retry_delay * (2 ** attempt)
                    time.sleep(wait_time)
        
        # All retries exhausted
        raise Exception(f"LLM request failed after {self.config.max_retries + 1} attempts. Last error: {last_exception}")
    
    def test_connection(self) -> Tuple[bool, str]:
        """
        Test if the provider connection is working.
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            response = self.generate("Test", system_prompt="Respond with 'OK'")
            return True, f"Connection successful. Model: {response.model}"
        except Exception as e:
            return False, f"Connection failed: {str(e)}"
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """
        Get usage statistics for this provider session.
        
        Returns:
            Dictionary with usage statistics
        """
        return {
            "provider": self.get_provider_name(),
            "total_tokens_used": self._total_tokens_used,
            "total_cost_estimate": self._total_cost,
            "model": self.config.model
        }
    
    def count_tokens(self, text: str) -> int:
        """
        Estimate token count for text. Default implementation uses rough approximation.
        Providers can override with more accurate tokenization.
        
        Args:
            text: Text to count tokens for
        
        Returns:
            Estimated token count
        """
        # Rough approximation: ~4 characters per token for most models
        return len(text) // 4
    
    def validate_config(self) -> Tuple[bool, List[str]]:
        """
        Validate the provider configuration.
        
        Returns:
            Tuple of (is_valid: bool, error_messages: List[str])
        """
        errors = []
        
        if not self.config.api_key or len(self.config.api_key.strip()) == 0:
            errors.append("API key is required")
        
        if not self.config.model or len(self.config.model.strip()) == 0:
            errors.append("Model name is required")
        
        if self.config.max_tokens <= 0:
            errors.append("max_tokens must be greater than 0")
        
        if not (0.0 <= self.config.temperature <= 2.0):
            errors.append("temperature must be between 0.0 and 2.0")
        
        return len(errors) == 0, errors