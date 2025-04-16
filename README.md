# LLM OpenAI Compatibility Layer

A compatibility layer for using OpenAI Agents SDK with multiple LLM providers like Claude, Gemini, and Deepseek.

This library enables you to run the same prompts against multiple LLM providers using the OpenAI Agents SDK, leveraging its powerful features while not being tied to a single provider.

## Features

- Use OpenAI Agents SDK with multiple LLM providers (OpenAI, Claude, Gemini, Deepseek)
- Unified interface for creating agents with different backends
- Run the same prompt against multiple providers simultaneously
- Support for tool use across providers
- Support for JSON-defined tools with callback URLs
- Error handling and graceful degradation
- AWS Lambda integration for serverless deployment

## Installation

```bash
pip install llm-openai-compatibility
```

## Prerequisites

You need API keys for the LLM providers you want to use. Set them as environment variables:

```bash
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
export GEMINI_API_KEY="your-gemini-key"
export DEEPSEEK_API_KEY="your-deepseek-key"
```

## Quick Start

### Creating an Agent with Any LLM Provider

```python
from llm_compatibility import UniversalAgent

# Create an agent with Claude
claude_agent = UniversalAgent.create(
    provider="claude",
    model_name="claude-3-haiku-20240307",
    instructions="You are a helpful assistant that provides concise information."
)

# Create an agent with OpenAI
openai_agent = UniversalAgent.create(
    provider="openai",
    model_name="gpt-4o-2024-08-06",
    instructions="You are a helpful assistant that provides detailed explanations."
)
```

### Running with Multiple Providers Simultaneously

```python
from llm_compatibility import run_with_multiple_providers_sync
from agents import function_tool

# Define a tool
@function_tool
def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    return f"The weather in {city} is currently sunny and 75°F."

# System prompt and messages
system_prompt = "You are a weather assistant. Use the tool to get weather information."
messages = [{"role": "user", "content": "What's the weather in Tokyo?"}]

# Providers and models
providers = ["openai", "claude", "gemini"]
model_names = {
    "openai": "gpt-4o-2024-08-06",
    "claude": "claude-3-haiku-20240307",
    "gemini": "gemini-pro"
}

# Run with multiple providers
results = run_with_multiple_providers_sync(
    system_prompt=system_prompt,
    messages=messages,
    providers=providers,
    model_names=model_names,
    tools=[get_weather]
)

# Print results
for provider, response in results.items():
    print(f"\n--- {provider.upper()} ---")
    print(response)
```

### Using JSON-Defined Tools

You can define tools as JSON objects instead of Python functions:

```python
from llm_compatibility import run_with_multiple_providers_sync, create_tools_from_json

# Define tools as JSON
tools_json = [
    {
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
    },
    {
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
]

# Create function tools from JSON definitions
tools = create_tools_from_json(tools_json)

# Run with multiple providers
results = run_with_multiple_providers_sync(
    system_prompt="You are an assistant that can provide weather info and calculate expressions.",
    messages=[{"role": "user", "content": "What's the weather in Paris? Also, what's 137 * 429?"}],
    providers=["openai", "claude"],
    model_names={"openai": "gpt-4o", "claude": "claude-3-haiku"},
    tools=tools
)
```

#### Using Callback URLs

You can also define tools with callback URLs that will be called when the tool is invoked:

```python
callback_tool_json = {
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

# Create the tool
search_tool = create_tools_from_json(callback_tool_json)[0]

# When the tool is called, it will POST the parameters to the callback URL
# and return the response
```

## Documentation

### LLMClient

A factory class for creating OpenAI-compatible clients for different LLM providers.

```python
from llm_compatibility import LLMClient

# Create a client for Claude
claude_client = LLMClient.create_client(provider="claude")

# Create a client with explicit API key
openai_client = LLMClient.create_client(
    provider="openai",
    api_key="your-openai-key"
)
```

### UniversalAgent

A wrapper around the Agent class that simplifies creating agents with different LLM backends.

```python
from llm_compatibility import UniversalAgent

# Create a basic agent
agent = UniversalAgent.create(
    provider="openai",
    model_name="gpt-4o-2024-08-06",
    instructions="You are a helpful assistant.",
    temperature=0.7
)

# Create an agent with tools
from agents import function_tool

@function_tool
def calculator(a: float, b: float, operation: str) -> float:
    """Perform a mathematical operation on two numbers."""
    if operation == "add":
        return a + b
    elif operation == "subtract":
        return a - b
    elif operation == "multiply":
        return a * b
    elif operation == "divide":
        return a / b
    else:
        raise ValueError(f"Unknown operation: {operation}")

agent_with_tools = UniversalAgent.create(
    provider="claude",
    model_name="claude-3-opus-20240229",
    instructions="You are a math assistant.",
    tools=[calculator]
)
```

### run_with_multiple_providers

Run the same prompt against multiple LLM providers asynchronously.

```python
import asyncio
from llm_compatibility import run_with_multiple_providers

async def main():
    results = await run_with_multiple_providers(
        system_prompt="You are a helpful assistant.",
        messages=[{"role": "user", "content": "What is the capital of France?"}],
        providers=["openai", "claude"],
        model_names={"openai": "gpt-4o", "claude": "claude-3-haiku"}
    )
    print(results)

asyncio.run(main())
```

### run_with_multiple_providers_sync

Synchronous version of `run_with_multiple_providers`.

```python
from llm_compatibility import run_with_multiple_providers_sync

results = run_with_multiple_providers_sync(
    system_prompt="You are a helpful assistant.",
    messages=[{"role": "user", "content": "What is the capital of France?"}],
    providers=["openai", "claude"],
    model_names={"openai": "gpt-4o", "claude": "claude-3-haiku"}
)
print(results)
```

## Examples

See the `examples` directory for more examples of how to use the library:

- `weather_agent_demo.py`: Example of using a weather tool with multiple providers

## Testing

Run the tests with:

```bash
python -m unittest discover -s src/tests
```

## AWS Lambda Deployment

A Lambda handler is included for easy serverless deployment. It supports passing tools as JSON:

```python
from llm_compatibility import run_with_multiple_providers_sync, create_tools_from_json

def lambda_handler(event, context):
    # Get JSON tools from event or environment variables
    json_tools = event.get("json_tools") or os.environ.get("JSON_TOOLS")

    if json_tools:
        tools = create_tools_from_json(json_tools)
    else:
        tools = [default_tool]

    # Run against multiple providers
    return results
```

Configure with environment variables:

- `SYSTEM_PROMPT`: System prompt instructions
- `PROVIDERS`: Comma-separated list of providers
- `API_KEY_OPENAI`, `API_KEY_CLAUDE`, etc.: API keys for providers
- `JSON_TOOLS`: JSON string defining tools

See [Lambda Deployment Guide](src/examples/lambda_deployment.md) for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
