# MCP Server Connection Troubleshooting Guide

This guide helps resolve common MCP (Model Context Protocol) server connection issues, particularly the "Connection closed" error.

## Common Issues and Solutions

### Issue 1: "Connection closed" Error

**Error Message:**
```
[ERROR] mcp_agent.mcp.mcp_agent_client_session - send_request failed: Connection closed
```

**Root Causes:**
1. Python interpreter not found or incorrectly configured
2. Missing Python dependencies
3. Encoding issues on Windows
4. MCP server startup failure

**Solutions:**

#### Solution 1: Verify Python Installation

Check that Python is properly installed and accessible:

```bash
# Check Python version
python --version
# or
python3 --version

# Check if Python is in PATH
which python   # Unix/Linux/macOS
where python   # Windows
```

**Requirements:**
- Python 3.8 or higher required
- Python must be in system PATH

#### Solution 2: Install Required Dependencies

Ensure all required packages are installed:

```bash
pip install -r requirements.txt
```

Key dependencies:
- `mcp-agent` - Core MCP framework
- `anthropic` - Claude API client
- `openai` - OpenAI API client
- `google-genai` - Google Gemini API client

#### Solution 3: Configure Python Command (Platform-Specific)

Edit `mcp_agent.config.yaml` based on your platform:

**Windows:**
```yaml
command-executor:
  command: python  # or 'py' if python command not found
  args:
    - tools/command_executor.py
  env:
    PYTHONPATH: .
    PYTHONIOENCODING: utf-8
```

**macOS/Linux:**
```yaml
command-executor:
  command: python3  # or 'python' if linked to Python 3
  args:
    - tools/command_executor.py
  env:
    PYTHONPATH: .
    PYTHONIOENCODING: utf-8
```

#### Solution 4: Set Environment Variables

Ensure proper encoding, especially on Windows:

**Windows (PowerShell):**
```powershell
$env:PYTHONIOENCODING = "utf-8"
```

**Windows (Command Prompt):**
```cmd
set PYTHONIOENCODING=utf-8
```

**Unix/Linux/macOS:**
```bash
export PYTHONIOENCODING=utf-8
```

### Issue 2: "Tool 'write_file' not found" Error

**Error Message:**
```
[ERROR] Error: Tool 'write_file' not found
```

**Root Causes:**
1. MCP server failed to start properly
2. Tool registration incomplete
3. Server connection not established

**Solutions:**

#### Solution 1: Check Server Logs

Enable detailed logging to see server startup:

1. Check console output when starting the application
2. Look for server initialization messages:
   ```
   🚀 Code Implementation MCP Server
   Available tools:
     • write_file
     • read_file
     ...
   ```

#### Solution 2: Verify Server Configuration

Ensure `code-implementation` server is properly configured in `mcp_agent.config.yaml`:

```yaml
mcp:
  servers:
    code-implementation:
      args:
        - tools/code_implementation_server.py
      command: python
      description: Paper code reproduction tool server
      env:
        PYTHONPATH: .
        PYTHONIOENCODING: utf-8
```

#### Solution 3: Test Server Standalone

Test if the MCP server can start independently:

```bash
cd /path/to/DeepCode
python tools/code_implementation_server.py
```

Expected output:
```
🚀 Code Implementation MCP Server
📝 Paper Code Implementation Tool Server
Available tools:
  • read_code_mem
  • write_file
  • execute_python
  ...
🔧 Server starting...
```

### Issue 3: Python Path Issues

**Symptoms:**
- "ModuleNotFoundError" errors
- "No module named 'mcp'" errors

**Solutions:**

#### Solution 1: Set PYTHONPATH

Ensure PYTHONPATH includes the project root:

```bash
# Unix/Linux/macOS
export PYTHONPATH="${PYTHONPATH}:/path/to/DeepCode"

# Windows (PowerShell)
$env:PYTHONPATH = "${env:PYTHONPATH};C:\path\to\DeepCode"
```

#### Solution 2: Use Absolute Paths

In `mcp_agent.config.yaml`, use absolute paths for server scripts:

```yaml
code-implementation:
  args:
    - /full/path/to/DeepCode/tools/code_implementation_server.py
  command: python
```

### Issue 4: Windows-Specific Issues

**Common Problems on Windows:**
1. UTF-8 encoding issues
2. Path separator differences
3. Python launcher (`py`) vs `python` command

**Solutions:**

#### Solution 1: Use Python Launcher

Windows users can try using the `py` launcher:

```yaml
command: py
args:
  - -3  # Force Python 3
  - tools/code_implementation_server.py
```

#### Solution 2: Set Console Encoding

Configure Windows console for UTF-8:

```cmd
chcp 65001
set PYTHONIOENCODING=utf-8
```

#### Solution 3: Use Forward Slashes

In configuration files, prefer forward slashes even on Windows:

```yaml
args:
  - tools/code_implementation_server.py  # Good
  # Not: tools\code_implementation_server.py
```

## Diagnostic Commands

### Check MCP Server Health

1. **List available Python installations:**
   ```bash
   # Windows
   where python
   py --list
   
   # Unix/Linux/macOS
   which python python3
   ```

2. **Verify MCP agent installation:**
   ```bash
   pip show mcp-agent
   ```

3. **Test server startup:**
   ```bash
   python tools/command_executor.py
   python tools/code_implementation_server.py
   ```

4. **Check for import errors:**
   ```bash
   python -c "from mcp.server.fastmcp import FastMCP; print('OK')"
   python -c "from mcp.server import Server; print('OK')"
   ```

### Enable Debug Logging

Add to your environment or startup script:

```bash
# Unix/Linux/macOS
export MCP_LOG_LEVEL=DEBUG

# Windows (PowerShell)
$env:MCP_LOG_LEVEL = "DEBUG"
```

## Getting Help

If you continue to experience issues:

1. **Gather Information:**
   - Python version: `python --version`
   - Operating system and version
   - Full error messages and stack traces
   - MCP server logs

2. **Check Existing Issues:**
   - Search GitHub issues: https://github.com/HKUDS/DeepCode/issues
   - Look for similar error messages

3. **Create New Issue:**
   - Use the "Question" or "Bug" template
   - Include all diagnostic information
   - Attach relevant log files

## Quick Fixes Checklist

- [ ] Python 3.8+ installed and in PATH
- [ ] All dependencies installed: `pip install -r requirements.txt`
- [ ] `PYTHONIOENCODING=utf-8` environment variable set
- [ ] `PYTHONPATH` includes project root
- [ ] Correct `python` command in `mcp_agent.config.yaml`
- [ ] MCP servers start successfully when run standalone
- [ ] No firewall blocking local connections
- [ ] UTF-8 console encoding (especially Windows)

## Platform-Specific Quick Start

### Windows
```powershell
# Set environment
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONPATH = "${env:PYTHONPATH};${PWD}"

# Install dependencies
pip install -r requirements.txt

# Test servers
python tools/command_executor.py
python tools/code_implementation_server.py
```

### macOS/Linux
```bash
# Set environment
export PYTHONIOENCODING=utf-8
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Install dependencies
pip3 install -r requirements.txt

# Test servers
python3 tools/command_executor.py
python3 tools/code_implementation_server.py
```

## Additional Resources

- [MCP Documentation](https://github.com/anthropics/mcp)
- [DeepCode README](../README.md)
- [Python Path Configuration](https://docs.python.org/3/using/cmdline.html#envvar-PYTHONPATH)
