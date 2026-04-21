"""Base tool definitions for GenericAgent.

This module provides common built-in tools that agents can use,
such as web search, file I/O, and shell execution.
"""

import os
import subprocess
import json
from typing import Any


def read_file(path: str) -> str:
    """Read the contents of a file at the given path.

    Args:
        path: The file path to read.

    Returns:
        The file contents as a string, or an error message.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: File not found: {path}"
    except PermissionError:
        return f"Error: Permission denied reading: {path}"
    except Exception as e:
        return f"Error reading file: {e}"


def write_file(path: str, content: str) -> str:
    """Write content to a file at the given path.

    Creates parent directories if they do not exist.

    Args:
        path: The file path to write.
        content: The string content to write.

    Returns:
        A success or error message.
    """
    try:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote {len(content)} characters to {path}"
    except PermissionError:
        return f"Error: Permission denied writing to: {path}"
    except Exception as e:
        return f"Error writing file: {e}"


def list_directory(path: str = ".") -> str:
    """List the contents of a directory.

    Args:
        path: The directory path to list. Defaults to current directory.

    Returns:
        A newline-separated list of entries, or an error message.
    """
    try:
        entries = os.listdir(path)
        entries.sort()
        lines = []
        for entry in entries:
            full = os.path.join(path, entry)
            tag = "/" if os.path.isdir(full) else ""
            lines.append(f"{entry}{tag}")
        return "\n".join(lines) if lines else "(empty directory)"
    except FileNotFoundError:
        return f"Error: Directory not found: {path}"
    except PermissionError:
        return f"Error: Permission denied listing: {path}"
    except Exception as e:
        return f"Error listing directory: {e}"


def run_shell(command: str, timeout: int = 30) -> str:
    """Execute a shell command and return its output.

    Args:
        command: The shell command string to execute.
        timeout: Maximum seconds to wait before killing the process.

    Returns:
        Combined stdout and stderr output, or an error message.
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        output_parts = []
        if result.stdout.strip():
            output_parts.append(result.stdout.strip())
        if result.stderr.strip():
            output_parts.append(f"[stderr]\n{result.stderr.strip()}")
        if not output_parts:
            return f"(exit code {result.returncode}, no output)"
        return "\n".join(output_parts)
    except subprocess.TimeoutExpired:
        return f"Error: Command timed out after {timeout} seconds"
    except Exception as e:
        return f"Error running command: {e}"


# Registry mapping tool names to their callable implementations.
TOOL_REGISTRY: dict[str, Any] = {
    "read_file": read_file,
    "write_file": write_file,
    "list_directory": list_directory,
    "run_shell": run_shell,
}


def dispatch_tool(name: str, arguments: dict) -> str:
    """Dispatch a tool call by name with the provided arguments.

    Args:
        name: The registered tool name.
        arguments: A dict of keyword arguments to pass to the tool.

    Returns:
        The tool's string result, or an error if the tool is unknown.
    """
    if name not in TOOL_REGISTRY:
        available = ", ".join(sorted(TOOL_REGISTRY.keys()))
        return f"Error: Unknown tool '{name}'. Available tools: {available}"
    try:
        return TOOL_REGISTRY[name](**arguments)
    except TypeError as e:
        return f"Error: Bad arguments for tool '{name}': {e}"
