#!/usr/bin/env python3
"""
Test script to verify the Vision tool works with the agent
"""

import os
import sys

# Add tools directory to path
sys.path.append(os.path.join(os.path.dirname(__file__)))
from tools import ALL_TOOLS


def test_vision_tool():
    """Test the Vision tool integration"""
    print("Testing Vision tool with agent...")

    # Check if Vision tool is available
    vision_tool = None
    for tool in ALL_TOOLS:
        if tool.name == "analyze_image_with_vision":
            vision_tool = tool
            break

    if vision_tool is None:
        print("❌ Vision tool not found in ALL_TOOLS")
        return False

    print(f"✅ Vision tool found: {vision_tool.name}")
    print(f"Description: {vision_tool.description}")

    # Test the tool function directly
    try:
        result = vision_tool.function({"image_path": "examples/cat.jpeg"})
        print("✅ Tool function executed successfully")
        print(f"Result preview: {result[:100]}...")
        return True
    except Exception as e:
        print(f"❌ Tool function failed: {e}")
        return False


if __name__ == "__main__":
    success = test_vision_tool()
    if success:
        print("\n🎉 Vision tool integration test passed!")
    else:
        print("\n❌ Vision tool integration test failed!")
        sys.exit(1)
