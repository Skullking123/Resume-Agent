import os
from typing import List, Dict, Any
from dotenv import load_dotenv
import google as genai
from google.genai import Client, types
from models.model import Model
from typing import Callable
from constants.ParameterTypes import ParameterTypesEnum

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
        
        # Verify API key exsists
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set")
        
        
    def query(self, input_text: str, **kwargs) -> Dict[str, Any]:
        """Query the Gemini model with support for function calling.
        
        Implements a tool-use loop using the Interactions API: sends the prompt
        with any defined tools, handles function calls from the model, executes
        callbacks, and returns the final response with accumulated token usage.
        
        Args:
            input_text: The prompt to send to the model
            **kwargs: Generation parameters (temperature, max_output_tokens, etc.)
        
        Returns:
            Dictionary with:
            - 'text': Final model response as a string (after all tool calls)
            - 'usage': Dict with token usage across all API calls:
                - 'prompt_tokens': Tokens in input
                - 'candidates_tokens': Tokens in output
                - 'total_tokens': Sum of all tokens used
            - 'tool_calls': List of tools called (if any), with results
        
        Raises:
            Exception: If API call or tool execution fails
        """
        try:
            generation_config = genai.types.GenerationConfig(**kwargs) if kwargs else None
            total_prompt_tokens = 0
            total_candidates_tokens = 0
            tool_calls_made = []
            
            with Client() as client:
                # Initialize interaction with the input and tools
                # Use client.interactions.create() for better function calling support
                interaction = client.interactions.create(
                    model=self.model_id,
                    input=input_text,
                    tools=self.tools if self.tools else None,
                    generation_config=generation_config
                )
                
                # Process the interaction steps until no more tool calls
                while True:
                    # Accumulate token usage from current state
                    if hasattr(interaction, 'token_count'):
                        total_prompt_tokens += interaction.token_count.input_token_count
                        total_candidates_tokens += interaction.token_count.output_token_count
                    
                    # Check if there are any function calls in the steps
                    function_calls = self._extract_function_calls_from_interaction(interaction)
                    
                    if not function_calls:
                        # No function calls - model has provided final response
                        final_text = self._get_final_response_text(interaction)
                        return {
                            "text": final_text,
                            "usage": {
                                "prompt_tokens": total_prompt_tokens,
                                "candidates_tokens": total_candidates_tokens,
                                "total_tokens": total_prompt_tokens + total_candidates_tokens
                            },
                            "tool_calls": tool_calls_made
                        }
                    
                    # Process each function call and submit results
                    for func_call in function_calls:
                        tool_name = func_call.name
                        tool_args = func_call.args
                        
                        # Execute the tool
                        try:
                            if tool_name not in self.tool_funcs:
                                result = f"Error: Tool '{tool_name}' not found"
                            else:
                                callback = self.tool_funcs[tool_name]
                                result = callback(**tool_args)
                            
                            success = True
                        except Exception as e:
                            result = f"Error executing {tool_name}: {str(e)}"
                            success = False
                        
                        # Track the tool call
                        tool_calls_made.append({
                            "tool": tool_name,
                            "args": tool_args,
                            "result": result,
                            "success": success
                        })
                        
                        # Submit the function result back to the interaction
                        interaction = client.interactions.submit(
                            name=func_call.name,
                            response=result
                        )
        
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")
    
    def _extract_function_calls_from_interaction(self, interaction) -> List[Any]:
        """Extract function calls from interaction steps.
        
        Args:
            interaction: Interaction object from Gemini Interactions API
        
        Returns:
            List of function call objects, empty if no function calls
        """
        function_calls = []
        
        # Iterate through interaction steps to find function calls
        if hasattr(interaction, 'steps'):
            for step in interaction.steps:
                if hasattr(step, 'type') and step.type == "function_call":
                    function_calls.append(step)
                elif hasattr(step, 'function_call'):
                    function_calls.append(step.function_call)
        
        return function_calls
    
    def _get_final_response_text(self, interaction) -> str:
        """Extract the final text response from interaction.
        
        Args:
            interaction: Interaction object from Gemini Interactions API
        
        Returns:
            Final response text, or empty string if none
        """
        if hasattr(interaction, 'response') and hasattr(interaction.response, 'text'):
            return interaction.response.output_text
        
        # Try to extract from latest step
        if hasattr(interaction, 'steps') and interaction.steps:
            for step in reversed(interaction.steps):
                if hasattr(step, 'text') and step.text:
                    return step.text
        
        return ""
    
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

    def define_tool(
        self,
        tool_name: str,
        tool_desc: str,
        tool_callback: Callable[..., Any],
        tool_args: Dict[str, Dict[str, Any]],
    ) -> None:
        """Register a tool that Gemini can call.
        
        Args:
            tool_name: Unique name for the tool (used in function calls)
            tool_desc: Human-readable description of what the tool does
            tool_callback: Python function to execute when tool is called
            tool_args: Dict mapping argument names to their schemas.
                Each value should be a dict with:
                - "type": JSON Schema type (string, number, integer, boolean, array, object)
                - "description": What this argument does
                - "required" (optional): Whether this argument is required (default: False)
                - "enum" (optional): List of allowed values
                - "items" (optional): For arrays, schema of array items
        
        Raises:
            ValueError: If tool definition is invalid
        
        Example:
            model.define_tool(
                tool_name="get_weather",
                tool_desc="Get the current weather for a location",
                tool_callback=get_weather_func,
                tool_args={
                    "location": {
                        "type": "string",
                        "description": "City name and country",
                        "required": True
                    },
                    "unit": {
                        "type": "string",
                        "description": "Temperature unit",
                        "enum": ["C", "F"],
                        "required": False
                    }
                }
            )
        """
        # Validate all args have a type
        required = []
        properties = {}
        
        for arg_name, arg_schema in tool_args.items():
            # all args need to have a type
            if "type" not in arg_schema:
                raise ValueError(f"Argument '{arg_name}' must have a 'type' defined")
            
            # Extract the schema for this property
            prop_schema = {k: v for k, v in arg_schema.items() if k != "required"}
            properties[arg_name] = prop_schema
            
            # Track which args are required
            if arg_schema.get("required", False):
                required.append(arg_name)
        
        # Store the callback function for later execution
        self.tool_funcs[tool_name] = tool_callback
        
        # Create Gemini-formatted function schema
        tool_schema = {
            "type": "function",
            "name": tool_name,
            "description": tool_desc,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required
            }
        }
        
        # Add to tools list for passing to the model
        self.tools.append(tool_schema)

