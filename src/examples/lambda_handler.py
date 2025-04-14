import json
import os
from typing import Dict, Any, List
from agents import function_tool
from llm_compatibility import run_with_multiple_providers_sync

@function_tool
def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    return f"The weather in {city} is currently sunny and 75°F."


def get_env_list(env_var_name: str) -> List[str]:
    """Get a comma-separated list from an environment variable."""
    value = os.environ.get(env_var_name, "")
    if not value:
        return []
    return [item.strip() for item in value.split(",")]

def get_env_dict(key_prefix: str, keys: List[str]) -> Dict[str, str]:
    """Get a dictionary from environment variables with a prefix."""
    result = {}
    for key in keys:
        env_key = f"{key_prefix}_{key.upper()}"
        value = os.environ.get(env_key)
        if value:
            result[key] = value
    return result

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler function that runs prompts against multiple LLM providers in parallel.
    
    Environment Variables:
        SYSTEM_PROMPT: The system prompt/instructions
        USER_MESSAGE: Default user message if not provided in the event
        PROVIDERS: Comma-separated list of providers (openai,claude,gemini,deepseek)
        MODEL_NAME_OPENAI: Model name for OpenAI
        MODEL_NAME_CLAUDE: Model name for Claude
        MODEL_NAME_GEMINI: Model name for Gemini
        MODEL_NAME_DEEPSEEK: Model name for Deepseek
        API_KEY_OPENAI: API key for OpenAI
        API_KEY_CLAUDE: API key for Claude (Anthropic)
        API_KEY_GEMINI: API key for Gemini
        API_KEY_DEEPSEEK: API key for Deepseek
        TEMPERATURE: Temperature parameter (default: 0.7)
    
    Event Structure:
        {
            "message": "Optional user message to override USER_MESSAGE env var",
            "providers": ["optional", "provider", "list"],
            "temperature": Optional temperature override
        }
    
    Returns:
        Dictionary with provider responses from all providers run in parallel
    """

    system_prompt = os.environ.get("SYSTEM_PROMPT", "You are a helpful assistant that provides weather information.")
    default_user_message = os.environ.get("USER_MESSAGE", "What's the weather like in San Francisco?")
    
    providers = event.get("providers") or get_env_list("PROVIDERS")
    
    if not providers:
        providers = ["openai"]
    
    model_names = get_env_dict("MODEL_NAME", providers)
    
    default_models = {
        "openai": "gpt-4o-2024-08-06",
        "claude": "claude-3-haiku-20240307",
        "gemini": "gemini-pro",
        "deepseek": "deepseek-chat"
    }
    
    for provider in providers:
        if provider not in model_names and provider in default_models:
            model_names[provider] = default_models[provider]
    
    api_keys = get_env_dict("API_KEY", providers)
    
    temperature = float(event.get("temperature", os.environ.get("TEMPERATURE", "0.7")))
    
    user_message = event.get("message", default_user_message)
    
    messages = [{"role": "user", "content": user_message}]
    
    results = run_with_multiple_providers_sync(
        system_prompt=system_prompt,
        messages=messages,
        providers=providers,
        model_names=model_names,
        api_keys=api_keys,
        tools=[get_weather],
        temperature=temperature,
    )
    
    response = {
        "statusCode": 200,
        "body": json.dumps({
            "input": {
                "message": user_message,
                "providers": providers,
                "temperature": temperature
            },
            "results": results
        })
    }
    
    return response

if __name__ == "__main__":

    test_event = {
        "message": "What's the weather in New York?",
        "providers": ["openai", "claude"]
    }
    
    result = lambda_handler(test_event, None)
    print(json.dumps(result, indent=2)) 