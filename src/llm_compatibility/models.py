from typing import Any, Dict, List, Optional, Union
import os
from agents import Agent, AsyncOpenAI, OpenAIChatCompletionsModel, OpenAIResponsesModel

class LLMClient:
    """Factory class to create OpenAI-compatible clients for different LLM providers."""
    
    @staticmethod
    def create_client(provider: str, api_key: Optional[str] = None) -> AsyncOpenAI:
        """
        Create an AsyncOpenAI client for the specified provider.
        
        Args:
            provider: The LLM provider ('openai', 'claude', 'gemini', 'deepseek')
            api_key: Optional API key. If not provided, will look for environment variables.
            
        Returns:
            AsyncOpenAI client configured for the specified provider
        """
        providers = {
            "openai": {
                "base_url": "https://api.openai.com/v1/",
                "env_var": "OPENAI_API_KEY"
            },
            "claude": {
                "base_url": "https://api.anthropic.com/v1/",
                "env_var": "ANTHROPIC_API_KEY"
            },
            "gemini": {
                "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
                "env_var": "GEMINI_API_KEY"
            },
            "deepseek": {
                "base_url": "https://api.deepseek.com/v1/",
                "env_var": "DEEPSEEK_API_KEY"
            }
        }
        
        if provider.lower() not in providers:
            raise ValueError(f"Unsupported provider: {provider}. Supported providers are: {', '.join(providers.keys())}")
            
        provider_config = providers[provider.lower()]
        
        provider_api_key = api_key or os.environ.get(provider_config["env_var"])
        if not provider_api_key:
            raise ValueError(f"API key not provided and {provider_config['env_var']} environment variable not set")
            
        return AsyncOpenAI(
            base_url=provider_config["base_url"],
            api_key=provider_api_key
        )

class UniversalAgent:
    """
    A wrapper around the Agent class that supports multiple LLM providers.
    Simplifies creating agents with different LLM backends.
    """
    
    @staticmethod
    def create(
        provider: str,
        model_name: str,
        instructions: str,
        api_key: Optional[str] = None,
        tools: Optional[List] = None,
        handoffs: Optional[List[Agent]] = None,
        temperature: float = 0.7,
        name: str = "Assistant",
        use_responses_api: bool = False,
    ) -> Agent:
        """
        Create an agent with the specified LLM provider and model.
        
        Args:
            provider: The LLM provider ('openai', 'claude', 'gemini', 'deepseek')
            model_name: The model name specific to the provider
            instructions: The system prompt/instructions for the agent
            api_key: Optional API key. If not provided, will look for environment variables
            tools: Optional list of tools the agent can use
            handoffs: Optional list of agents this agent can hand off to
            temperature: Model temperature parameter
            name: Name of the agent
            use_responses_api: Whether to use OpenAIResponsesModel instead of OpenAIChatCompletionsModel
            
        Returns:
            An Agent configured with the specified LLM provider
        """
        tools = tools or []
        handoffs = handoffs or []
        
        client = LLMClient.create_client(provider, api_key)
        
        model_class = OpenAIResponsesModel if use_responses_api else OpenAIChatCompletionsModel
        
        model = model_class(
            model=model_name,
            openai_client=client,
            temperature=temperature,
        )
        
        return Agent(
            name=name,
            instructions=instructions,
            model=model,
            tools=tools,
            handoffs=handoffs,
        ) 