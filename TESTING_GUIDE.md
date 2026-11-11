# Testing Function Calling Feature

## Overview

The updated `main.py` provides a comprehensive test suite for the new function calling feature in the Gemini model.

## What Gets Tested

### Test 1: Basic Query (No Tools)
- Ensures the model still works without any tools defined
- Verifies basic response and token counting

### Test 2: Weather Query (Single Tool)
- Registers the `get_weather` tool
- Queries for weather in multiple cities
- Tests tool invocation with parameters

### Test 3: Math Query (Multiple Tools)
- Registers math tools (`add_numbers`, `multiply_numbers`)
- Requests a calculation that requires multiple tool calls
- Tests chained tool usage and multi-step reasoning

### Test 4: Distance Query (Tool Reuse)
- Uses the `calculate_distance` tool for multiple city pairs
- Tests the model's ability to call the same tool multiple times

## Running the Tests

```bash
# Make sure you have your GEMINI_API_KEY set in .env
python main.py
```

## Expected Output

For each test, you'll see:

```
[Test X] Description
-------
Response: [Model's final answer]
Tokens Used: [Total tokens across all API calls]

Tools Called (N):
  1. tool_name({"arg1": "value1"})
     → Result: [tool result]
     → Success: True/False
  2. [Next tool call]...
```

## Example Output

```
[Test 2] Weather Query (Should Use Tools)
------
Response: Based on the current weather data, Paris is experiencing partly 
cloudy conditions at 22°C with 65% humidity, while London is rainy with 
18°C and 80% humidity.

Tokens Used: 450

Tools Called (2):
  1. get_weather({"location": "Paris", "unit": "C"})
     → Result: 22°C, Partly Cloudy, Humidity: 65%
     → Success: True
  2. get_weather({"location": "London", "unit": "C"})
     → Result: 18°C, Rainy, Humidity: 80%
     → Success: True
```

## Key Features Demonstrated

1. **Tool Registration** — Shows how to define tools with `define_tool()`
2. **Tool Invocation** — Model automatically calls tools when needed
3. **Parameter Passing** — Tests different parameter types (string, number, enum)
4. **Error Handling** — Shows success/failure tracking
5. **Token Accounting** — Demonstrates cumulative token tracking across multiple API calls
6. **Multi-Step Reasoning** — Tests chained tool calls for complex problems

## Troubleshooting

### "GEMINI_API_KEY not set"
- Make sure your `.env` file contains: `GEMINI_API_KEY=your-key-here`
- Verify the file is in the project root directory

### "No tools were called"
- This might happen if the model decides tools aren't needed for that query
- Some queries might not require tools (e.g., "introduce yourself")
- Try rephrasing to make it clear tools are helpful

### "Error executing tool"
- Check the tool callback function for bugs
- Verify all required parameters are being passed
- Look at the error message in the result

## Extending the Tests

To add more tests:

```python
# Define a new tool
def my_tool(param1: str) -> str:
    return f"Result for {param1}"

# Register it
agent.define_tool(
    tool_name="my_tool",
    tool_desc="What this tool does",
    tool_callback=my_tool,
    tool_args={
        "param1": {
            "type": "string",
            "description": "Description of param1",
            "required": True
        }
    }
)

# Test it
response = agent.query("Use my_tool for...")
print(f"Response: {response['text']}")
print(f"Tool calls: {response['tool_calls']}")
```

## Notes

- The simulated tools (weather, distance, math) return fake data for testing
- In production, you'd integrate with real APIs
- The test demonstrates the complete function calling loop
- All tool calls are tracked and returned in the response
