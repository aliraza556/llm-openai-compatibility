from typing import Dict, Any, List, Optional, Callable, Union
import json
import requests
from functools import wraps
from agents import function_tool

class JsonTool:
    """
    A class to create function tools from JSON definitions.
    """
    
    @staticmethod
    def from_json(json_def: Dict[str, Any]) -> Callable:
        """
        Create a function tool from a JSON definition.
        
        The JSON definition should have the following structure:
        {
            "name": "tool_name",
            "description": "Tool description",
            "parameters": {
                "type": "object",
                "properties": {
                    "param1": {
                        "type": "string",
                        "description": "Parameter description"
                    },
                    ...
                },
                "required": ["param1", ...]
            },
            "callback_url": "https://api.example.com/tools/tool_name" (optional)
        }
        
        Args:
            json_def: JSON definition of the tool
            
        Returns:
            A function decorated with @function_tool
        """
        name = json_def.get("name")
        description = json_def.get("description", "")
        parameters = json_def.get("parameters", {})
        callback_url = json_def.get("callback_url")
        
        if not name:
            raise ValueError("Tool definition must include a 'name' field")
        
        @function_tool
        def dynamic_tool(**kwargs):
            """Dynamic tool created from JSON definition."""

            if callback_url:
                try:
                    response = requests.post(
                        callback_url,
                        json={"name": name, "parameters": kwargs}
                    )
                    response.raise_for_status()
                    return response.text
                except Exception as e:
                    return f"Error calling {name}: {str(e)}"
            else:
                params_str = ", ".join(f"{k}={v}" for k, v in kwargs.items())
                return f"Tool {name} called with parameters: {params_str}"
        
        dynamic_tool.__name__ = name
        dynamic_tool.__doc__ = description
        
        dynamic_tool.tool_schema = {
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": parameters
            }
        }
        
        return dynamic_tool

def create_tools_from_json(json_tools: Union[str, List[Dict[str, Any]]]) -> List[Callable]:
    """
    Create multiple function tools from JSON definitions.
    
    Args:
        json_tools: Either a JSON string or a list of tool definitions
        
    Returns:
        List of function tools
    """
    if isinstance(json_tools, str):
        try:
            tools_list = json.loads(json_tools)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON string")
    else:
        tools_list = json_tools
    
    if not isinstance(tools_list, list):
        tools_list = [tools_list]
    
    return [JsonTool.from_json(tool_def) for tool_def in tools_list]