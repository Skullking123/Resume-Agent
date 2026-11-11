# Quick Start - Function Calling Test

## 1. Verify Setup
```bash
# Ensure .env has your API key
cat .env  # Should contain: GEMINI_API_KEY=sk-...
```

## 2. Run Tests
```bash
python main.py
```

## 3. Expected Output Example

```
======================================================================
GEMINI FUNCTION CALLING TEST
======================================================================

[Test 1] Basic Query (No Tools)
------
Response: I'm Claude, an AI assistant...
Tokens Used: 145

[Registering Tools]
------
✓ Registered: get_weather
✓ Registered: calculate_distance
✓ Registered: add_numbers
✓ Registered: multiply_numbers

[Test 2] Weather Query (Should Use Tools)
------
Response: Based on the weather data, Paris is 22°C and Partly Cloudy...

Tokens Used: 425

Tools Called (2):
  1. get_weather({"location": "Paris", "unit": "C"})
     → Result: 22°C, Partly Cloudy, Humidity: 65%
     → Success: True
  2. get_weather({"location": "London", "unit": "C"})
     → Result: 18°C, Rainy, Humidity: 80%
     → Success: True

[Test 3] Math Query (Should Use Multiple Tools)
------
Response: (15 + 8) * 3 = 69. First I added 15 + 8 = 23, 
then multiplied 23 * 3 = 69.

Tokens Used: 380

Tools Called (2):
  1. add_numbers({"a": 15, "b": 8})
     → Result: 23
     → Success: True
  2. multiply_numbers({"a": 23, "b": 3})
     → Result: 69
     → Success: True

[Test 4] Distance Query (Should Use Tools)
------
Response: Paris to Tokyo is 9,730 km. New York to London is 5,570 km...

Tokens Used: 410

Tools Called (2):
  1. calculate_distance({"city1": "Paris", "city2": "Tokyo"})
     → Result: 9,730 km
     → Success: True
  2. calculate_distance({"city1": "New York", "city2": "London"})
     → Result: 5,570 km
     → Success: True

======================================================================
TEST COMPLETE
======================================================================
```

## 4. What Just Happened

✅ **Test 1** - Verified basic query works
✅ **Test 2** - Model called `get_weather` twice (for Paris and London)
✅ **Test 3** - Model chained calls: `add_numbers` then `multiply_numbers`
✅ **Test 4** - Model called `calculate_distance` twice

## 5. Key Points

| Aspect | Result |
|--------|--------|
| Model | Initialized successfully |
| Tools | All 4 registered |
| Test 1 | No tool calls (expected) |
| Test 2 | 2 tool calls (weather) |
| Test 3 | 2 chained tool calls (math) |
| Test 4 | 2 tool calls (distance) |
| **Total** | **6 tool calls total** |

## 6. Understand the Response

```python
response = agent.query("...")

# Get the final answer
response["text"]           # "The answer is..."

# See how many tokens were used
response["usage"]["total_tokens"]           # 425

# See what tools were called
response["tool_calls"]     # [{"tool": "...", "args": {...}, ...}]

# Each tool call has:
for call in response["tool_calls"]:
    call["tool"]          # "get_weather"
    call["args"]          # {"location": "Paris", "unit": "C"}
    call["result"]        # "22°C, Partly Cloudy..."
    call["success"]       # True/False
```

## 7. Common Issues

**Issue:** No tools called in Test 2-4
- **Fix:** The model decides if tools are needed. Queries might not require them.

**Issue:** "GEMINI_API_KEY not set"
- **Fix:** Add to `.env`: `GEMINI_API_KEY=your-api-key`

**Issue:** "Tool not found" error
- **Fix:** Tool registration failed. Check tool_name matches in query.

## 8. Next Steps

1. ✅ Run `python main.py` to confirm everything works
2. 📖 Read `FUNCTION_CALLING_GUIDE.md` for feature details
3. 🔧 Modify tools in `main.py` to test different scenarios
4. 🚀 Integrate function calling into your application

## 9. Files to Read

- **CHANGES_SUMMARY.md** - What changed and why
- **FUNCTION_CALLING_GUIDE.md** - How to use function calling
- **VISUAL_TEST_GUIDE.txt** - Flowcharts and examples
- **TESTING_GUIDE.md** - Testing instructions

## 10. Test Results Checklist

After running `python main.py`, verify:

- [ ] Test 1 completes (basic query)
- [ ] Tools register successfully (4 checkmarks)
- [ ] Test 2 shows weather tool calls
- [ ] Test 3 shows chained math operations
- [ ] Test 4 shows distance calculations
- [ ] All tools show "Success: True"
- [ ] Token counts are positive
- [ ] No error messages appear
- [ ] "TEST COMPLETE" message appears at end

All 8 items ✓ = **Success!** 🎉

---

**Ready?** Run: `python main.py`
