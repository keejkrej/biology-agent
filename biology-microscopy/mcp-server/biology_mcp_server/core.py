"""
Core microscopy analysis functions

These functions contain the actual logic for reading and analyzing microscopy files.
The server.py file wraps these as MCP tools.
"""

from pathlib import Path
from typing import Optional, Dict, Any, List
import traceback

from bioio import BioImage


def _serialize_metadata(obj: Any) -> Any:
    """Convert metadata objects to JSON-serializable format."""
    if hasattr(obj, '__dict__'):
        return {k: _serialize_metadata(v) for k, v in obj.__dict__.items() if not k.startswith('_')}
    elif isinstance(obj, (list, tuple)):
        return [_serialize_metadata(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: _serialize_metadata(v) for k, v in obj.items()}
    elif isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    else:
        return str(obj)


def read_microscopy_metadata(file_path: str) -> Dict[str, Any]:
    """Read complete metadata from a microscopy file."""
    try:
        file_path = Path(file_path).expanduser().resolve()

        if not file_path.exists():
            return {"error": f"File not found: {file_path}"}

        img = BioImage(file_path)

        result = {
            "file_path": str(file_path),
            "file_name": file_path.name,
            "channel_names": img.channel_names,
            "dimensions": {
                "order": img.dims.order,
                "T": img.dims.T,
                "C": img.dims.C,
                "Z": img.dims.Z,
                "Y": img.dims.Y,
                "X": img.dims.X,
            },
            "shape": img.shape,
            "physical_pixel_sizes": {
                "Z": img.physical_pixel_sizes.Z,
                "Y": img.physical_pixel_sizes.Y,
                "X": img.physical_pixel_sizes.X,
            },
            "scenes": img.scenes if hasattr(img, 'scenes') else [],
            "current_scene": img.current_scene if hasattr(img, 'current_scene') else None,
        }

        if hasattr(img, 'metadata') and img.metadata is not None:
            result["metadata"] = _serialize_metadata(img.metadata)

        return result

    except Exception as e:
        return {
            "error": str(e),
            "error_type": type(e).__name__,
            "traceback": traceback.format_exc()
        }


def get_image_info(file_path: str) -> Dict[str, Any]:
    """Get summary information about a microscopy image."""
    try:
        file_path = Path(file_path).expanduser().resolve()

        if not file_path.exists():
            return {"error": f"File not found: {file_path}"}

        img = BioImage(file_path)

        return {
            "file_name": file_path.name,
            "dimensions": f"{img.dims.order} = {img.shape}",
            "num_channels": img.dims.C,
            "channel_names": img.channel_names,
            "num_timepoints": img.dims.T,
            "num_z_slices": img.dims.Z,
            "xy_dimensions": (img.dims.Y, img.dims.X),
            "pixel_sizes_um": {
                "Z": img.physical_pixel_sizes.Z,
                "Y": img.physical_pixel_sizes.Y,
                "X": img.physical_pixel_sizes.X,
            },
            "has_multiple_scenes": len(img.scenes) > 1 if hasattr(img, 'scenes') else False,
        }

    except Exception as e:
        return {
            "error": str(e),
            "error_type": type(e).__name__,
            "traceback": traceback.format_exc()
        }


def list_scenes(file_path: str) -> Dict[str, Any]:
    """List all scenes in a multi-scene microscopy file."""
    try:
        file_path = Path(file_path).expanduser().resolve()

        if not file_path.exists():
            return {"error": f"File not found: {file_path}"}

        img = BioImage(file_path)

        if not hasattr(img, 'scenes'):
            return {
                "message": "This file format does not support multiple scenes",
                "scenes": []
            }

        return {
            "file_name": file_path.name,
            "scenes": img.scenes,
            "num_scenes": len(img.scenes),
            "current_scene": img.current_scene,
        }

    except Exception as e:
        return {
            "error": str(e),
            "error_type": type(e).__name__,
            "traceback": traceback.format_exc()
        }


def get_channel_info(file_path: str, scene: Optional[str] = None) -> Dict[str, Any]:
    """Get detailed information about channels in the image."""
    try:
        file_path = Path(file_path).expanduser().resolve()

        if not file_path.exists():
            return {"error": f"File not found: {file_path}"}

        img = BioImage(file_path)

        if scene is not None and hasattr(img, 'set_scene'):
            img.set_scene(scene)

        return {
            "file_name": file_path.name,
            "current_scene": img.current_scene if hasattr(img, 'current_scene') else None,
            "num_channels": img.dims.C,
            "channel_names": img.channel_names,
            "channels": [
                {"index": i, "name": name}
                for i, name in enumerate(img.channel_names)
            ]
        }

    except Exception as e:
        return {
            "error": str(e),
            "error_type": type(e).__name__,
            "traceback": traceback.format_exc()
        }


def get_physical_dimensions(file_path: str) -> Dict[str, Any]:
    """Get physical dimensions and pixel sizes in micrometers."""
    try:
        file_path = Path(file_path).expanduser().resolve()

        if not file_path.exists():
            return {"error": f"File not found: {file_path}"}

        img = BioImage(file_path)

        px_z = img.physical_pixel_sizes.Z
        px_y = img.physical_pixel_sizes.Y
        px_x = img.physical_pixel_sizes.X

        physical_dims = {}
        if px_x is not None and px_y is not None:
            physical_dims["width_um"] = img.dims.X * px_x
            physical_dims["height_um"] = img.dims.Y * px_y
            physical_dims["area_um2"] = (img.dims.X * px_x) * (img.dims.Y * px_y)

        if px_z is not None and img.dims.Z > 1:
            physical_dims["depth_um"] = img.dims.Z * px_z
            if "area_um2" in physical_dims:
                physical_dims["volume_um3"] = physical_dims["area_um2"] * physical_dims["depth_um"]

        return {
            "file_name": file_path.name,
            "pixel_sizes_um": {
                "Z": px_z,
                "Y": px_y,
                "X": px_x,
            },
            "dimensions_pixels": {
                "Z": img.dims.Z,
                "Y": img.dims.Y,
                "X": img.dims.X,
            },
            "physical_dimensions": physical_dims,
        }

    except Exception as e:
        return {
            "error": str(e),
            "error_type": type(e).__name__,
            "traceback": traceback.format_exc()
        }


def validate_microscopy_file(file_path: str) -> Dict[str, Any]:
    """Validate that a file can be read by bioio and check for common issues."""
    try:
        file_path = Path(file_path).expanduser().resolve()

        validation = {
            "file_path": str(file_path),
            "file_name": file_path.name,
            "exists": file_path.exists(),
            "is_file": file_path.is_file() if file_path.exists() else False,
            "file_size_mb": round(file_path.stat().st_size / (1024 * 1024), 2) if file_path.exists() else None,
            "readable_by_bioio": False,
            "warnings": [],
            "errors": []
        }

        if not validation["exists"]:
            validation["errors"].append("File does not exist")
            return validation

        if not validation["is_file"]:
            validation["errors"].append("Path is not a file")
            return validation

        try:
            img = BioImage(file_path)
            validation["readable_by_bioio"] = True
            validation["format_detected"] = True

            if img.dims.C == 0:
                validation["warnings"].append("No channels detected")

            if img.dims.X == 0 or img.dims.Y == 0:
                validation["errors"].append("Invalid XY dimensions")

            if img.physical_pixel_sizes.X is None:
                validation["warnings"].append("Physical pixel size (X) not found in metadata")

            if img.physical_pixel_sizes.Y is None:
                validation["warnings"].append("Physical pixel size (Y) not found in metadata")

            validation["summary"] = {
                "dimensions": f"{img.dims.order} = {img.shape}",
                "channels": img.dims.C,
                "timepoints": img.dims.T,
                "z_slices": img.dims.Z,
            }

        except Exception as e:
            validation["readable_by_bioio"] = False
            validation["errors"].append(f"Failed to read with bioio: {str(e)}")

        return validation

    except Exception as e:
        return {
            "error": str(e),
            "error_type": type(e).__name__,
            "traceback": traceback.format_exc()
        }
