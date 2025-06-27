#!/usr/bin/env python3
"""
Quick test to make sure our uv setup is working correctly
"""

def test_imports():
    """Test that all required packages can be imported"""
    try:
        from google.cloud import vision
        print("✅ google-cloud-vision imported successfully")
    except ImportError as e:
        print(f"❌ google-cloud-vision import failed: {e}")
        return False

    try:
        from PIL import Image
        print("✅ pillow imported successfully")
    except ImportError as e:
        print(f"❌ pillow import failed: {e}")
        return False

    try:
        import requests
        print("✅ requests imported successfully")
    except ImportError as e:
        print(f"❌ requests import failed: {e}")
        return False

    try:
        from bs4 import BeautifulSoup
        print("✅ beautifulsoup4 imported successfully")
    except ImportError as e:
        print(f"❌ beautifulsoup4 import failed: {e}")
        return False

    try:
        from dotenv import load_dotenv
        print("✅ python-dotenv imported successfully")
    except ImportError as e:
        print(f"❌ python-dotenv import failed: {e}")
        return False

    return True

def test_script_structure():
    """Test that our script files exist and are structured correctly"""
    import os
    
    files_to_check = [
        'scripts/image_analyzer.py',
        'pyproject.toml',
        '.env.example'
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} missing")
            return False
    
    return True

def main():
    print("🧪 Testing PickPrice setup...")
    print("=" * 40)
    
    imports_ok = test_imports()
    structure_ok = test_script_structure()
    
    print("=" * 40)
    if imports_ok and structure_ok:
        print("🎉 All tests passed! Setup looks good.")
        print("Next steps:")
        print("1. Set up Google Vision API credentials")
        print("2. Test with: python scripts/image_analyzer.py path/to/image.jpg")
    else:
        print("❌ Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main()