#!/usr/bin/env python3
"""
Docker utilities for Codex to interact with running services
"""
import subprocess
import json
import time
import webbrowser
import requests
from typing import Dict, List, Optional, Union, Any

def get_all_containers(running_only: bool = True) -> List[Dict[str, Any]]:
    """Get information about all Docker containers"""
    cmd = ["docker", "ps", "-a", "--format", "{{json .}}"]
    if running_only:
        cmd = ["docker", "ps", "--format", "{{json .}}"]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        containers = []
        for line in result.stdout.strip().split('\n'):
            if line:
                containers.append(json.loads(line))
        return containers
    except subprocess.CalledProcessError as e:
        print(f"Error getting container info: {e}")
        return []

def get_container_by_name(name: str) -> Optional[Dict[str, Any]]:
    """Get container details by name"""
    containers = get_all_containers(running_only=False)
    for container in containers:
        if container.get('Names') == name:
            return container
    return None

def get_port_mappings(container_id: str) -> Dict[str, str]:
    """Get port mappings for a container"""
    try:
        result = subprocess.run(
            ["docker", "container", "port", container_id], 
            check=True, capture_output=True, text=True
        )
        
        port_map = {}
        for line in result.stdout.strip().split('\n'):
            if line:
                parts = line.split(' -> ')
                if len(parts) == 2:
                    container_port = parts[0]
                    host_mapping = parts[1]
                    port_map[container_port] = host_mapping
        
        return port_map
    except subprocess.CalledProcessError as e:
        print(f"Error getting port info: {e}")
        return {}

def open_web_service(service_name: str, path: str = "/") -> Dict[str, Any]:
    """Open a web service in the browser"""
    container = get_container_by_name(service_name)
    if not container:
        return {"status": "error", "message": f"Service {service_name} not found"}
    
    port_mappings = get_port_mappings(container.get('ID', ''))
    if not port_mappings:
        return {"status": "error", "message": f"No port mappings for {service_name}"}
    
    # Find the first port mapping
    for container_port, host_mapping in port_mappings.items():
        host, port = host_mapping.split(':')
        url = f"http://{host}:{port}{path}"
        webbrowser.open(url)
        return {"status": "success", "message": f"Opened {url}", "url": url}
    
    return {"status": "error", "message": "Failed to find a valid port mapping"}

def check_service_health(service_name: str, port: str = None, path: str = "/") -> Dict[str, Any]:
    """Check if a web service is healthy"""
    container = get_container_by_name(service_name)
    if not container:
        return {"status": "error", "message": f"Service {service_name} not found"}
    
    if port:
        url = f"http://localhost:{port}{path}"
    else:
        port_mappings = get_port_mappings(container.get('ID', ''))
        if not port_mappings:
            return {"status": "error", "message": f"No port mappings for {service_name}"}
        
        # Find the first port mapping
        for container_port, host_mapping in port_mappings.items():
            host, port = host_mapping.split(':')
            url = f"http://{host}:{port}{path}"
            break
    
    try:
        response = requests.get(url, timeout=5)
        if response.status_code < 400:
            return {
                "status": "success", 
                "message": f"Service {service_name} is healthy",
                "url": url,
                "response_code": response.status_code
            }
        else:
            return {
                "status": "error", 
                "message": f"Service returned status code {response.status_code}",
                "url": url,
                "response_code": response.status_code
            }
    except requests.RequestException as e:
        return {"status": "error", "message": f"Failed to connect: {str(e)}", "url": url}

def open_webui_ui() -> Dict[str, Any]:
    """Open the Open WebUI interface"""
    return open_web_service("open-webui")

def open_flowise() -> Dict[str, Any]:
    """Open the Flowise interface"""
    return open_web_service("flowise")

def list_all_services() -> Dict[str, Any]:
    """List all running services with their URLs"""
    containers = get_all_containers()
    services = []
    
    for container in containers:
        container_id = container.get('ID', '')
        name = container.get('Names', '')
        port_mappings = get_port_mappings(container_id)
        
        urls = []
        for container_port, host_mapping in port_mappings.items():
            host, port = host_mapping.split(':')
            urls.append(f"http://{host}:{port}")
        
        services.append({
            "name": name,
            "id": container_id,
            "status": container.get('Status', ''),
            "ports": port_mappings,
            "urls": urls
        })
    
    return {"status": "success", "services": services}

if __name__ == "__main__":
    # Print list of all services when run directly
    services = list_all_services()
    print(json.dumps(services, indent=2))
