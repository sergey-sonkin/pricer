#!/usr/bin/env python3
"""
Quick test to make sure our uv setup is working correctly
"""


def test_imports():
    """Test that all required packages can be imported"""
    import importlib.util

    packages = [
        ("google.cloud.vision", "google-cloud-vision"),
        ("PIL", "pillow"),
        ("requests", "requests"),
        ("bs4", "beautifulsoup4"),
        ("dotenv", "python-dotenv"),
    ]

    for module_name, package_name in packages:
        if importlib.util.find_spec(module_name) is not None:
            print(f"✅ {package_name} imported successfully")
        else:
            print(f"❌ {package_name} import failed")
            return False

    return True


def test_script_structure():
    """Test that our script files exist and are structured correctly"""
    import os

    files_to_check = ["scripts/image_analyzer.py", "pyproject.toml", ".env.example"]

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
