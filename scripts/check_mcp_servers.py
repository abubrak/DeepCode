#!/usr/bin/env python3
"""
MCP Server Health Check Script

This script verifies that MCP servers can start correctly and helps diagnose
common configuration issues.

Usage:
    python scripts/check_mcp_servers.py
"""

import sys
import subprocess
import importlib
import os
from pathlib import Path
import time

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    """Print a formatted header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}\n")

def print_success(text):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")

def print_error(text):
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")

def print_warning(text):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")

def print_info(text):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ {text}{Colors.RESET}")

def check_python_version():
    """Check if Python version meets requirements"""
    print_header("1. Checking Python Version")
    version = sys.version_info
    print_info(f"Python version: {sys.version}")
    
    if version >= (3, 8):
        print_success(f"Python {version.major}.{version.minor}.{version.micro} meets requirements (>= 3.8)")
        return True
    else:
        print_error(f"Python {version.major}.{version.minor}.{version.micro} is too old. Python 3.8+ required")
        return False

def check_python_path():
    """Check if Python is accessible"""
    print_header("2. Checking Python Executable")
    print_info(f"Python executable: {sys.executable}")
    
    # Check if 'python' command is available
    try:
        result = subprocess.run(['python', '--version'], 
                              capture_output=True, text=True, timeout=5)
        print_success(f"'python' command available: {result.stdout.strip()}")
    except Exception as e:
        print_warning(f"'python' command not available: {e}")
        print_info("  Note: Use 'python3' instead on Unix/Linux systems")
    
    return True

def check_dependencies():
    """Check if required packages are installed"""
    print_header("3. Checking Required Dependencies")
    
    required_packages = [
        'mcp',
        'mcp.server',
        'mcp.server.fastmcp',
        'anthropic',
        'openai',
        'google.genai',
        'aiofiles',
    ]
    
    all_ok = True
    for package in required_packages:
        try:
            # Try to import the package
            parts = package.split('.')
            if len(parts) == 1:
                importlib.import_module(package)
            else:
                # For nested imports like mcp.server
                mod = importlib.import_module(parts[0])
                for part in parts[1:]:
                    mod = getattr(mod, part, None)
                    if mod is None:
                        raise ImportError(f"Cannot import {package}")
            
            print_success(f"Package '{package}' is installed")
        except ImportError as e:
            print_error(f"Package '{package}' is NOT installed")
            print_info(f"  Install with: pip install {parts[0]}")
            all_ok = False
    
    return all_ok

def check_encoding():
    """Check system encoding settings"""
    print_header("4. Checking Encoding Configuration")
    
    stdout_enc = sys.stdout.encoding or "unknown"
    stderr_enc = sys.stderr.encoding or "unknown"
    print_info(f"stdout encoding: {stdout_enc}")
    print_info(f"stderr encoding: {stderr_enc}")
    print_info(f"Default encoding: {sys.getdefaultencoding()}")
    
    # Check environment variable
    pythonioencoding = os.environ.get('PYTHONIOENCODING', 'Not set')
    print_info(f"PYTHONIOENCODING: {pythonioencoding}")
    
    # Check if UTF-8 encoding is set (case-insensitive)
    stdout_is_utf8 = stdout_enc.lower() == 'utf-8' if stdout_enc != "unknown" else False
    env_is_utf8 = pythonioencoding.lower() == 'utf-8' if pythonioencoding != 'Not set' else False
    
    if stdout_is_utf8 or env_is_utf8:
        print_success("UTF-8 encoding is configured")
        return True
    else:
        print_warning("UTF-8 encoding not set. Set PYTHONIOENCODING=utf-8")
        return False

def check_mcp_server(server_script, server_name, timeout=3):
    """Test if an MCP server can start"""
    print_header(f"5. Testing {server_name}")
    
    script_path = Path(server_script)
    if not script_path.exists():
        print_error(f"Server script not found: {server_script}")
        return False
    
    print_info(f"Testing: {server_script}")
    
    try:
        # Start the server process
        process = subprocess.Popen(
            [sys.executable, str(script_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env={**os.environ, 'PYTHONIOENCODING': 'utf-8'}
        )
        
        # Wait a bit for startup
        time.sleep(timeout)
        
        # Check if process is still running
        poll = process.poll()
        
        if poll is None:
            # Process is still running - good sign
            print_success(f"{server_name} started successfully")
            process.terminate()
            process.wait(timeout=2)
            return True
        else:
            # Process exited
            stdout, stderr = process.communicate()
            if poll == 0:
                print_warning(f"{server_name} exited normally (might be waiting for input)")
                if stdout:
                    print_info("stdout:\n" + stdout[:500])
                return True
            else:
                print_error(f"{server_name} failed to start (exit code: {poll})")
                if stderr:
                    print_error("stderr:\n" + stderr[:500])
                return False
                
    except Exception as e:
        print_error(f"Failed to test {server_name}: {e}")
        return False
    finally:
        try:
            if process.poll() is None:
                process.terminate()
                process.wait(timeout=2)
        except:
            pass

def check_pythonpath():
    """Check PYTHONPATH configuration"""
    print_header("6. Checking PYTHONPATH")
    
    pythonpath = os.environ.get('PYTHONPATH', 'Not set')
    print_info(f"PYTHONPATH: {pythonpath}")
    
    current_dir = os.getcwd()
    if current_dir in sys.path or '.' in sys.path:
        print_success("Current directory is in Python path")
        return True
    else:
        print_warning("Current directory not in Python path")
        print_info("  Set PYTHONPATH=. or add current directory to sys.path")
        return False

def main():
    """Run all health checks"""
    print(f"\n{Colors.BOLD}{'='*60}")
    print(f"  MCP Server Health Check")
    print(f"{'='*60}{Colors.RESET}\n")
    
    results = []
    
    # Run checks
    results.append(("Python Version", check_python_version()))
    results.append(("Python Path", check_python_path()))
    results.append(("Dependencies", check_dependencies()))
    results.append(("Encoding", check_encoding()))
    results.append(("PYTHONPATH", check_pythonpath()))
    
    # Test MCP servers
    results.append(("Command Executor", check_mcp_server(
        "tools/command_executor.py", 
        "Command Executor Server"
    )))
    results.append(("Code Implementation", check_mcp_server(
        "tools/code_implementation_server.py",
        "Code Implementation Server"
    )))
    
    # Print summary
    print_header("Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        if result:
            print_success(f"{name}: PASS")
        else:
            print_error(f"{name}: FAIL")
    
    print(f"\n{Colors.BOLD}Total: {passed}/{total} checks passed{Colors.RESET}\n")
    
    if passed == total:
        print_success("All checks passed! Your MCP server setup is ready.")
        return 0
    else:
        print_error("Some checks failed. Please review the errors above.")
        print_info("\nFor detailed troubleshooting, see: docs/TROUBLESHOOTING_MCP.md")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Health check interrupted by user{Colors.RESET}")
        sys.exit(130)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
