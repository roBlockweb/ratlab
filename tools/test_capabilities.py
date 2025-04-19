#!/usr/bin/env python3
"""
Test the capabilities of Codex by executing a series of commands
"""
import os
import sys
import json
import subprocess
import importlib.util
from pathlib import Path

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

try:
    from tools.docker_utils import list_all_services
except ImportError:
    print("Warning: Docker utilities not found.")
    list_all_services = None

def print_header(message):
    """Print a formatted header"""
    print("\n" + "="*70)
    print(f" {message}")
    print("="*70)

def run_command(command):
    """Run a shell command and return result"""
    print(f"\n> {command}")
    try:
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        if e.stderr:
            print(e.stderr)
        return False

def check_python():
    """Check Python environment"""
    print_header("CHECKING PYTHON ENVIRONMENT")
    run_command("python --version")
    run_command("pip list | grep -E 'openai|requests|beautifulsoup4|playwright|huggingface|langchain'")

def check_node():
    """Check Node.js environment"""
    print_header("CHECKING NODE.JS ENVIRONMENT")
    run_command("node --version")
    run_command("npm --version")

def check_browser_tools():
    """Check browser automation tools"""
    print_header("CHECKING BROWSER AUTOMATION TOOLS")
    
    # Check for Playwright
    try:
        spec = importlib.util.find_spec("playwright")
        if spec is not None:
            print("✓ Playwright is installed")
            # Try to get browser info
            run_command("python -m playwright --version")
        else:
            print("✗ Playwright is not installed")
    except ImportError:
        print("✗ Playwright is not installed")
    
    # Check for Selenium
    try:
        spec = importlib.util.find_spec("selenium")
        if spec is not None:
            print("✓ Selenium is installed")
        else:
            print("✗ Selenium is not installed")
    except ImportError:
        print("✗ Selenium is not installed")

def check_docker():
    """Check Docker environment"""
    print_header("CHECKING DOCKER ENVIRONMENT")
    
    # Check Docker installation
    docker_installed = run_command("docker --version")
    
    if docker_installed and list_all_services:
        # List running services
        print("\nRunning Docker services:")
        services = list_all_services()
        if services["status"] == "success":
            for service in services["services"]:
                print(f"  - {service['name']} ({service['status']})")
                if service['urls']:
                    print(f"    URLs: {', '.join(service['urls'])}")

def check_git():
    """Check Git installation"""
    print_header("CHECKING GIT ENVIRONMENT")
    run_command("git --version")
    run_command("git config --get user.name")
    run_command("git config --get user.email")

def check_file_structure():
    """Check the file structure"""
    print_header("CHECKING FILE STRUCTURE")
    
    ratlab_dir = parent_dir
    
    # Check for key files
    required_files = [
        "codex.py",
        "codex",
        ".env",
        "requirements.txt",
        "config/system_prompt.txt",
        "tools/docker_utils.py",
        "tools/install_dependencies.py"
    ]
    
    print("Checking for required files:")
    for file_path in required_files:
        full_path = os.path.join(ratlab_dir, file_path)
        if os.path.exists(full_path):
            print(f"  ✓ {file_path}")
        else:
            print(f"  ✗ {file_path} (missing)")

def check_openai_api():
    """Check OpenAI API key"""
    print_header("CHECKING OPENAI API KEY")
    
    env_path = os.path.join(parent_dir, ".env")
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            content = f.read()
        
        if "OPENAI_API_KEY" in content:
            print("✓ OPENAI_API_KEY found in .env file")
            
            # Test API key validity
            print("\nTesting API connection...")
            run_command("python -c \"import openai; openai.api_key = '$(grep OPENAI_API_KEY .env | cut -d= -f2)'; print(openai.models.list())\"")
        else:
            print("✗ OPENAI_API_KEY not found in .env file")
    else:
        print("✗ .env file not found")

def main():
    """Run all checks"""
    print_header("CODEX CAPABILITY TEST")
    print("Running tests to ensure Codex has all necessary capabilities...")
    
    check_python()
    check_node()
    check_browser_tools()
    check_docker()
    check_git()
    check_file_structure()
    check_openai_api()
    
    print_header("TEST COMPLETE")
    print("""
To start using Codex:
1. Navigate to the ratlab directory: cd /Users/rohan/gits/ratlab
2. Run the Codex assistant: ./codex

You can also set up direnv to automatically activate the environment:
1. Install direnv: brew install direnv
2. Add this to your shell configuration: eval "$(direnv hook zsh)"
3. Allow the directory: direnv allow /Users/rohan/gits/ratlab
    """)

if __name__ == "__main__":
    main()
