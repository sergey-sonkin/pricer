"""
Agent Tools Package

Provides clean tool definitions for the pricing agent.
Each tool wraps specific functionality for use in the agent system.
"""

from .amazon_searcher import AMAZON_SEARCH_TOOL
from .base import ToolDefinition
from .ebay_researcher import EBAY_RESEARCHER_TOOL
from .file_system import LIST_FILES_TOOL, READ_FILE_TOOL
from .gemini_analyzer import GEMINI_ANALYZER_TOOL
from .openai_analyzer import OPENAI_ANALYZER_TOOL
from .vision_analyzer import VISION_ANALYZER_TOOL

# All available tools
ALL_TOOLS = [
    READ_FILE_TOOL,
    LIST_FILES_TOOL,
    GEMINI_ANALYZER_TOOL,
    OPENAI_ANALYZER_TOOL,
    VISION_ANALYZER_TOOL,
    EBAY_RESEARCHER_TOOL,
    AMAZON_SEARCH_TOOL,
]

__all__ = [
    "ToolDefinition",
    "READ_FILE_TOOL",
    "LIST_FILES_TOOL",
    "GEMINI_ANALYZER_TOOL",
    "OPENAI_ANALYZER_TOOL",
    "VISION_ANALYZER_TOOL",
    "EBAY_RESEARCHER_TOOL",
    "AMAZON_SEARCH_TOOL",
    "ALL_TOOLS",
]
