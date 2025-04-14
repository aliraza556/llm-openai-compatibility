from typing import Dict, List, Any, Optional
import asyncio
from agents import Runner

async def run_with_multiple_providers(
    system_prompt: str,
    messages: List[Dict[str, str]],
    providers: List[str],
    model_names: Dict[str, str],
    api_keys: Optional[Dict[str, str]] = None,
    tools: Optional[List] = None,
    temperature: float = 0.7,
) -> Dict[str, Any]:
    """
    Run the same prompt against multiple LLM providers in parallel and return the results.
    
    Args:
        system_prompt: The system prompt/instructions
        messages: List of message objects with role and content keys
        providers: List of provider names ('openai', 'claude', 'gemini', 'deepseek')
        model_names: Dict mapping provider names to model names
        api_keys: Optional dict mapping provider names to API keys
        tools: Optional list of tools to use
        temperature: Model temperature parameter
        
    Returns:
        Dict mapping provider names to their responses
    """
    from .models import UniversalAgent
    
    api_keys = api_keys or {}
    tools = tools or []
    
    async def run_provider(provider: str) -> tuple[str, str]:
        """Run a single provider and return the result."""
        if provider not in model_names:
            raise ValueError(f"No model name specified for provider: {provider}")
            
        agent = UniversalAgent.create(
            provider=provider,
            model_name=model_names[provider],
            instructions=system_prompt,
            api_key=api_keys.get(provider),
            tools=tools,
            temperature=temperature,
        )
        
        input_message = next((msg["content"] for msg in messages if msg["role"] == "user"), "")
        
        try:
            result = await Runner.run(agent, input=input_message)
            return provider, result.final_output
        except Exception as e:
            return provider, f"Error: {str(e)}"
    
    tasks = [run_provider(provider) for provider in providers]
    results_list = await asyncio.gather(*tasks)
    
    return {provider: result for provider, result in results_list}

def run_with_multiple_providers_sync(
    system_prompt: str,
    messages: List[Dict[str, str]],
    providers: List[str],
    model_names: Dict[str, str],
    api_keys: Optional[Dict[str, str]] = None,
    tools: Optional[List] = None,
    temperature: float = 0.7,
) -> Dict[str, Any]:
    """
    Synchronous version of run_with_multiple_providers.
    """
    return asyncio.run(
        run_with_multiple_providers(
            system_prompt=system_prompt,
            messages=messages,
            providers=providers,
            model_names=model_names,
            api_keys=api_keys,
            tools=tools,
            temperature=temperature,
        )
    ) 