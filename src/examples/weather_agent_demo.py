import asyncio
import os
from typing import Dict
from agents import function_tool
from llm_compatibility import UniversalAgent, run_with_multiple_providers_sync

@function_tool
def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    return f"The weather in {city} is currently sunny and 75°F."

SYSTEM_PROMPT = """You are a helpful assistant that provides weather information.
When asked about the weather in a location, use the get_weather tool to retrieve the information.
Respond in a friendly and conversational tone."""

MESSAGES = [
    {"role": "user", "content": "What's the weather like in San Francisco today?"}
]

PROVIDERS = ["openai", "claude", "gemini", "deepseek"]
MODEL_NAMES = {
    "openai": "gpt-4o-2024-08-06",
    "claude": "claude-3-haiku-20240307",
    "gemini": "gemini-pro",
    "deepseek": "deepseek-chat"
}

API_KEYS: Dict[str, str] = {
    "openai": os.environ.get("OPENAI_API_KEY", ""),
    "claude": os.environ.get("ANTHROPIC_API_KEY", ""),
    "gemini": os.environ.get("GEMINI_API_KEY", ""),
    "deepseek": os.environ.get("DEEPSEEK_API_KEY", "")
}

def main():
    """Run the example with multiple providers."""
    print("Running weather agent with multiple providers...")
    
    available_providers = [p for p in PROVIDERS if API_KEYS.get(p)]
    
    if not available_providers:
        print("No API keys found. Please set at least one API key in the environment variables.")
        return
    
    print(f"Using providers: {', '.join(available_providers)}")
    
    results = run_with_multiple_providers_sync(
        system_prompt=SYSTEM_PROMPT,
        messages=MESSAGES,
        providers=available_providers,
        model_names={p: MODEL_NAMES[p] for p in available_providers},
        api_keys={p: API_KEYS[p] for p in available_providers},
        tools=[get_weather],
        temperature=0.7,
    )
    
    for provider, response in results.items():
        print(f"\n--- {provider.upper()} ---")
        print(response)

if __name__ == "__main__":
    main() 