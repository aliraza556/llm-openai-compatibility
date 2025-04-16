import unittest
from unittest.mock import MagicMock, patch
import json
import requests
from llm_compatibility import JsonTool, create_tools_from_json

class TestJsonTools(unittest.TestCase):
    """Test cases for the JSON tools functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.weather_tool_json = {
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
        
        self.calculate_tool_json = {
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
        
        self.callback_tool_json = {
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
    
    def test_create_single_tool(self):
        """Test creating a single tool from JSON."""
        tool = JsonTool.from_json(self.weather_tool_json)
        
        self.assertEqual(tool.__name__, "get_weather")
        self.assertEqual(tool.__doc__, "Get the current weather for a city.")
        self.assertTrue(hasattr(tool, "tool_schema"))
        self.assertEqual(tool.tool_schema["function"]["name"], "get_weather")
        
        result = tool(city="Tokyo", country="Japan")
        self.assertTrue("Tokyo" in result)
        self.assertTrue("Japan" in result)
    
    def test_create_multiple_tools(self):
        """Test creating multiple tools from JSON."""
        tools_json = [self.weather_tool_json, self.calculate_tool_json]
        tools = create_tools_from_json(tools_json)
        
        self.assertEqual(len(tools), 2)
        self.assertEqual(tools[0].__name__, "get_weather")
        self.assertEqual(tools[1].__name__, "calculate")
        
        weather_result = tools[0](city="Berlin")
        calculate_result = tools[1](expression="2+2")
        
        self.assertTrue("Berlin" in weather_result)
        self.assertTrue("2+2" in calculate_result)
    
    def test_create_from_json_string(self):
        """Test creating tools from a JSON string."""
        tools_json_str = json.dumps([self.weather_tool_json, self.calculate_tool_json])
        tools = create_tools_from_json(tools_json_str)
        
        self.assertEqual(len(tools), 2)
        self.assertEqual(tools[0].__name__, "get_weather")
        self.assertEqual(tools[1].__name__, "calculate")
    
    @patch('requests.post')
    def test_callback_tool(self, mock_post):
        """Test a tool with a callback URL."""
        mock_response = MagicMock()
        mock_response.text = "Mocked search results for 'AI'"
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response
        
        tool = JsonTool.from_json(self.callback_tool_json)
        
        result = tool(query="AI")
        
        mock_post.assert_called_once_with(
            self.callback_tool_json["callback_url"],
            json={"name": "search_web", "parameters": {"query": "AI"}}
        )
        
        self.assertEqual(result, "Mocked search results for 'AI'")
    
    @patch('requests.post')
    def test_callback_error(self, mock_post):
        """Test error handling in callback tools."""

        mock_post.side_effect = requests.RequestException("Connection error")
        
        tool = JsonTool.from_json(self.callback_tool_json)
        
        result = tool(query="AI")
        
        self.assertTrue(result.startswith("Error calling"))
        self.assertTrue("Connection error" in result)
    
    def test_invalid_json(self):
        """Test handling invalid JSON."""
        with self.assertRaises(ValueError):
            create_tools_from_json('{"invalid": "json"')
    
    def test_missing_name(self):
        """Test handling a tool definition without a name."""
        invalid_tool = {
            "description": "Invalid tool",
            "parameters": {}
        }
        
        with self.assertRaises(ValueError):
            JsonTool.from_json(invalid_tool)
            
if __name__ == "__main__":
    unittest.main()