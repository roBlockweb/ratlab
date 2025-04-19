#!/usr/bin/env python3
"""
Dependency installer for Codex environment
This script installs all required dependencies for the Codex assistant
"""
import subprocess
import sys
import os
import platform
from pathlib import Path

def print_status(message):
    """Print a formatted status message"""
    print(f"\n{'='*60}\n{message}\n{'='*60}")

def run_command(command, check=True):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(command, shell=True, check=check, text=True, capture_output=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        if e.stderr:
            print(e.stderr)
        return False

def install_package(package_manager, package):
    """Install a package using the specified package manager"""
    managers = {
        'pip': 'pip install',
        'npm': 'npm install -g',
        'brew': 'brew install',
        'gem': 'gem install',
    }
    
    if package_manager not in managers:
        print(f"Unknown package manager: {package_manager}")
        return False
    
    cmd = f"{managers[package_manager]} {package}"
    print(f"Running: {cmd}")
    return run_command(cmd)

def ensure_python_packages():
    """Install required Python packages"""
    print_status("Installing Python packages")
    
    # Get the directory of this script
    script_dir = Path(__file__).parent.parent
    requirements_file = script_dir / "requirements.txt"
    
    if requirements_file.exists():
        print(f"Installing packages from {requirements_file}")
        return run_command(f"pip install -r {requirements_file}")
    else:
        print("requirements.txt not found, installing essential packages")
        packages = [
            "openai",
            "python-dotenv",
            "requests",
            "beautifulsoup4",
            "huggingface_hub",
            "playwright",
            "selenium",
            "rich"
        ]
        
        success = True
        for package in packages:
            if not install_package('pip', package):
                success = False
        
        return success

def setup_browser_automation():
    """Set up browser automation tools"""
    print_status("Setting up browser automation")
    
    # Install Playwright browsers
    print("Installing Playwright browsers")
    run_command("playwright install")
    
    # Install WebDriver for Selenium
    print("Setting up WebDriver for Selenium")
    if platform.system() == "Darwin":  # macOS
        run_command("brew install --cask chromedriver", check=False)
    elif platform.system() == "Linux":
        run_command("CHROMEDRIVER_VERSION=$(curl -s https://chromedriver.storage.googleapis.com/LATEST_RELEASE) && " +
                   "wget -q -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip && " +
                   "unzip /tmp/chromedriver.zip -d /tmp && " +
                   "sudo mv /tmp/chromedriver /usr/local/bin/chromedriver && " +
                   "sudo chmod +x /usr/local/bin/chromedriver", check=False)
    
    return True

def setup_node_environment():
    """Set up Node.js environment and tools"""
    print_status("Setting up Node.js environment")
    
    # Check if Node.js is installed
    node_installed = run_command("node --version", check=False)
    
    if not node_installed:
        if platform.system() == "Darwin":  # macOS
            print("Installing Node.js using Homebrew")
            run_command("brew install node")
        else:
            print("Please install Node.js manually: https://nodejs.org/")
            return False
    
    # Install useful Node.js packages
    node_packages = [
        "http-server",
        "typescript",
        "eslint",
        "prettier"
    ]
    
    success = True
    for package in node_packages:
        if not install_package('npm', package):
            success = False
    
    return success

def setup_git_environment():
    """Set up Git environment and configuration"""
    print_status("Setting up Git environment")
    
    # Check if Git is installed
    git_installed = run_command("git --version", check=False)
    
    if not git_installed:
        if platform.system() == "Darwin":  # macOS
            print("Installing Git using Homebrew")
            run_command("brew install git")
        else:
            print("Please install Git manually: https://git-scm.com/")
            return False
    
    # Configure Git if not already configured
    name_configured = run_command("git config --global user.name", check=False)
    email_configured = run_command("git config --global user.email", check=False)
    
    if not name_configured or not email_configured:
        print("\nGit is not fully configured. Please run:")
        print("git config --global user.name \"Your Name\"")
        print("git config --global user.email \"your.email@example.com\"")
    
    return True

def install_extra_cli_tools():
    """Install extra CLI tools that might be useful"""
    print_status("Installing extra CLI tools")
    
    if platform.system() == "Darwin":  # macOS
        brew_packages = [
            "jq",        # JSON processor
            "fzf",       # Fuzzy finder
            "wget",      # File downloader
            "httpie",    # HTTP client
            "ripgrep"    # Fast grep
        ]
        
        for package in brew_packages:
            install_package('brew', package)
    else:
        print("Please install extra tools manually as needed.")
    
    return True

def main():
    """Main function to install all dependencies"""
    print_status("Starting Codex dependency installation")
    
    # Ensure Python packages
    if not ensure_python_packages():
        print("Failed to install Python packages")
    
    # Set up browser automation
    if not setup_browser_automation():
        print("Failed to set up browser automation")
    
    # Set up Node.js environment
    if not setup_node_environment():
        print("Failed to set up Node.js environment")
    
    # Set up Git environment
    if not setup_git_environment():
        print("Failed to set up Git environment")
    
    # Install extra CLI tools
    if not install_extra_cli_tools():
        print("Failed to install extra CLI tools")
    
    print_status("Dependency installation complete!")
    print("You can now run Codex with: python codex.py")

if __name__ == "__main__":
    main()
