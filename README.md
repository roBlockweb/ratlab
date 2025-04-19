# RatLab - Autonomous AI Development Environment

RatLab is an enhanced environment that grants OpenAI models full access to your development tools and system capabilities. This enables AI to autonomously perform a wide range of tasks with minimal human intervention.

## Features

- 🧠 **Fully Autonomous Operation**: AI can perform complex tasks without constant human guidance
- 💻 **Complete System Access**: Execute shell commands, manipulate files, and control applications
- 🌐 **Web Capabilities**: Browse websites, fetch content, and interact with web services
- 🔧 **Dev Tool Integration**: Seamless integration with VS Code, Git, and other development tools
- 🐳 **Docker Control**: Manage containers and interact with containerized services
- 📦 **Package Management**: Install and update packages across multiple package managers
- 🤗 **AI Model Access**: Integrate with Hugging Face models for specialized tasks
- 🔍 **Web Browsing Automation**: Control browsers programmatically with Playwright/Selenium
- 📊 **Data Processing**: Process and visualize data from various sources

## Quick Start

1. Run the setup script to configure everything:
   ```
   cd /Users/rohan/gits/ratlab
   chmod +x setup.sh
   ./setup.sh
   ```

2. Start Codex:
   ```
   codex
   ```

3. Using the interactive mode:
   - Type your requests after the `Codex>` prompt
   - For multi-line input, enter your full request and end with `##` on a new line
   - Type `help` to see available commands
   - Type `examples` to see example requests
   - Type `exit` or `quit` to exit

## System Requirements

- macOS with Homebrew installed
- Python 3.8+
- OpenAI API key
- Git
- Node.js (optional, installed automatically if needed)
- Docker (optional, for container-related features)

## Directory Structure

- `codex.py` - Main AI assistant implementation
- `codex` - Shell script to launch the assistant
- `config/` - Configuration files including system prompts
- `tools/` - Utility scripts and tools
- `src/` - Directory for source code projects
- `data/` - Directory for data files
- `logs/` - Directory for log files

## Available Tools

The AI has access to these integrated tools:

- **file_operations**: Read, write, list, copy, and delete files
- **shell_command**: Execute shell commands
- **search_docs**: Search documentation
- **code_completion**: Complete code snippets using OpenAI
- **web_browse**: Browse the web and fetch content
- **code_generation**: Generate code from descriptions
- **vscode**: Open VS Code
- **github**: Perform GitHub operations
- **huggingface**: Interact with Hugging Face models
- **docker**: Manage Docker containers
- **install_package**: Install software packages
- **open_service**: Open web services in your browser
- **list_services**: List all available Docker services

## Example Prompts

Try asking Codex:

- "Create a simple Flask web server in src/app.py"
- "Clone the repository https://github.com/openai/whisper.git"
- "Open the Open WebUI interface in my browser"
- "Generate a Python script that creates a REST API for user management"
- "Set up a React project with TypeScript in the src directory"
- "Search for information about large language models"
- "Check if Docker is running properly and list all containers"

## Customization

You can customize the system prompt by editing:
```
/Users/rohan/gits/ratlab/config/system_prompt.txt
```

## Troubleshooting

If you encounter issues:

1. Run the test capabilities script:
   ```
   ./tools/test_capabilities.py
   ```

2. Ensure your OpenAI API key is valid in the `.env` file

3. Check that all dependencies are installed:
   ```
   source venv/bin/activate
   pip install -r requirements.txt
   ```

## License

MIT

---

Developed as an exploration of AI capabilities and autonomy.
