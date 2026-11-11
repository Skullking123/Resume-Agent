
import contextlib
import inspect
import io
import traceback
import types
from abc import ABC, abstractmethod
from typing import (
    Any, Callable, Dict, Literal, Optional, Union, get_args, get_origin, get_type_hints,
)


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
        self.tools = []
        self.tool_funcs = {}
    
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
    
    @abstractmethod
    def define_tool(
        self,
        tool_name: str,
        tool_desc: str,
        tool_callback: Callable[..., Any],
        tool_args: Dict[str, Dict[str, Any]],
    ) -> None:
        """
        Args:
            tool_name: Unique name for the tool
            tool_desc: Human-readable description of what the tool does
            tool_callback: Function to execute when tool is called
            tool_args: Dict mapping arg names to their schemas
                {
                    "location": {
                        "type": "string",
                        "description": "City name",
                        "required": True
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["C", "F"],
                        "required": False
                    }
                }
        
        Raises:
            NotImplementedError: Subclass must implement
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
