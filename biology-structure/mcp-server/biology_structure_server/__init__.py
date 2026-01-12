"""
Biology Structure MCP Server

Biomolecular structure prediction using Boltz-2.
Supports NVIDIA NIM cloud API and local GPU execution.
"""

from .server import main

__version__ = "1.0.0"
__all__ = ["main"]
