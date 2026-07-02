#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP wrapper for the PCIe Chapter 7 Query Tool.
Provides a programmatic interface for other AI agents.
"""

import sys
import io
import contextlib

# Import the original command implementations
from pcie_ch7_tool import (
    cmd_search,
    cmd_section,
    cmd_reg,
    cmd_cap,
    cmd_list_caps,
    cmd_toc,
    cmd_attr,
    cmd_help,
)

def run(command: str, args: str = "") -> str:
    """Execute a command and return its output as a string.

    Parameters
    ----------
    command: str
        The command name (e.g., "search", "reg").
    args: str, optional
        Arguments passed to the command.

    Returns
    -------
    str
        Captured stdout from the command execution.
    """
    buf = io.StringIO()
    # Redirect stdout temporarily
    with contextlib.redirect_stdout(buf):
        cmd = command.lower()
        if cmd == "search":
            cmd_search(args)
        elif cmd == "section":
            cmd_section(args)
        elif cmd == "reg":
            cmd_reg(args)
        elif cmd == "cap":
            cmd_cap(args)
        elif cmd == "caps":
            cmd_list_caps()
        elif cmd == "toc":
            cmd_toc(args.split() if args else [])
        elif cmd == "attr":
            cmd_attr(args)
        elif cmd == "help":
            cmd_help()
        else:
            # Fallback to search for unknown commands as original tool does
            cmd_search(" ".join([command] + ([args] if args else [])))
    return buf.getvalue()

# Simple CLI for manual testing
if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        arguments = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
        print(run(cmd, arguments))
    else:
        print("Usage: pcie_ch7_mcp.py <command> [args]")
