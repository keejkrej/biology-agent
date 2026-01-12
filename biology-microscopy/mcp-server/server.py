#!/usr/bin/env python3
"""
Biology Microscopy MCP Server

Provides tools for reading and analyzing microscopy image files using bioio.
Supports OME-TIFF, Nikon ND2, and other formats through bioio plugins.
"""

from typing import Optional, Dict, Any

from fastmcp import FastMCP

# Import core functions
from core import (
    read_microscopy_metadata as _read_microscopy_metadata,
    get_image_info as _get_image_info,
    list_scenes as _list_scenes,
    get_channel_info as _get_channel_info,
    get_physical_dimensions as _get_physical_dimensions,
    validate_microscopy_file as _validate_microscopy_file,
)


# Initialize FastMCP server
mcp = FastMCP("Biology Microscopy Server")


@mcp.tool()
def read_microscopy_metadata(file_path: str) -> Dict[str, Any]:
    """
    Read complete metadata from a microscopy file.

    Args:
        file_path: Path to the microscopy image file (OME-TIFF, ND2, etc.)

    Returns:
        Dictionary containing:
        - metadata: Format-specific metadata
        - channel_names: List of channel identifiers
        - dimensions: Image dimensions (X, Y, Z, C, T)
        - physical_pixel_sizes: Physical dimensions in microns
        - scenes: Available scenes in multi-scene files
        - shape: Tuple of dimension sizes

    Example:
        >>> read_microscopy_metadata("/path/to/image.ome.tiff")
    """
    return _read_microscopy_metadata(file_path)


@mcp.tool()
def get_image_info(file_path: str) -> Dict[str, Any]:
    """
    Get summary information about a microscopy image.

    Args:
        file_path: Path to the microscopy image file

    Returns:
        Concise summary with dimensions, channels, and basic properties

    Example:
        >>> get_image_info("/path/to/image.nd2")
    """
    return _get_image_info(file_path)


@mcp.tool()
def list_scenes(file_path: str) -> Dict[str, Any]:
    """
    List all scenes in a multi-scene microscopy file.

    Args:
        file_path: Path to the microscopy image file

    Returns:
        Dictionary with list of scene names/IDs and current scene

    Example:
        >>> list_scenes("/path/to/multi_scene.ome.tiff")
    """
    return _list_scenes(file_path)


@mcp.tool()
def get_channel_info(file_path: str, scene: Optional[str] = None) -> Dict[str, Any]:
    """
    Get detailed information about channels in the image.

    Args:
        file_path: Path to the microscopy image file
        scene: Optional scene name/ID to switch to before reading channels

    Returns:
        Dictionary with channel names and count

    Example:
        >>> get_channel_info("/path/to/image.ome.tiff")
        >>> get_channel_info("/path/to/image.ome.tiff", scene="Image:0")
    """
    return _get_channel_info(file_path, scene)


@mcp.tool()
def get_physical_dimensions(file_path: str) -> Dict[str, Any]:
    """
    Get physical dimensions and pixel sizes in micrometers.

    Args:
        file_path: Path to the microscopy image file

    Returns:
        Dictionary with pixel sizes and calculated physical dimensions

    Example:
        >>> get_physical_dimensions("/path/to/image.ome.tiff")
    """
    return _get_physical_dimensions(file_path)


@mcp.tool()
def validate_microscopy_file(file_path: str) -> Dict[str, Any]:
    """
    Validate that a file can be read by bioio and check for common issues.

    Args:
        file_path: Path to the microscopy image file

    Returns:
        Validation results with any warnings or errors

    Example:
        >>> validate_microscopy_file("/path/to/image.ome.tiff")
    """
    return _validate_microscopy_file(file_path)


if __name__ == "__main__":
    # Run the MCP server with stdio transport
    mcp.run()

