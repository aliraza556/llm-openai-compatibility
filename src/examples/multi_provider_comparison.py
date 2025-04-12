import asyncio
import os
from typing import Dict, List, Optional
import json
from tabulate import tabulate
from agents import function_tool
from llm_compatibility import run_with_multiple_providers

@function_tool
def get_weather(city: str, country: Optional[str] = None) -> str:
    """Get the current weather for a city."""
    location = f"{city}, {country}" if country else city
    return f"The weather in {location} is currently sunny and 75°F with 30% humidity."

@function_tool
def search_web(query: str) -> str:
    """Search the web for information (simulated)."""
    return f"Here are the search results for '{query}':\n" + \
           f"1. Wikipedia: Information about {query}\n" + \
           f"2. News article: Recent developments related to {query}\n" + \
           f"3. Academic paper: Research on {query}"

@function_tool
def calculate(expression: str) -> str:
    """Evaluate a mathematical expression."""
    try:
        result = eval(expression)
        return f"The result of {expression} is {result}"
    except Exception as e:
        return f"Error evaluating expression: {str(e)}"

SYSTEM_PROMPT = """You are a helpful assistant that can answer questions using tools when needed.
When answering questions, use the provided tools if they would help with the answer.
Be concise and informative in your responses."""

EXAMPLE_QUERIES = [
    "What's the weather like in Tokyo, Japan?",
    "Can you calculate 137 * 429?",
    "Search for information about quantum computing",
    "What's 15% of 230?",
    "Tell me about the weather in Paris and Rome"
]

PROVIDERS = ["openai", "claude", "gemini", "deepseek"]
MODEL_NAMES = {
    "openai": "gpt-4o-2024-08-06",
    "claude": "claude-3-haiku-20240307",
    "gemini": "gemini-pro",
    "deepseek": "deepseek-chat"
}

API_KEYS = {
    "openai": os.environ.get("OPENAI_API_KEY", ""),
    "claude": os.environ.get("ANTHROPIC_API_KEY", ""),
    "gemini": os.environ.get("GEMINI_API_KEY", ""),
    "deepseek": os.environ.get("DEEPSEEK_API_KEY", "")
}

async def run_comparison():
    """Run the comparison with multiple providers and queries."""

    all_tools = [get_weather, search_web, calculate]
    
    available_providers = [p for p in PROVIDERS if API_KEYS.get(p)]
    
    if not available_providers:
        print("No API keys found. Please set at least one API key in the environment variables.")
        return
    
    print(f"Using providers: {', '.join(available_providers)}")
    print(f"Available tools: get_weather, search_web, calculate\n")
    
    all_results: Dict[str, Dict[str, str]] = {}
    
    for query in EXAMPLE_QUERIES:
        print(f"Query: {query}")
        print("-" * 50)
        
        messages = [{"role": "user", "content": query}]
        
        results = await run_with_multiple_providers(
            system_prompt=SYSTEM_PROMPT,
            messages=messages,
            providers=available_providers,
            model_names={p: MODEL_NAMES[p] for p in available_providers},
            api_keys={p: API_KEYS[p] for p in available_providers},
            tools=all_tools,
            temperature=0.7,
        )
        
        all_results[query] = results
        
        for provider, response in results.items():
            print(f"\n--- {provider.upper()} ---")
            print(response)
        
        print("\n" + "=" * 70 + "\n")
    
    print_comparison_table(all_results)
    
    with open("provider_comparison_results.json", "w") as f:
        json.dump(all_results, f, indent=2)
    print("Results saved to provider_comparison_results.json")

def print_comparison_table(results: Dict[str, Dict[str, str]]):
    """Print a comparison table of the results."""

    first_query = next(iter(results.values()))
    headers = ["Query"] + [p.upper() for p in first_query.keys()]
    
    rows = []
    for query, provider_results in results.items():
        short_query = query[:30] + "..." if len(query) > 30 else query

        short_responses = [short_query]
        for provider, response in provider_results.items():
            short_response = response[:50] + "..." if len(response) > 50 else response
            short_responses.append(short_response)
        
        rows.append(short_responses)
    
    print("\nComparison of Provider Responses (truncated):")
    print(tabulate(rows, headers=headers, tablefmt="grid"))

if __name__ == "__main__":

    try:
        import tabulate
    except ImportError:
        print("This example requires the tabulate package. Install it with: pip install tabulate")
        exit(1)
    
    asyncio.run(run_comparison()) 