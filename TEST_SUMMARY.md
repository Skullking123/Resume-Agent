# main.py - Function Calling Test Suite

## What's New

The updated `main.py` now contains a comprehensive test suite for the new function calling feature.

## Test Suite Overview

### Structure

```
main.py
├── Tool Definitions (Simulated)
│   ├── get_weather() - Returns weather for cities
│   ├── calculate_distance() - Returns distance between cities
│   ├── add_numbers() - Adds two numbers
│   └── multiply_numbers() - Multiplies two numbers
│
└── Test Cases
    ├── Test 1: Basic Query (No Tools)
    ├── Test 2: Weather Query (Single Tool, Multiple Calls)
    ├── Test 3: Math Query (Multiple Tools, Chained)
    └── Test 4: Distance Query (Tool Reuse)
```

## Running the Tests

```bash
# Ensure GEMINI_API_KEY is set in .env
python main.py
```

## What Each Test Does

### Test 1: Basic Query (No Tools)
**Purpose:** Verify backward compatibility
- Query: "Hello, please introduce yourself briefly"
- Expected: Simple response without tool calls
- Validates: Basic query functionality works as before

### Test 2: Weather Query
**Purpose:** Test single tool with multiple invocations
- Query: "What's the weather like in Paris and London?"
- Expected: Model calls `get_weather` twice (once per city)
- Validates: Tool parameter passing, enum values (unit: C/F)

### Test 3: Math Query
**Purpose:** Test chained tool calls
- Query: "What is (15 + 8) * 3?"
- Expected: Model calls tools in sequence
  1. `add_numbers(15, 8)` → 23
  2. `multiply_numbers(23, 3)` → 69
- Validates: Multi-step reasoning, tool chaining

### Test 4: Distance Query
**Purpose:** Test tool reuse and complex reasoning
- Query: "How far is it from Paris to Tokyo? And from New York to London?"
- Expected: Model calls `calculate_distance` twice
- Validates: Parameter extraction, multiple tool calls

## Output Format

Each test displays:

```
[Test N] Description
-------
Response: [Final model answer]
Tokens Used: [Total tokens]

Tools Called (N):
  1. tool_name({"param": "value"})
     → Result: [tool result]
     → Success: True
  2. [next call...]
```

## Test Flow Diagram

```
┌─ Test 1: No Tools ──────┐
│  Query → Response       │
│  (No tool calls)        │
└─────────────────────────┘

┌─ Test 2: Weather ──────────────────┐
│  Query + Tools registered          │
│    → get_weather called            │
│    → get_weather called            │
│  → Final Response                  │
└────────────────────────────────────┘

┌─ Test 3: Math ───────────────────────┐
│  Query + Tools registered             │
│    → add_numbers(15, 8) = 23          │
│    → multiply_numbers(23, 3) = 69     │
│  → Final Response                     │
└───────────────────────────────────────┘

┌─ Test 4: Distance ─────────────────────┐
│  Query + Tools registered              │
│    → calculate_distance("Paris", "Tokyo")
│    → calculate_distance("NY", "London") │
│  → Final Response                      │
└────────────────────────────────────────┘
```

## Key Features Demonstrated

| Feature | Where | How |
|---------|-------|-----|
| Tool Registration | All tests | `define_tool()` method |
| Tool Invocation | Tests 2-4 | Model decides when to call |
| Parameter Types | Tests 2-4 | string, number, enum |
| Error Handling | All | success/failure tracking |
| Token Tracking | All | Cumulative across calls |
| Multi-Step Logic | Test 3 | Chained tool calls |
| Tool Reuse | Test 4 | Same tool called multiple times |

## Expected Results

- ✅ All syntax checks pass
- ✅ Model initializes successfully
- ✅ Tools are registered without errors
- ✅ Queries execute and return responses
- ✅ Tool calls are tracked in response
- ✅ Token usage is accumulated correctly

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "GEMINI_API_KEY not set" | Add to `.env`: `GEMINI_API_KEY=your-api-key` |
| "No tools called" | Query might not need tools; model decides usage |
| "Tool not found error" | Check tool is registered before query |
| "Parameter mismatch" | Ensure tool_args schema matches callback signature |

## Next Steps

1. ✅ Run `python main.py` to test
2. Review output for each test
3. Check tool_calls array for proper tracking
4. Monitor token usage across all calls
5. Extend with your own tools/queries

## Files Created/Modified

- ✅ `main.py` - Updated with comprehensive tests
- ✅ `FUNCTION_CALLING_GUIDE.md` - Feature documentation
- ✅ `TESTING_GUIDE.md` - Testing instructions
- ✅ `models/gemini.py` - Reworked query() with tool-calling loop

All tests are ready to run! 🚀
