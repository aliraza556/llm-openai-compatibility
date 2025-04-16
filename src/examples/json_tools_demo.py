import json
import os
from typing import Dict, List
from llm_compatibility import (
    UniversalAgent, 
    run_with_multiple_providers_sync, 
    create_tools_from_json
)

WEATHER_TOOL_JSON = {
    "name": "get_weather",
    "description": "Get the current weather for a city.",
    "parameters": {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "The city to get weather for"
            },
            "country": {
                "type": "string",
                "description": "The country (optional)"
            }
        },
        "required": ["city"]
    }
}

CALCULATOR_TOOL_JSON = {
    "name": "calculate",
    "description": "Perform a calculation.",
    "parameters": {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "The mathematical expression to evaluate"
            }
        },
        "required": ["expression"]
    }
}

TOOLS_JSON = [WEATHER_TOOL_JSON, CALCULATOR_TOOL_JSON]

SYSTEM_PROMPT = """You are a helpful assistant that can answer questions using tools when needed.
When asked about the weather, use the get_weather tool.
When asked about calculations, use the calculate tool.
Be concise and informative in your responses."""

MESSAGES = [
    {"role": "user", "content": "What's the weather like in Tokyo, Japan? Also, what's 137 * 429?"}
]

PROVIDERS = ["openai", "claude"]
MODEL_NAMES = {
    "openai": "gpt-4o-2024-08-06",
    "claude": "claude-3-haiku-20240307"
}

API_KEYS: Dict[str, str] = {
    "openai": os.environ.get("OPENAI_API_KEY", ""),
    "claude": os.environ.get("ANTHROPIC_API_KEY", "")
}

def main():
    """Run the example with JSON-defined tools."""
    print("Running example with JSON-defined tools...")
    
    tools = create_tools_from_json(TOOLS_JSON)
    
    available_providers = [p for p in PROVIDERS if API_KEYS.get(p)]
    
    if not available_providers:
        print("No API keys found. Please set at least one API key in the environment variables.")
        return
    
    print(f"Using providers: {', '.join(available_providers)}")
    print(f"Tools created from JSON: {', '.join(tool.__name__ for tool in tools)}")
    
    results = run_with_multiple_providers_sync(
        system_prompt=SYSTEM_PROMPT,
        messages=MESSAGES,
        providers=available_providers,
        model_names={p: MODEL_NAMES[p] for p in available_providers},
        api_keys={p: API_KEYS[p] for p in available_providers},
        tools=tools,
        temperature=0.7,
    )
    
    for provider, response in results.items():
        print(f"\n--- {provider.upper()} ---")
        print(response)
        
    print("\n--- Example with callback URLs ---")
    CALLBACK_TOOL_JSON = {
        "name": "search_web",
        "description": "Search the web for information.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query"
                }
            },
            "required": ["query"]
        },
        "callback_url": "https://api.example.com/search"
    }
    
    callback_tool = create_tools_from_json(CALLBACK_TOOL_JSON)[0]
    print(f"Created callback tool: {callback_tool.__name__}")
    print(f"When called, it will make a POST request to: {CALLBACK_TOOL_JSON['callback_url']}")
    print("This is a mock example - in real usage, you would provide an actual API endpoint.")

if __name__ == "__main__":
    main()