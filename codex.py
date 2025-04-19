#!/usr/bin/env python3
"""
Codex - An AI assistant with extended capabilities
"""
import os
import sys
import json
import time
import argparse
import subprocess
import webbrowser
import traceback
from pathlib import Path
import openai
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import shutil
import re
import threading
import importlib

# Import local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from tools.docker_utils import list_all_services, open_web_service, open_webui_ui, open_flowise
except ImportError:
    print("Warning: Docker utilities not found. Some features may be limited.")

# Load environment variables
load_dotenv()

# Set system prompt path
SYSTEM_PROMPT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config', 'system_prompt.txt')

# Configure OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    print("Error: OPENAI_API_KEY not found in environment variables.")
    sys.exit(1)

class Codex:
    def __init__(self):
        self.tools = {
            "file_operations": self.file_operations,
            "shell_command": self.shell_command,
            "search_docs": self.search_docs,
            "code_completion": self.code_completion,
            "web_browse": self.web_browse,
            "code_generation": self.code_generation,
            "vscode": self.vscode,
            "github": self.github_operations,
            "huggingface": self.huggingface_operations,
            "docker": self.docker_operations,
            "install_package": self.install_package,
            "open_service": self.open_service,
            "list_services": self.list_services,
        }
        
        # Initialize workspace
        self.workspace_path = os.path.dirname(os.path.abspath(__file__))
        self.ensure_directories()
        self.welcome_message()
        
        # Load system prompt if available
        self.system_prompt = self.load_system_prompt()
    
    def welcome_message(self):
        """Display welcome message"""
        print("\n" + "="*60)
        print("✨ Welcome to Codex - Your AI-powered Development Environment ✨")
        print("="*60)
        print("🔧 Available tools:")
        for tool in self.tools:
            print(f"  • {tool}")
        print("\n💡 Type 'help' for assistance or 'exit' to quit")
        print("="*60 + "\n")
    
    def load_system_prompt(self):
        """Load system prompt from file"""
        try:
            if os.path.exists(SYSTEM_PROMPT_PATH):
                with open(SYSTEM_PROMPT_PATH, 'r') as f:
                    return f.read()
            else:
                print(f"System prompt not found at {SYSTEM_PROMPT_PATH}")
                return "You are Codex, an AI assistant with the ability to help with coding and technical tasks. You have access to various tools to assist the user."
        except Exception as e:
            print(f"Error loading system prompt: {e}")
            return "You are Codex, an AI assistant with the ability to help with coding and technical tasks. You have access to various tools to assist the user."
    
    def ensure_directories(self):
        """Ensure all necessary directories exist"""
        for directory in ["src", "data", "logs", "tools", "config"]:
            os.makedirs(os.path.join(self.workspace_path, directory), exist_ok=True)
    
    def shell_command(self, command):
        """Execute a shell command and return the output"""
        try:
            result = subprocess.run(command, shell=True, check=True, 
                                  text=True, capture_output=True)
            return {"status": "success", "stdout": result.stdout, "stderr": result.stderr}
        except subprocess.CalledProcessError as e:
            return {"status": "error", "stdout": e.stdout, "stderr": e.stderr, "code": e.returncode}
    
    def file_operations(self, operation, path, content=None):
        """Perform file operations like read, write, list"""
        path_obj = Path(path)
        
        if operation == "read":
            try:
                return {"status": "success", "content": path_obj.read_text()}
            except Exception as e:
                return {"status": "error", "message": str(e)}
        
        elif operation == "write":
            try:
                # Create parent directories if they don't exist
                path_obj.parent.mkdir(parents=True, exist_ok=True)
                path_obj.write_text(content)
                return {"status": "success"}
            except Exception as e:
                return {"status": "error", "message": str(e)}
        
        elif operation == "list":
            try:
                files = [str(p) for p in Path(path).iterdir()]
                return {"status": "success", "files": files}
            except Exception as e:
                return {"status": "error", "message": str(e)}
                
        elif operation == "copy":
            try:
                shutil.copy2(path, content)  # content is the destination path
                return {"status": "success"}
            except Exception as e:
                return {"status": "error", "message": str(e)}
                
        elif operation == "delete":
            try:
                if path_obj.is_file():
                    path_obj.unlink()
                elif path_obj.is_dir():
                    shutil.rmtree(path_obj)
                return {"status": "success"}
            except Exception as e:
                return {"status": "error", "message": str(e)}
        
        return {"status": "error", "message": "Unknown operation"}
    
    def search_docs(self, query):
        """Search documentation"""
        try:
            # Implementation could be enhanced with local doc search or web search
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            # Open a browser with the search results
            webbrowser.open(search_url)
            return {"status": "success", "message": f"Opened search results for: {query}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def code_completion(self, code, language="python"):
        """Get code completion using OpenAI API"""
        try:
            response = openai.chat.completions.create(
                model="gpt-4", 
                messages=[
                    {"role": "system", "content": f"You are an expert {language} programmer. Complete the following code."},
                    {"role": "user", "content": code}
                ]
            )
            return {"status": "success", "completion": response.choices[0].message.content}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def code_generation(self, description, language="python", file_path=None):
        """Generate code from description"""
        try:
            response = openai.chat.completions.create(
                model="gpt-4", 
                messages=[
                    {"role": "system", "content": f"You are an expert {language} programmer. Write complete, working code based on the following description. Include detailed comments."},
                    {"role": "user", "content": description}
                ]
            )
            
            code = response.choices[0].message.content
            
            # Extract code if wrapped in markdown code blocks
            if "```" in code:
                pattern = r"```(?:\w+)?\n([\s\S]*?)\n```"
                matches = re.findall(pattern, code)
                if matches:
                    code = "\n".join(matches)
            
            # Save to file if path is provided
            if file_path:
                Path(file_path).write_text(code)
                return {"status": "success", "code": code, "message": f"Code saved to {file_path}"}
            else:
                return {"status": "success", "code": code}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def web_browse(self, url, action="open"):
        """Browse the web - open URLs, fetch page content"""
        try:
            if action == "open":
                webbrowser.open(url)
                return {"status": "success", "message": f"Opened {url} in browser"}
            elif action == "fetch":
                headers = {
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
                }
                response = requests.get(url, headers=headers)
                soup = BeautifulSoup(response.text, "html.parser")
                
                # Extract text content
                text = soup.get_text(separator="\n", strip=True)
                
                # Limit response size to avoid overwhelming the AI
                max_length = 5000
                if len(text) > max_length:
                    text = text[:max_length] + "... [content truncated]"
                
                return {"status": "success", "content": text, "title": soup.title.string if soup.title else ""}
            else:
                return {"status": "error", "message": "Unknown action"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def vscode(self, path=None, new_window=False):
        """Open VS Code with the specified path"""
        try:
            command = ["code"]
            
            if new_window:
                command.append("--new-window")
                
            if path:
                # Ensure path exists
                path_obj = Path(path)
                if not path_obj.exists():
                    return {"status": "error", "message": f"Path does not exist: {path}"}
                command.append(str(path_obj))
            else:
                # Default to workspace directory
                command.append(self.workspace_path)
            
            subprocess.run(command, check=True)
            return {"status": "success", "message": f"Opened VS Code with path: {path or self.workspace_path}"}
        except FileNotFoundError:
            return {"status": "error", "message": "VS Code command line tools not found. Try installing: brew install --cask visual-studio-code"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def github_operations(self, action, repo_path=None, remote_url=None, branch=None, commit_message=None):
        """Perform GitHub operations"""
        try:
            if action == "init":
                # Initialize a new git repository
                result = subprocess.run(["git", "init"], cwd=repo_path or self.workspace_path, 
                                      capture_output=True, text=True, check=True)
                return {"status": "success", "message": f"Initialized git repository: {result.stdout}"}
                
            elif action == "clone":
                # Clone a repository
                if not remote_url:
                    return {"status": "error", "message": "Remote URL is required for clone action"}
                
                result = subprocess.run(["git", "clone", remote_url, repo_path or "."], 
                                      capture_output=True, text=True, check=True)
                return {"status": "success", "message": f"Cloned repository: {result.stdout}"}
                
            elif action == "add":
                # Add files to git
                result = subprocess.run(["git", "add", "."], cwd=repo_path or self.workspace_path, 
                                      capture_output=True, text=True, check=True)
                return {"status": "success", "message": "Added files to git staging"}
                
            elif action == "commit":
                # Commit changes
                if not commit_message:
                    return {"status": "error", "message": "Commit message is required"}
                
                result = subprocess.run(["git", "commit", "-m", commit_message], 
                                      cwd=repo_path or self.workspace_path, 
                                      capture_output=True, text=True, check=True)
                return {"status": "success", "message": f"Committed changes: {result.stdout}"}
                
            elif action == "push":
                # Push changes
                cmd = ["git", "push"]
                if remote_url:
                    cmd.append(remote_url)
                if branch:
                    cmd.append(branch)
                
                result = subprocess.run(cmd, cwd=repo_path or self.workspace_path, 
                                      capture_output=True, text=True, check=True)
                return {"status": "success", "message": f"Pushed changes: {result.stdout}"}
                
            elif action == "pull":
                # Pull changes
                cmd = ["git", "pull"]
                if remote_url:
                    cmd.append(remote_url)
                if branch:
                    cmd.append(branch)
                
                result = subprocess.run(cmd, cwd=repo_path or self.workspace_path, 
                                      capture_output=True, text=True, check=True)
                return {"status": "success", "message": f"Pulled changes: {result.stdout}"}
                
            elif action == "status":
                # Check status
                result = subprocess.run(["git", "status"], cwd=repo_path or self.workspace_path, 
                                      capture_output=True, text=True, check=True)
                return {"status": "success", "output": result.stdout}
                
            else:
                return {"status": "error", "message": f"Unknown git action: {action}"}
        except subprocess.CalledProcessError as e:
            return {"status": "error", "message": f"Git error: {e.stderr}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def huggingface_operations(self, action, model_id=None, task=None, inputs=None):
        """Interact with Hugging Face Hub"""
        try:
            # Dynamically import huggingface_hub
            try:
                from huggingface_hub import HfApi, hf_hub_download, snapshot_download
                from huggingface_hub import InferenceClient
            except ImportError:
                return {"status": "error", "message": "huggingface_hub not installed. Install with: pip install huggingface_hub"}
            
            if action == "search":
                # Search for models
                api = HfApi()
                models = api.list_models(filter=task, search=model_id, limit=5)
                return {"status": "success", "models": [m.id for m in models]}
                
            elif action == "download":
                # Download a model
                if not model_id:
                    return {"status": "error", "message": "Model ID is required for download action"}
                
                download_path = os.path.join(self.workspace_path, "models", model_id.replace("/", "_"))
                os.makedirs(download_path, exist_ok=True)
                
                result = snapshot_download(repo_id=model_id, local_dir=download_path)
                return {"status": "success", "path": result}
            
            elif action == "inference":
                # Run inference on a model
                if not model_id or inputs is None:
                    return {"status": "error", "message": "Model ID and inputs are required for inference"}
                
                client = InferenceClient(model=model_id)
                result = client(inputs)
                return {"status": "success", "result": result}
            
            else:
                return {"status": "error", "message": f"Unknown Hugging Face action: {action}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def docker_operations(self, action, container=None, image=None, ports=None, env=None, command=None):
        """Interact with Docker"""
        try:
            if action == "ps":
                # List containers
                result = subprocess.run(["docker", "ps", "-a"], capture_output=True, text=True, check=True)
                return {"status": "success", "output": result.stdout}
                
            elif action == "images":
                # List images
                result = subprocess.run(["docker", "images"], capture_output=True, text=True, check=True)
                return {"status": "success", "output": result.stdout}
                
            elif action == "run":
                # Run a container
                if not image:
                    return {"status": "error", "message": "Image name is required for run action"}
                
                cmd = ["docker", "run", "-d"]
                
                # Add port mappings
                if ports:
                    for port_map in ports:
                        cmd.extend(["-p", port_map])
                
                # Add environment variables
                if env:
                    for key, value in env.items():
                        cmd.extend(["-e", f"{key}={value}"])
                
                # Add name if provided
                if container:
                    cmd.extend(["--name", container])
                
                # Add image name
                cmd.append(image)
                
                # Add command if provided
                if command:
                    cmd.extend(command if isinstance(command, list) else [command])
                
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                return {"status": "success", "container_id": result.stdout.strip()}
                
            elif action == "stop":
                # Stop a container
                if not container:
                    return {"status": "error", "message": "Container name/ID is required for stop action"}
                
                result = subprocess.run(["docker", "stop", container], capture_output=True, text=True, check=True)
                return {"status": "success", "output": result.stdout}
                
            elif action == "rm":
                # Remove a container
                if not container:
                    return {"status": "error", "message": "Container name/ID is required for rm action"}
                
                result = subprocess.run(["docker", "rm", container], capture_output=True, text=True, check=True)
                return {"status": "success", "output": result.stdout}
                
            elif action == "logs":
                # Get container logs
                if not container:
                    return {"status": "error", "message": "Container name/ID is required for logs action"}
                
                result = subprocess.run(["docker", "logs", container], capture_output=True, text=True, check=True)
                return {"status": "success", "logs": result.stdout}
                
            else:
                return {"status": "error", "message": f"Unknown Docker action: {action}"}
        except subprocess.CalledProcessError as e:
            return {"status": "error", "message": f"Docker error: {e.stderr}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def open_service(self, service_name=None, path="/"):
        """Open a web service in the browser"""
        try:
            if service_name == "webui" or service_name == "open-webui":
                return open_webui_ui()
            elif service_name == "flowise":
                return open_flowise()
            elif service_name:
                return open_web_service(service_name, path)
            else:
                # List available services and let the user choose
                services = list_all_services()
                return services
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def list_services(self):
        """List all available Docker services"""
        try:
            return list_all_services()
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def install_package(self, package_name, manager="pip"):
        """Install a package using the specified package manager"""
        commands = {
            "pip": ["pip", "install"],
            "npm": ["npm", "install", "-g"],
            "brew": ["brew", "install"],
            "gem": ["gem", "install"],
            "apt": ["apt", "install", "-y"],
        }
        
        if manager not in commands:
            return {"status": "error", "message": f"Unknown package manager: {manager}"}
        
        try:
            cmd = commands[manager] + [package_name]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return {"status": "success", "output": result.stdout, "message": f"Installed {package_name} using {manager}"}
        except subprocess.CalledProcessError as e:
            return {"status": "error", "message": f"Installation error: {e.stderr}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def display_help(self):
        """Display help information"""
        help_text = """
        Codex Help
        ==========
        
        Commands:
        - help: Display this help message
        - exit/quit: Exit Codex
        
        Tool Usage Examples:
        - "Run the command ls -la" (shell_command)
        - "Create a file named test.py with a simple hello world program" (file_operations, code_generation)
        - "Open VSCode for this project" (vscode)
        - "Clone the repository https://github.com/username/repo.git" (github_operations)
        - "What is the latest version of Python?" (web_browse)
        - "Generate a script that downloads images from a URL" (code_generation)
        
        For more detailed examples, type "examples".
        """
        print(help_text)
    
    def display_examples(self):
        """Display examples of using the tools"""
        examples = """
        Codex Examples
        =============
        
        Shell Commands:
        - "Run ls -la to see files in the current directory"
        - "Check if node.js is installed with 'node --version'"
        
        File Operations:
        - "Create a file called app.py with a Flask web server"
        - "Read the content of README.md"
        - "List all files in the src directory"
        
        VSCode:
        - "Open this project in VSCode"
        - "Open the file app.py in VSCode"
        
        GitHub:
        - "Initialize a git repository in this directory"
        - "Clone the repository https://github.com/openai/whisper.git"
        - "Commit all changes with message 'Initial commit'"
        
        Web Browsing:
        - "Search for 'How to use React hooks'"
        - "Get the content of the webpage https://example.com"
        
        Docker:
        - "List all running Docker containers"
        - "Run a Redis container on port 6379"
        - "Stop the container named 'my-redis'"
        
        Hugging Face:
        - "Search for text-to-image models on Hugging Face"
        - "Download the BERT base model"
        
        Code Generation:
        - "Generate a Python script that sends an email"
        - "Create a React component for a login form"
        """
        print(examples)
    
    def process_request(self, user_input):
        """Process a user request using the OpenAI API with improved formatting"""
        try:
            if user_input.lower() == "help":
                self.display_help()
                return
            
            if user_input.lower() == "examples":
                self.display_examples()
                return
            
            # Process the user input with the AI
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_input}
            ]
            
            # Show a spinner or message while waiting for API response
            print("Thinking...", end="\r")
            
            response = openai.chat.completions.create(
                model="gpt-4", 
                messages=messages
            )
            
            # Clear the thinking message
            print(" " * 20, end="\r")
            
            content = response.choices[0].message.content
            
            # Check if the response contains a tool call
            if "```json" in content:
                # Extract the JSON with regex to handle cases with multiple code blocks
                json_pattern = r"```json\s*([\s\S]*?)\s*```"
                json_matches = re.findall(json_pattern, content)
                
                if json_matches:
                    for json_str in json_matches:
                        try:
                            tool_data = json.loads(json_str)
                            if "tool" in tool_data and tool_data["tool"] in self.tools:
                                print(f"\n🛠️ Executing tool: {tool_data['tool']}...")
                                tool_func = self.tools[tool_data["tool"]]
                                result = tool_func(**tool_data.get("params", {}))
                                print(f"\n📊 Tool result:\n{json.dumps(result, indent=2)}")
                            else:
                                print(f"\n⚠️ Unknown tool or missing 'tool' key: {json_str}")
                        except json.JSONDecodeError:
                            print(f"\n❌ Failed to parse tool call JSON: {json_str}")
                
                # Display the remaining content without JSON blocks
                clean_content = re.sub(json_pattern, "", content).strip()
                if clean_content:
                    print("\n" + "=" * 80)
                    print("📝 Response:")
                    print("=" * 80)
                    print(clean_content)
                    print("=" * 80)
            else:
                # No tool call, just display the response
                print("\n" + "=" * 80)
                print("📝 Response:")
                print("=" * 80)
                print(content)
                print("=" * 80)
        
        except Exception as e:
            print(f"\n❌ Error processing request: {e}")
            print(f"\nStack trace: {traceback.format_exc()}")
    
    def run_interactive(self):
        """Run in interactive mode with improved input handling"""
        print("\nStarting Codex interactive session. Enter 'exit' to quit.")
        print("For multi-line input, end your message with '##' on a new line.")
        print("Example: Tell me about Python\n##")
        
        while True:
            try:
                # Collect multi-line input
                lines = []
                print("\nCodex> ", end="")
                
                while True:
                    line = input()
                    if line.strip() == "##":
                        break
                    if line.lower() in ["exit", "quit"]:
                        print("Goodbye! 👋")
                        return
                    lines.append(line)
                
                user_input = "\n".join(lines).strip()
                if not user_input:
                    continue
                
                # Process the complete input
                print("\n🔄 Processing your request...\n")
                self.process_request(user_input)
                print("\n✅ Response complete.")
            
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}")
                print("Try again or type 'exit' to quit.")

def main():
    parser = argparse.ArgumentParser(description="Codex - AI Assistant with extended capabilities")
    parser.add_argument("--interactive", "-i", action="store_true", help="Run in interactive mode")
    args = parser.parse_args()
    
    codex = Codex()
    
    if args.interactive:
        codex.run_interactive()
    else:
        codex.run_interactive()  # Default to interactive mode for now

if __name__ == "__main__":
    main()
