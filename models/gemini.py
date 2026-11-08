import os
from typing import Optional
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
    
    def query(self, input_text: str, **kwargs) -> str:
        """Query the Gemini model.
        
        Args:
            input_text: The prompt to send to the model
            **kwargs: Generation parameters (temperature, max_output_tokens, etc.)
        
        Returns:
            Model response as a string
        
        Raises:
            Exception: If API call fails
        """
        try:
            with Client() as client:
                response = client.models.generate_content(
                    model=self.model_id,
                    contents=input_text
                )
            return response.text
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
