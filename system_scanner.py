"""
System Scanner Module for ADO-TEE
Safely discovers scan roots and recursively discovers files while 
skipping protected system folders, virtual environments, and caches.
"""

from pathlib import Path

# Directories to skip during recursive file discovery
IGNORE_DIRS = {
    ".git", ".venv", "venv", "__pycache__", "node_modules", 
    "AppData", "Application Data", "Local Settings", "$Recycle.Bin",
    "System Volume Information", "Windows", "Program Files", 
    "Program Files (x86)", "ProgramData", "output"
}

# File extensions to ignore
IGNORE_EXTENSIONS = {
    ".tmp", ".temp", ".part", ".crdownload", ".download",
    ".log", ".cache", ".pyc", ".dll", ".exe", ".msi",
    ".sys", ".bin", ".iso"
}

def get_scan_roots():
    """
    Returns safe, accessible scan roots to avoid permission errors (WinError 5).
    Focuses on user profile folders and specific project workspaces.
    """
    user_profile = Path.home()  # Resolves to C:\Users\Admin
    
    # Safe folders to monitor and scan
    roots = [
        user_profile / "Desktop",
        user_profile / "Documents",
        user_profile / "Downloads",
        Path(r"D:\Admin\hacktober")  # Your development/hacktober directory
    ]
    
    # Filter to only return paths that actually exist on your machine
    valid_roots = [path for path in roots if path.exists()]
    return valid_roots

def discover_files(root_path: Path):
    """
    Recursively discovers valid files under a given root path while 
    safely bypassing ignored directories and system junk.
    """
    discovered = []
    try:
        for path in root_path.rglob("*"):
            # Check if any parent folder matches our ignore list
            if any(part in IGNORE_DIRS for part in path.parts):
                continue
            
            if path.is_file():
                # Skip ignored file extensions
                if path.suffix.lower() in IGNORE_EXTENSIONS:
                    continue
                discovered.append(path)
                
    except PermissionError:
        print(f"[WARNING] Permission denied accessing some items in: {root_path}")
    except Exception as error:
        print(f"[ERROR] Error scanning root {root_path}: {error}")
        
    return discovered