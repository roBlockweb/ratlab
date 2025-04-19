#!/bin/bash
# Script to commit and push changes to GitHub

echo "Committing changes to GitHub..."

# Ensure we're in the right directory
cd /Users/rohan/gits/ratlab

# Add all changes
git add .

# Commit with the message
git commit -m "RatLab v0.1 - Self-optimized AI development environment" -m "
- Enhanced interactive mode with multi-line input support
- Improved error handling throughout the codebase
- Added better formatting for AI responses and tool results
- Fixed issues with terminal output display
- Updated documentation with clearer usage instructions
"

# Push to GitHub
git push origin main

echo "Changes successfully committed and pushed to GitHub!"
