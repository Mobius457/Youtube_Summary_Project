#!/usr/bin/env python3
"""
Setup script for YouTube Summarizer development environment.

This script automates the setup process for new developers.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def run_command(command, check=True, shell=False):
    """Run a command and return the result."""
    try:
        if shell:
            result = subprocess.run(command, shell=True, check=check, capture_output=True, text=True)
        else:
            result = subprocess.run(command.split(), check=check, capture_output=True, text=True)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        print(f"Error: {e.stderr}")
        return None


def check_python_version():
    """Check if Python version is compatible."""
    print("🐍 Checking Python version...")
    
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required!")
        print(f"Current version: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True


def check_git():
    """Check if Git is installed."""
    print("📦 Checking Git installation...")
    
    result = run_command("git --version", check=False)
    if result is None or result.returncode != 0:
        print("❌ Git is not installed or not in PATH")
        return False
    
    print(f"✅ {result.stdout.strip()}")
    return True


def create_virtual_environment():
    """Create and activate virtual environment."""
    print("🔧 Creating virtual environment...")
    
    venv_path = Path("venv")
    if venv_path.exists():
        print("⚠️  Virtual environment already exists")
        response = input("Do you want to recreate it? (y/N): ").lower()
        if response == 'y':
            print("🗑️  Removing existing virtual environment...")
            shutil.rmtree(venv_path)
        else:
            print("✅ Using existing virtual environment")
            return True
    
    result = run_command("python -m venv venv")
    if result is None:
        print("❌ Failed to create virtual environment")
        return False
    
    print("✅ Virtual environment created")
    return True


def install_dependencies():
    """Install project dependencies."""
    print("📦 Installing dependencies...")
    
    # Determine pip path based on OS
    if os.name == 'nt':  # Windows
        pip_path = "venv\\Scripts\\pip"
        python_path = "venv\\Scripts\\python"
    else:  # Unix-like
        pip_path = "venv/bin/pip"
        python_path = "venv/bin/python"
    
    # Upgrade pip first
    print("⬆️  Upgrading pip...")
    result = run_command(f"{python_path} -m pip install --upgrade pip")
    if result is None:
        print("❌ Failed to upgrade pip")
        return False
    
    # Install development dependencies
    print("📚 Installing development dependencies...")
    result = run_command(f"{pip_path} install -r requirements/development.txt")
    if result is None:
        print("❌ Failed to install dependencies")
        return False
    
    print("✅ Dependencies installed")
    return True


def setup_environment_file():
    """Setup environment configuration file."""
    print("⚙️  Setting up environment configuration...")
    
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        print("⚠️  .env file already exists")
        response = input("Do you want to overwrite it? (y/N): ").lower()
        if response != 'y':
            print("✅ Using existing .env file")
            return True
    
    if not env_example.exists():
        print("❌ .env.example file not found")
        return False
    
    # Copy .env.example to .env
    shutil.copy(env_example, env_file)
    print("✅ .env file created from .env.example")
    
    # Prompt for YouTube API key
    print("\n🔑 Optional: YouTube API Key Setup")
    print("A YouTube API key improves performance but is not required.")
    print("You can get one from: https://console.cloud.google.com/")
    
    api_key = input("Enter your YouTube API key (or press Enter to skip): ").strip()
    if api_key:
        # Update .env file with API key
        with open(env_file, 'r') as f:
            content = f.read()
        
        content = content.replace('YOUTUBE_API_KEY=your-youtube-api-key-here', f'YOUTUBE_API_KEY={api_key}')
        
        with open(env_file, 'w') as f:
            f.write(content)
        
        print("✅ YouTube API key added to .env file")
    else:
        print("⏭️  Skipping YouTube API key setup")
    
    return True


def download_nltk_data():
    """Download required NLTK data."""
    print("📚 Downloading NLTK data...")
    
    # Determine python path based on OS
    if os.name == 'nt':  # Windows
        python_path = "venv\\Scripts\\python"
    else:  # Unix-like
        python_path = "venv/bin/python"
    
    nltk_script = '''
import nltk
import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

print("Downloading punkt...")
nltk.download('punkt', quiet=True)
print("Downloading stopwords...")
nltk.download('stopwords', quiet=True)
print("NLTK data downloaded successfully!")
'''
    
    result = run_command(f'{python_path} -c "{nltk_script}"', shell=True)
    if result is None:
        print("❌ Failed to download NLTK data")
        return False
    
    print("✅ NLTK data downloaded")
    return True


def create_cache_directory():
    """Create cache directory."""
    print("📁 Creating cache directory...")
    
    cache_dir = Path("cache")
    if not cache_dir.exists():
        cache_dir.mkdir()
        print("✅ Cache directory created")
    else:
        print("✅ Cache directory already exists")
    
    return True


def run_tests():
    """Run tests to verify setup."""
    print("🧪 Running tests to verify setup...")
    
    # Determine python path based on OS
    if os.name == 'nt':  # Windows
        python_path = "venv\\Scripts\\python"
    else:  # Unix-like
        python_path = "venv/bin/python"
    
    result = run_command(f"{python_path} -m pytest tests/ -v --tb=short", check=False)
    if result is None or result.returncode != 0:
        print("⚠️  Some tests failed, but setup is complete")
        print("You can run tests manually later with: pytest")
        return True
    
    print("✅ All tests passed")
    return True


def print_next_steps():
    """Print next steps for the user."""
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Activate the virtual environment:")
    
    if os.name == 'nt':  # Windows
        print("   venv\\Scripts\\activate")
    else:  # Unix-like
        print("   source venv/bin/activate")
    
    print("\n2. Start the development server:")
    print("   python run.py")
    
    print("\n3. Open your browser and go to:")
    print("   http://localhost:5000")
    
    print("\n4. Optional: Configure your YouTube API key in .env file")
    
    print("\n📚 Documentation:")
    print("   - README: docs/README.md")
    print("   - API docs: docs/API.md")
    print("   - Deployment: docs/DEPLOYMENT.md")
    
    print("\n🧪 Run tests:")
    print("   pytest")
    
    print("\n🎯 Happy coding!")


def main():
    """Main setup function."""
    print("🚀 YouTube Summarizer Development Setup")
    print("=" * 50)
    
    # Check prerequisites
    if not check_python_version():
        sys.exit(1)
    
    if not check_git():
        print("⚠️  Git is recommended but not required for setup")
    
    # Setup steps
    steps = [
        ("Create virtual environment", create_virtual_environment),
        ("Install dependencies", install_dependencies),
        ("Setup environment file", setup_environment_file),
        ("Download NLTK data", download_nltk_data),
        ("Create cache directory", create_cache_directory),
        ("Run tests", run_tests),
    ]
    
    for step_name, step_func in steps:
        print(f"\n📋 {step_name}...")
        if not step_func():
            print(f"❌ Failed: {step_name}")
            print("Setup incomplete. Please check the errors above.")
            sys.exit(1)
    
    print_next_steps()


if __name__ == "__main__":
    main()
