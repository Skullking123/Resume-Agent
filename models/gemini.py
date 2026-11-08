import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv
import google as genai
from google.genai import Client, types
from models.model import Model

load_dotenv()


class Gemini(Model):
    """Google Gemini model implementation.
    
    Requires GEMINI_API_KEY in .env file or environment variable.
    """
    
    def __init__(self, model_id: str, **kwargs):
        """Initialize the Gemini model.
        
        Args:
            model_id: Gemini model to use (e.g., "gemini-pro", "gemini-pro-vision")
            **kwargs: Additional parameters (temperature, top_p, etc.)
        
        Raises:
            ValueError: If GEMINI_API_KEY is not set
        """
        super().__init__(model_id, **kwargs)
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set")
        
        self.model = model_id
        
    def query(self, input_text: str, **kwargs) -> Dict[str, Any]:
        """Query the Gemini model and return both text and token usage.
        
        Args:
            input_text: The prompt to send to the model
            **kwargs: Generation parameters (temperature, max_output_tokens, etc.)
        
        Returns:
            Dictionary with 'text' and 'usage' keys containing:
            - text: Model response as a string
            - usage: Dictionary with token usage information
        
        Raises:
            Exception: If API call fails
        """
        try:
            generation_config = genai.types.GenerationConfig(**kwargs) if kwargs else None
            with Client() as client:
                response = client.models.generate_content(
                    model=self.model_id,
                    contents=input_text,
                    config=generation_config
                )
            return {
                "text": response.text,
                "usage": {
                    "prompt_tokens": response.usage_metadata.prompt_token_count,
                    "candidates_tokens": response.usage_metadata.candidates_token_count,
                    "total_tokens": response.usage_metadata.total_token_count
                }
            }
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")
    
    def is_available(self) -> bool:
        """Check if Gemini model is available and API is accessible.
        
        Returns:
            True if model is ready, False otherwise
        """
        try:
            api_key = os.getenv("GEMINI_API_KEY")
            return api_key is not None
        except Exception:
            return False
