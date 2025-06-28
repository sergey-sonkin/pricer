"""
File System Tools for Agent

Provides basic file system operations like reading files and listing directories.
"""

import os
from typing import Any

from .base import ToolDefinition


def read_file(input_data: dict[str, Any]) -> str:
    """
    Read the contents of a file
    
    Args:
        input_data: Dictionary containing 'path' key
        
    Returns:
        File contents as a string
        
    Raises:
        Exception: If file cannot be read
    """
    path = input_data["path"]
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        raise Exception(f"Error reading file: {str(e)}")


def list_files(input_data: dict[str, Any]) -> str:
    """
    List files and directories in a path
    
    Args:
        input_data: Dictionary with optional 'path' key (defaults to current directory)
        
    Returns:
        Newline-separated list of files and directories
        
    Raises:
        Exception: If directory cannot be listed
    """
    path = input_data.get("path", ".")
    try:
        files = os.listdir(path)
        return "\n".join(files)
    except Exception as e:
        raise Exception(f"Error listing files: {str(e)}")


# Tool definitions
READ_FILE_TOOL = ToolDefinition(
    name="read_file",
    description="Read the contents of a given relative file path. Use this when you want to see what's inside a file. Do not use this with directory names.",
    input_schema={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "The relative path of a file in the working directory.",
            }
        },
        "required": ["path"],
    },
    function=read_file,
)

LIST_FILES_TOOL = ToolDefinition(
    name="list_files",
    description="List files and directories at a given path. If no path is provided, lists files in the current directory.",
    input_schema={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Optional relative path to list files from. Defaults to current directory if not provided.",
            }
        },
        "required": [],
    },
    function=list_files,
)