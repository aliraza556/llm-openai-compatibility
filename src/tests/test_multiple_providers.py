import unittest
import os
import asyncio
from unittest.mock import patch, MagicMock
from typing import Dict, Any

from agents import Agent, Runner
from llm_compatibility import (
    LLMClient, 
    UniversalAgent,
    run_with_multiple_providers,
    run_with_multiple_providers_sync
)

class TestLLMCompatibility(unittest.TestCase):
    """Test cases for the LLM compatibility layer."""
    
    def setUp(self):
        """Set up test environment."""

        self.env_patcher = patch.dict(os.environ, {
            "OPENAI_API_KEY": "mock-openai-key",
            "ANTHROPIC_API_KEY": "mock-anthropic-key",
            "GEMINI_API_KEY": "mock-gemini-key",
            "DEEPSEEK_API_KEY": "mock-deepseek-key"
        })
        self.env_patcher.start()
        
        self.system_prompt = "You are a helpful assistant."
        self.messages = [{"role": "user", "content": "Hello, world!"}]
        self.providers = ["openai", "claude", "gemini", "deepseek"]
        self.model_names = {
            "openai": "gpt-4o",
            "claude": "claude-3-opus",
            "gemini": "gemini-pro",
            "deepseek": "deepseek-chat"
        }
        
    def tearDown(self):
        """Clean up after tests."""
        self.env_patcher.stop()
    
    def test_llm_client_create(self):
        """Test LLMClient.create_client method."""

        for provider in self.providers:
            client = LLMClient.create_client(provider)
            self.assertIsNotNone(client)
            
        with self.assertRaises(ValueError):
            LLMClient.create_client("invalid-provider")
            
        with patch.dict(os.environ, {"OPENAI_API_KEY": ""}):
            with self.assertRaises(ValueError):
                LLMClient.create_client("openai")
                
    def test_universal_agent_create(self):
        """Test UniversalAgent.create method."""

        for provider in self.providers:
            agent = UniversalAgent.create(
                provider=provider,
                model_name=self.model_names[provider],
                instructions=self.system_prompt
            )
            self.assertIsInstance(agent, Agent)
    
    @patch("agents.Runner.run")
    async def test_run_with_multiple_providers(self, mock_run):
        """Test run_with_multiple_providers function with parallel execution."""

        mock_result = MagicMock()
        mock_result.final_output = "Hello from the LLM!"
        mock_run.return_value = mock_result
        
        results = await run_with_multiple_providers(
            system_prompt=self.system_prompt,
            messages=self.messages,
            providers=self.providers,
            model_names=self.model_names
        )
        
        self.assertEqual(len(results), len(self.providers))
        for provider in self.providers:
            self.assertIn(provider, results)
            self.assertEqual(results[provider], "Hello from the LLM!")
            
        self.assertEqual(mock_run.call_count, len(self.providers))
    
    @patch("llm_compatibility.utils.run_with_multiple_providers")
    def test_run_with_multiple_providers_sync(self, mock_async_run):
        """Test run_with_multiple_providers_sync function."""

        expected_results = {provider: f"Hello from {provider}!" for provider in self.providers}
        mock_async_run.return_value = expected_results
        
        results = run_with_multiple_providers_sync(
            system_prompt=self.system_prompt,
            messages=self.messages,
            providers=self.providers,
            model_names=self.model_names
        )
        
        self.assertEqual(results, expected_results)
        mock_async_run.assert_called_once()
        
    @patch("agents.Runner.run")
    async def test_error_handling(self, mock_run):
        """Test error handling in parallel run_with_multiple_providers."""

        def side_effect(agent, input):
            if "claude" in str(agent.model):
                raise Exception("Test error")
            mock_result = MagicMock()
            mock_result.final_output = "Success"
            return mock_result
            
        mock_run.side_effect = side_effect
        
        results = await run_with_multiple_providers(
            system_prompt=self.system_prompt,
            messages=self.messages,
            providers=self.providers,
            model_names=self.model_names
        )
        
        for provider in self.providers:
            if provider == "claude":
                self.assertTrue(results[provider].startswith("Error:"))
            else:
                self.assertEqual(results[provider], "Success")

def async_test(coro):
    """Decorator for running async test methods."""
    def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(coro(*args, **kwargs))
    return wrapper

TestLLMCompatibility.test_run_with_multiple_providers = async_test(TestLLMCompatibility.test_run_with_multiple_providers)
TestLLMCompatibility.test_error_handling = async_test(TestLLMCompatibility.test_error_handling)

if __name__ == "__main__":
    unittest.main() 