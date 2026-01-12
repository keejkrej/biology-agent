"""
Biology Microscopy MCP Server

Provides tools for reading and analyzing microscopy image files using bioio.
Supports OME-TIFF, Nikon ND2, and other formats through bioio plugins.
"""

from .server import main, mcp

__version__ = "1.0.0"
__all__ = ["main", "mcp"]
