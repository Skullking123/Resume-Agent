from models.model_factory import ModelFactory
from constants.ModelFamily import ModelFamilyEnum
import json


# Example tools for testing
def get_weather(location: str, unit: str = "C") -> str:
    """Simulated weather lookup tool."""
    weather_data = {
        "Paris": f"22°{unit}, Partly Cloudy, Humidity: 65%",
        "London": f"18°{unit}, Rainy, Humidity: 80%",
        "Tokyo": f"25°{unit}, Sunny, Humidity: 55%",
        "New York": f"20°{unit}, Mostly Cloudy, Humidity: 70%",
    }
    return weather_data.get(location, f"Weather data not available for {location}")


def calculate_distance(city1: str, city2: str) -> str:
    """Simulated distance calculator between cities."""
    distances = {
        ("Paris", "London"): "344 km",
        ("London", "Paris"): "344 km",
        ("Paris", "Tokyo"): "9,730 km",
        ("Tokyo", "Paris"): "9,730 km",
        ("New York", "London"): "5,570 km",
        ("London", "New York"): "5,570 km",
    }
    key = (city1, city2)
    return distances.get(key, f"Distance not found for {city1} to {city2}")


def add_numbers(a: float, b: float) -> str:
    """Add two numbers together."""
    return str(a + b)


def multiply_numbers(a: float, b: float) -> str:
    """Multiply two numbers together."""
    return str(a * b)


if __name__ == "__main__":
    print("=" * 70)
    print("GEMINI FUNCTION CALLING TEST")
    print("=" * 70)
    
    agent = ModelFactory.createModel(ModelFamilyEnum.GEMINI, "gemini-3.8-flash")
    
    # Test 1: Basic query without tools
    print("\n[Test 1] Basic Query (No Tools)")
    print("-" * 70)
    response = agent.query("Hello, please introduce yourself briefly")
    print(f"Response: {response['text']}")
    print(f"Tokens Used: {response['usage']['total_tokens']}")
    
    # Register tools
    print("\n[Registering Tools]")
    print("-" * 70)
    
    agent.define_tool(
        tool_name="get_weather",
        tool_desc="Get the current weather for a location",
        tool_callback=get_weather,
        tool_args={
            "location": {
                "type": "string",
                "description": "City name (e.g., Paris, London, Tokyo, New York)",
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
    print("✓ Registered: get_weather")
    
    agent.define_tool(
        tool_name="calculate_distance",
        tool_desc="Calculate the distance between two cities",
        tool_callback=calculate_distance,
        tool_args={
            "city1": {
                "type": "string",
                "description": "First city name",
                "required": True
            },
            "city2": {
                "type": "string",
                "description": "Second city name",
                "required": True
            }
        }
    )
    print("✓ Registered: calculate_distance")
    
    agent.define_tool(
        tool_name="add_numbers",
        tool_desc="Add two numbers together",
        tool_callback=add_numbers,
        tool_args={
            "a": {
                "type": "number",
                "description": "First number",
                "required": True
            },
            "b": {
                "type": "number",
                "description": "Second number",
                "required": True
            }
        }
    )
    print("✓ Registered: add_numbers")
    
    agent.define_tool(
        tool_name="multiply_numbers",
        tool_desc="Multiply two numbers together",
        tool_callback=multiply_numbers,
        tool_args={
            "a": {
                "type": "number",
                "description": "First number",
                "required": True
            },
            "b": {
                "type": "number",
                "description": "Second number",
                "required": True
            }
        }
    )
    print("✓ Registered: multiply_numbers")
    
    # Test 2: Weather query (should use get_weather tool)
    print("\n[Test 2] Weather Query (Should Use Tools)")
    print("-" * 70)
    response = agent.query("What's the weather like in Paris and London? Please use Celsius.")
    print(f"Response: {response['text']}")
    print(f"Tokens Used: {response['usage']['total_tokens']}")
    
    if response["tool_calls"]:
        print(f"\nTools Called ({len(response['tool_calls'])}):")
        for i, call in enumerate(response["tool_calls"], 1):
            print(f"  {i}. {call['tool']}({json.dumps(call['args'])})")
            print(f"     → Result: {call['result']}")
            print(f"     → Success: {call['success']}")
    else:
        print("No tools were called")
    
    # Test 3: Math query (should use math tools)
    print("\n[Test 3] Math Query (Should Use Multiple Tools)")
    print("-" * 70)
    response = agent.query("What is (15 + 8) * 3? Show me step by step using the available math tools.")
    print(f"Response: {response['text']}")
    print(f"Tokens Used: {response['usage']['total_tokens']}")
    
    if response["tool_calls"]:
        print(f"\nTools Called ({len(response['tool_calls'])}):")
        for i, call in enumerate(response["tool_calls"], 1):
            print(f"  {i}. {call['tool']}({json.dumps(call['args'])})")
            print(f"     → Result: {call['result']}")
            print(f"     → Success: {call['success']}")
    else:
        print("No tools were called")
    
    # Test 4: Distance query
    print("\n[Test 4] Distance Query (Should Use Tools)")
    print("-" * 70)
    response = agent.query("How far is it from Paris to Tokyo? And from New York to London?")
    print(f"Response: {response['text']}")
    print(f"Tokens Used: {response['usage']['total_tokens']}")
    
    if response["tool_calls"]:
        print(f"\nTools Called ({len(response['tool_calls'])}):")
        for i, call in enumerate(response["tool_calls"], 1):
            print(f"  {i}. {call['tool']}({json.dumps(call['args'])})")
            print(f"     → Result: {call['result']}")
            print(f"     → Success: {call['success']}")
    else:
        print("No tools were called")
    
    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)