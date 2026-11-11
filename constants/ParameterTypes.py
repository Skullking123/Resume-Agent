from enum import Enum

class ParameterTypesEnum(str, Enum):
    """Enum for JSON Schema parameter types used in tool/function calling.
    
    Corresponds to JSON Schema type keywords and is compatible with:
    - Google Gemini API (function calling)
    - OpenAI ChatGPT API (function calling)
    - Anthropic Claude API (tool use)
    
    Usage:
        skill_args = {
            "location": {"type": ParameterTypes.STRING},
            "temperature": {"type": ParameterTypes.NUMBER},
            "is_active": {"type": ParameterTypes.BOOLEAN},
            "tags": {"type": ParameterTypes.ARRAY},
        }
    """
    
    # Primitive types
    STRING = "string"
    NUMBER = "number"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    
    # Complex types
    ARRAY = "array"
    OBJECT = "object"
    
    # Null type
    NULL = "null"