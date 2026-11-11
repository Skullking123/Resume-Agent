# Function Calling Guide for Gemini Model

## Overview

The reworked `query()` function in the Gemini model now supports **tool-calling loops**. This means:

1. You define tools/functions that the model can call
2. When you query the model, it can decide to call these functions
3. The function results are returned to the model for further reasoning
4. This continues until the model provides a final answer

## How It Works

### 1. Define Your Tools

```python
from models.model_factory import ModelFactory, ModelFamily

agent = ModelFactory.createModel(ModelFamily.GEMINI, "gemini-3.8-flash")

# Define a function to use as a tool
def get_weather(location: str, unit: str = "C") -> str:
    """Get weather for a location. (Fake implementation)"""
    return f"Weather in {location}: 22°{unit}, Sunny"

# Register it as a tool
agent.define_tool(
    tool_name="get_weather",
    tool_desc="Get the current weather for a location",
    tool_callback=get_weather,
    tool_args={
        "location": {
            "type": "string",
            "description": "City name",
            "required": True
        },
        "unit": {
            "type": "string",
            "description": "Temperature unit (C or F)",
            "enum": ["C", "F"],
            "required": False
        }
    }
)
```

### 2. Query the Model

The model will now automatically use your tools when appropriate:

```python
response = agent.query("What's the weather in Paris?")

print(response["text"])  # Final answer from model
print(response["usage"])  # Token usage stats
print(response["tool_calls"])  # List of tools that were called
```

### 3. Response Structure

The `query()` function returns a dictionary with:

```python
{
    "text": "Based on the weather data I retrieved, it's 22°C and sunny in Paris.",
    "usage": {
        "prompt_tokens": 150,
        "candidates_tokens": 50,
        "total_tokens": 200
    },
    "tool_calls": [
        {
            "tool": "get_weather",
            "args": {"location": "Paris", "unit": "C"},
            "result": "Weather in Paris: 22°C, Sunny",
            "success": True
        }
    ]
}
```

## Tool-Calling Loop

The `query()` function implements this loop:

```
1. Send prompt + tools to Gemini
2. Get response
3. Check if model wants to call a function
   - If yes → Execute the function → Send results back to model → Go to step 2
   - If no → Return final response
```

This continues until the model decides it has enough information to answer.

## Example: Multi-Step Tool Use

```python
def add_numbers(a: float, b: float) -> float:
    return a + b

def multiply_numbers(a: float, b: float) -> float:
    return a * b

agent.define_tool("add_numbers", "Add two numbers", add_numbers, {
    "a": {"type": "number", "description": "First number", "required": True},
    "b": {"type": "number", "description": "Second number", "required": True}
})

agent.define_tool("multiply_numbers", "Multiply two numbers", multiply_numbers, {
    "a": {"type": "number", "description": "First number", "required": True},
    "b": {"type": "number", "description": "Second number", "required": True}
})

response = agent.query("What is (5 + 3) * 2?")
# Model will:
# 1. Call add_numbers(5, 3) → 8
# 2. Call multiply_numbers(8, 2) → 16
# 3. Return: "The answer is 16"
```

## Token Usage Tracking

Token usage is **accumulated across all API calls** in the loop:

```python
response = agent.query("Complex query requiring multiple tool calls")

total_tokens = response["usage"]["total_tokens"]  # Sum of all calls
prompt_tokens = response["usage"]["prompt_tokens"]  # All prompts combined
candidate_tokens = response["usage"]["candidates_tokens"]  # All responses combined
```

## Error Handling

If a tool execution fails, it's tracked in the response:

```python
{
    "tool": "get_weather",
    "args": {"location": "InvalidCity"},
    "result": "Error executing get_weather: Invalid city name",
    "success": False  # ← Indicates failure
}
```

The model still gets the error message and can use it to refine its approach.

## Important Notes

1. **Tools are optional** — If `self.tools` is empty, `query()` works normally
2. **No tools are called by default** — The model decides if it needs tools based on your prompt
3. **Streaming not supported yet** — The function waits for complete responses
4. **All tool args are kwargs** — Pass as named arguments to your callback function
5. **Tool results are strings** — Convert complex data to strings if needed

## Updating Your Usage

If you were previously using:

```python
# Old way
response = agent.query("Hello, introduce yourself")
print(response["total_token_count"])  # ❌ No longer exists
```

Update to:

```python
# New way
response = agent.query("Hello, introduce yourself")
print(response["usage"]["total_tokens"])  # ✅ Correct path
print(response["text"])  # Get the actual response text
```
