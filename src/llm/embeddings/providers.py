"""
Embeddings Providers

Handles generation of vector embeddings for semantic search.
Supports both cloud providers (OpenAI) and local models (sentence-transformers).
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import numpy as np
from dataclasses import dataclass


@dataclass 
class EmbeddingResponse:
    """Standard response format for embeddings."""
    embeddings: np.ndarray  # Shape: (n_texts, embedding_dim)
    model: str
    provider: str
    tokens_used: int = 0
    cost_estimate: float = 0.0


class EmbeddingProvider(ABC):
    """Abstract base class for embedding providers."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.model = config.get('model', '')
        self._initialize()
    
    @abstractmethod
    def _initialize(self):
        """Initialize the embedding provider."""
        pass
    
    @abstractmethod
    def generate_embeddings(self, texts: List[str]) -> EmbeddingResponse:
        """Generate embeddings for a list of texts."""
        pass
    
    @abstractmethod
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings produced by this provider."""
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Get the name of this provider."""
        pass


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """
    OpenAI embeddings provider using their embeddings API.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.client = None
        super().__init__(config)
    
    def _initialize(self):
        """Initialize OpenAI client."""
        try:
            import openai
            api_key = self.config.get('api_key', '')
            if not api_key:
                raise ValueError("OpenAI API key required for embeddings")
            
            self.client = openai.OpenAI(api_key=api_key)
            
            # Validate model
            valid_models = [
                'text-embedding-ada-002',
                'text-embedding-3-small',
                'text-embedding-3-large'
            ]
            
            if self.model not in valid_models:
                raise ValueError(f"Invalid OpenAI embedding model: {self.model}")
                
        except ImportError:
            raise ImportError("openai package required for OpenAI embeddings")
        except Exception as e:
            raise Exception(f"Failed to initialize OpenAI embeddings: {e}")
    
    def generate_embeddings(self, texts: List[str]) -> EmbeddingResponse:
        """Generate embeddings using OpenAI API."""
        if not texts:
            return EmbeddingResponse(
                embeddings=np.array([]),
                model=self.model,
                provider=self.get_provider_name()
            )
        
        try:
            # OpenAI has a limit on batch size, so we may need to chunk
            batch_size = 100
            all_embeddings = []
            total_tokens = 0
            
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                
                response = self.client.embeddings.create(
                    model=self.model,
                    input=batch
                )
                
                # Extract embeddings
                batch_embeddings = [item.embedding for item in response.data]
                all_embeddings.extend(batch_embeddings)
                
                # Track token usage
                if hasattr(response, 'usage') and response.usage:
                    total_tokens += response.usage.total_tokens
            
            # Convert to numpy array
            embeddings_array = np.array(all_embeddings, dtype=np.float32)
            
            # Calculate cost
            cost_estimate = self._calculate_cost(total_tokens)
            
            return EmbeddingResponse(
                embeddings=embeddings_array,
                model=self.model,
                provider=self.get_provider_name(),
                tokens_used=total_tokens,
                cost_estimate=cost_estimate
            )
            
        except Exception as e:
            raise Exception(f"Failed to generate OpenAI embeddings: {e}")
    
    def get_embedding_dimension(self) -> int:
        """Get embedding dimension for OpenAI models."""
        dimensions = {
            'text-embedding-ada-002': 1536,
            'text-embedding-3-small': 1536,
            'text-embedding-3-large': 3072
        }
        return dimensions.get(self.model, 1536)
    
    def get_provider_name(self) -> str:
        """Return provider name."""
        return "openai_embeddings"
    
    def _calculate_cost(self, tokens_used: int) -> float:
        """Calculate cost for OpenAI embeddings."""
        # OpenAI embedding pricing (as of 2024)
        costs_per_token = {
            'text-embedding-ada-002': 0.0000001,    # $0.10 per 1M tokens
            'text-embedding-3-small': 0.00000002,   # $0.02 per 1M tokens
            'text-embedding-3-large': 0.00000013    # $0.13 per 1M tokens
        }
        
        cost_per_token = costs_per_token.get(self.model, 0.0000001)
        return tokens_used * cost_per_token


class LocalEmbeddingProvider(EmbeddingProvider):
    """
    Local embeddings provider using sentence-transformers.
    Runs models locally without API calls.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.sentence_model = None
        super().__init__(config)
    
    def _initialize(self):
        """Initialize sentence-transformers model."""
        try:
            from sentence_transformers import SentenceTransformer
            
            # Default to a good general-purpose model if none specified
            if not self.model:
                self.model = 'all-MiniLM-L6-v2'
            
            # Load the model (downloads on first use)
            self.sentence_model = SentenceTransformer(self.model)
            
        except ImportError:
            raise ImportError("sentence-transformers package required for local embeddings")
        except Exception as e:
            raise Exception(f"Failed to initialize local embedding model '{self.model}': {e}")
    
    def generate_embeddings(self, texts: List[str]) -> EmbeddingResponse:
        """Generate embeddings using local sentence-transformer model."""
        if not texts:
            return EmbeddingResponse(
                embeddings=np.array([]),
                model=self.model,
                provider=self.get_provider_name()
            )
        
        try:
            # Generate embeddings
            embeddings = self.sentence_model.encode(
                texts,
                convert_to_numpy=True,
                show_progress_bar=len(texts) > 50  # Show progress for large batches
            )
            
            # Ensure float32 type for consistent storage
            embeddings = embeddings.astype(np.float32)
            
            return EmbeddingResponse(
                embeddings=embeddings,
                model=self.model,
                provider=self.get_provider_name(),
                tokens_used=0,  # Local models don't use tokens
                cost_estimate=0.0  # No API cost
            )
            
        except Exception as e:
            raise Exception(f"Failed to generate local embeddings: {e}")
    
    def get_embedding_dimension(self) -> int:
        """Get embedding dimension for the loaded model."""
        if self.sentence_model is None:
            # Common dimensions for popular models
            common_dimensions = {
                'all-MiniLM-L6-v2': 384,
                'all-mpnet-base-v2': 768,
                'all-MiniLM-L12-v2': 384,
                'paraphrase-MiniLM-L6-v2': 384
            }
            return common_dimensions.get(self.model, 384)
        
        return self.sentence_model.get_sentence_embedding_dimension()
    
    def get_provider_name(self) -> str:
        """Return provider name."""
        return "local_embeddings"


class EmbeddingProviderFactory:
    """Factory for creating embedding providers."""
    
    PROVIDERS = {
        'openai': OpenAIEmbeddingProvider,
        'local': LocalEmbeddingProvider
    }
    
    @classmethod
    def create_provider(cls, config: Dict[str, Any]) -> EmbeddingProvider:
        """
        Create an embedding provider based on configuration.
        
        Args:
            config: Embedding configuration dictionary
        
        Returns:
            Configured EmbeddingProvider instance
        """
        provider_name = config.get('provider', 'local')
        
        if provider_name not in cls.PROVIDERS:
            available = list(cls.PROVIDERS.keys())
            raise ValueError(f"Unknown embedding provider '{provider_name}'. Available: {available}")
        
        provider_class = cls.PROVIDERS[provider_name]
        return provider_class(config)
    
    @classmethod
    def get_available_providers(cls) -> List[str]:
        """Get list of available embedding providers."""
        return list(cls.PROVIDERS.keys())