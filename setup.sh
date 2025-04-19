#!/bin/bash
# Ratlab Setup Script
# This script sets up the Ratlab environment with all necessary dependencies

# Terminal colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Print header
echo -e "${BLUE}=================================${NC}"
echo -e "${BLUE}     Ratlab Setup Script        ${NC}"
echo -e "${BLUE}=================================${NC}"

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# Make scripts executable
echo -e "\n${GREEN}Making scripts executable...${NC}"
chmod +x codex
chmod +x tools/test_capabilities.py
chmod +x tools/docker_utils.py
chmod +x tools/install_dependencies.py

# Create symbolic link to make codex accessible from anywhere
echo -e "\n${GREEN}Creating symbolic link...${NC}"
if [ -f /usr/local/bin/codex ]; then
    echo "Removing existing symbolic link..."
    sudo rm /usr/local/bin/codex
fi

echo "Creating new symbolic link..."
sudo ln -s "$SCRIPT_DIR/codex" /usr/local/bin/codex
echo "Codex is now accessible from anywhere using the 'codex' command"

# Ensure virtual environment is set up
echo -e "\n${GREEN}Setting up virtual environment...${NC}"
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo -e "\n${GREEN}Installing Python requirements...${NC}"
pip install -r requirements.txt

# Set up browser automation tools
echo -e "\n${GREEN}Setting up browser automation tools...${NC}"
python -m playwright install

# Check for direnv
echo -e "\n${GREEN}Setting up automatic environment activation...${NC}"
if ! command -v direnv &> /dev/null; then
    echo "direnv not found. Installing..."
    brew install direnv
    
    # Add to shell config if not already there
    SHELL_CONFIG=""
    if [ -f "$HOME/.zshrc" ]; then
        SHELL_CONFIG="$HOME/.zshrc"
    elif [ -f "$HOME/.bashrc" ]; then
        SHELL_CONFIG="$HOME/.bashrc"
    fi
    
    if [ -n "$SHELL_CONFIG" ]; then
        if ! grep -q "direnv hook" "$SHELL_CONFIG"; then
            echo "Adding direnv hook to $SHELL_CONFIG"
            echo 'eval "$(direnv hook zsh)"' >> "$SHELL_CONFIG"
            echo "Please restart your terminal or run: source $SHELL_CONFIG"
        fi
    else
        echo -e "${RED}Could not find shell configuration file. Please add the following line to your shell config:${NC}"
        echo 'eval "$(direnv hook zsh)"'
    fi
else
    echo "direnv already installed"
fi

# Allow direnv
echo "Allowing direnv for this directory..."
direnv allow .

# Final instructions
echo -e "\n${GREEN}Setup complete!${NC}"
echo -e "\n${BLUE}=================================${NC}"
echo -e "${BLUE}     Ratlab is ready to use      ${NC}"
echo -e "${BLUE}=================================${NC}"
echo -e "\nTo use Codex, you can run:"
echo "  1. Just type 'codex' from anywhere"
echo "  2. Or navigate to this directory and run './codex'"
echo -e "\nTo test all capabilities, run:"
echo "  ./tools/test_capabilities.py"
echo -e "\nEnjoy your autonomous AI environment!"

# Deactivate virtual environment
deactivate
