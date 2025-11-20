"""
Test script to verify Soulnote installation
"""

import sys
import importlib

def test_imports():
    """Test if all required packages can be imported"""
    print("Testing Soulnote Installation...")
    print("=" * 50)
    
    required_packages = [
        ('flask', 'Flask'),
        ('flask_cors', 'Flask-CORS'),
        ('requests', 'Requests'),
        ('speech_recognition', 'SpeechRecognition'),
        ('librosa', 'Librosa'),
        ('numpy', 'NumPy'),
        ('PIL', 'Pillow'),
        ('matplotlib', 'Matplotlib'),
        ('pydub', 'PyDub'),
    ]
    
    all_passed = True
    
    for package_name, display_name in required_packages:
        try:
            importlib.import_module(package_name)
            print(f"✓ {display_name:20s} - OK")
        except ImportError as e:
            print(f"✗ {display_name:20s} - FAILED")
            print(f"  Error: {e}")
            all_passed = False
    
    print("=" * 50)
    
    if all_passed:
        print("✓ All packages installed successfully!")
        print("\nNext steps:")
        print("1. Start LM Studio and load a model")
        print("2. Start the local server in LM Studio (port 1234)")
        print("3. Run: python backend/app.py")
        print("4. Open frontend/index.html in your browser")
        return True
    else:
        print("✗ Some packages failed to install")
        print("\nTry running: pip install -r requirements.txt")
        return False


def test_lmstudio_connection():
    """Test connection to LM Studio"""
    print("\n" + "=" * 50)
    print("Testing LM Studio Connection...")
    print("=" * 50)
    
    try:
        import requests
        response = requests.get("http://localhost:1234/v1/models", timeout=2)
        if response.status_code == 200:
            print("✓ LM Studio is running and accessible")
            print(f"  Response: {response.json()}")
            return True
        else:
            print(f"✗ LM Studio returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to LM Studio")
        print("  Make sure LM Studio is running with the local server started")
        print("  Expected URL: http://localhost:1234")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_directories():
    """Test if required directories exist"""
    print("\n" + "=" * 50)
    print("Testing Directory Structure...")
    print("=" * 50)
    
    from pathlib import Path
    
    required_dirs = [
        'backend',
        'models',
        'utils',
        'frontend',
        'static/css',
        'static/js',
        'uploads',
        'output',
    ]
    
    all_exist = True
    base_path = Path(__file__).parent
    
    for dir_name in required_dirs:
        dir_path = base_path / dir_name
        if dir_path.exists():
            print(f"✓ {dir_name:20s} - Exists")
        else:
            print(f"✗ {dir_name:20s} - Missing")
            all_exist = False
    
    print("=" * 50)
    
    if all_exist:
        print("✓ All directories present")
    else:
        print("✗ Some directories are missing")
    
    return all_exist


if __name__ == "__main__":
    print("\n")
    print("╔════════════════════════════════════════════════╗")
    print("║      Soulnote Installation Test Script        ║")
    print("╚════════════════════════════════════════════════╝")
    print("\n")
    
    # Test imports
    imports_ok = test_imports()
    
    # Test directories
    dirs_ok = test_directories()
    
    # Test LM Studio connection
    lmstudio_ok = test_lmstudio_connection()
    
    # Final summary
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    print(f"Package Installation: {'✓ PASS' if imports_ok else '✗ FAIL'}")
    print(f"Directory Structure:  {'✓ PASS' if dirs_ok else '✗ FAIL'}")
    print(f"LM Studio Connection: {'✓ PASS' if lmstudio_ok else '⚠ NOT RUNNING'}")
    print("=" * 50)
    
    if imports_ok and dirs_ok:
        print("\n✓ Soulnote is ready to use!")
        if not lmstudio_ok:
            print("⚠ Remember to start LM Studio before using the app")
        sys.exit(0)
    else:
        print("\n✗ Please fix the issues above before continuing")
        sys.exit(1)
