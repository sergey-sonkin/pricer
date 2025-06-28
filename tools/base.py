"""
Base classes and types for agent tools

Defines the common ToolDefinition structure used by all tools.
"""

from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class ToolDefinition:
    """Definition of a tool that can be used by the agent"""
    name: str
    description: str
    input_schema: dict[str, Any]
    function: Callable[[dict[str, Any]], str]