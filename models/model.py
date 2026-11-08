
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union


class Model(ABC):
    """Abstract base class for model implementations.
    
    Allows users to implement any model (LLM, classifier, etc.) by inheriting
    from this class and implementing the required methods.
    """
    
    def __init__(self, model_id: str, **kwargs):
        """Initialize the model.
        
        Args:
            model_id: The actual model being used (e.g., "gemini-pro", "gpt-4", "llama-2")
            **kwargs: Additional model-specific configuration parameters
        """
        self.model_id = model_id
        self.config = kwargs
    
    @abstractmethod
    def query(self, input_text: str, **kwargs) -> str:
        """Query the model with input text.
        
        Args:
            input_text: The input prompt or query
            **kwargs: Model-specific query parameters (temperature, max_tokens, etc.)
        
        Returns:
            Model output as a string along with token usage
        
        Raises:
            NotImplementedError: Must be implemented by subclass
        """
        raise NotImplementedError
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the model is available and ready to use.
        
        Returns:
            True if model is ready, False otherwise
        
        Raises:
            NotImplementedError: Must be implemented by subclass
        """
        raise NotImplementedError
    
    def batch_query(self, inputs: list[str], **kwargs) -> list[str]:
        """Query the model with multiple inputs.
        
        Args:
            inputs: List of input prompts
            **kwargs: Model-specific query parameters
        
        Returns:
            List of model outputs
        """
        return [self.query(inp, **kwargs) for inp in inputs]
    
    def get_config(self) -> Dict[str, Any]:
        """Get the model configuration.
        
        Returns:
            Dictionary of model configuration parameters
        """
        return {"model_id": self.model_id, **self.config}
