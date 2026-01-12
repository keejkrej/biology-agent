#!/usr/bin/env python3
"""
Test the Biology MCP Server

Creates test files and validates all MCP tools work correctly.
"""

import sys
import json
import tempfile
import numpy as np
from pathlib import Path

# Add parent mcp-server to path
sys.path.insert(0, str(Path(__file__).parent.parent / "mcp-server"))

from core import (
    read_microscopy_metadata,
    get_image_info,
    list_scenes,
    get_channel_info,
    get_physical_dimensions,
    validate_microscopy_file
)


def create_test_ome_tiff(output_path: Path):
    """Create a test OME-TIFF file for testing."""
    import tifffile

    print(f"Creating test OME-TIFF file: {output_path}")

    # Create random test data (3 channels, 5 Z-slices, 256x256 pixels)
    data = np.random.randint(0, 255, (3, 5, 256, 256), dtype=np.uint8)

    # Write as OME-TIFF using tifffile
    # Format: CZYX order
    tifffile.imwrite(
        str(output_path),
        data,
        photometric='minisblack',
        metadata={
            'axes': 'CZYX',
            'Channel': {'Name': ['DAPI', 'GFP', 'RFP']},
            'PhysicalSizeX': 0.065,
            'PhysicalSizeY': 0.065,
            'PhysicalSizeZ': 0.2,
            'PhysicalSizeXUnit': 'µm',
            'PhysicalSizeYUnit': 'µm',
            'PhysicalSizeZUnit': 'µm',
        }
    )

    print(f"✅ Created test file: {output_path.name}")
    return output_path


def test_validate_microscopy_file(test_file):
    """Test validate_microscopy_file tool."""
    print("\n" + "="*60)
    print("Testing: validate_microscopy_file")
    print("="*60)

    result = validate_microscopy_file(str(test_file))

    if "error" in result:
        print(f"❌ Error: {result['error']}")
        return False

    print(f"✅ File exists: {result.get('exists')}")
    print(f"✅ Is file: {result.get('is_file')}")
    print(f"✅ Readable by bioio: {result.get('readable_by_bioio')}")
    print(f"   File size: {result.get('file_size_mb')} MB")

    if result.get('warnings'):
        print(f"⚠️  Warnings: {len(result['warnings'])}")
        for warning in result['warnings']:
            print(f"   - {warning}")

    if result.get('errors'):
        print(f"❌ Errors: {len(result['errors'])}")
        for error in result['errors']:
            print(f"   - {error}")
        return False

    return result.get('readable_by_bioio', False)


def test_read_microscopy_metadata(test_file):
    """Test read_microscopy_metadata tool."""
    print("\n" + "="*60)
    print("Testing: read_microscopy_metadata")
    print("="*60)

    result = read_microscopy_metadata(str(test_file))

    if "error" in result:
        print(f"❌ Error: {result['error']}")
        return False

    print(f"✅ File: {result.get('file_name')}")
    print(f"✅ Channels: {result.get('channel_names')}")
    print(f"✅ Dimensions: {result.get('dimensions')}")
    print(f"✅ Shape: {result.get('shape')}")
    print(f"✅ Physical pixel sizes: {result.get('physical_pixel_sizes')}")

    # Validate expected values
    assert result['dimensions']['C'] == 3, "Expected 3 channels"
    assert result['dimensions']['Z'] == 5, "Expected 5 Z-slices"
    assert len(result['channel_names']) == 3, "Expected 3 channel names"
    assert "DAPI" in result['channel_names'], "Expected DAPI channel"

    print("✅ All assertions passed")
    return True


def test_get_image_info(test_file):
    """Test get_image_info tool."""
    print("\n" + "="*60)
    print("Testing: get_image_info")
    print("="*60)

    result = get_image_info(str(test_file))

    if "error" in result:
        print(f"❌ Error: {result['error']}")
        return False

    print(f"✅ File: {result.get('file_name')}")
    print(f"✅ Dimensions: {result.get('dimensions')}")
    print(f"✅ Num channels: {result.get('num_channels')}")
    print(f"✅ Num Z-slices: {result.get('num_z_slices')}")
    print(f"✅ XY dimensions: {result.get('xy_dimensions')}")

    assert result['num_channels'] == 3, "Expected 3 channels"
    assert result['num_z_slices'] == 5, "Expected 5 Z-slices"

    print("✅ All assertions passed")
    return True


def test_get_channel_info(test_file):
    """Test get_channel_info tool."""
    print("\n" + "="*60)
    print("Testing: get_channel_info")
    print("="*60)

    result = get_channel_info(str(test_file))

    if "error" in result:
        print(f"❌ Error: {result['error']}")
        return False

    print(f"✅ Num channels: {result.get('num_channels')}")
    print(f"✅ Channel names: {result.get('channel_names')}")
    print(f"✅ Channels:")
    for ch in result.get('channels', []):
        print(f"   [{ch['index']}] {ch['name']}")

    assert result['num_channels'] == 3, "Expected 3 channels"
    assert len(result['channels']) == 3, "Expected 3 channel entries"

    print("✅ All assertions passed")
    return True


def test_get_physical_dimensions(test_file):
    """Test get_physical_dimensions tool."""
    print("\n" + "="*60)
    print("Testing: get_physical_dimensions")
    print("="*60)

    result = get_physical_dimensions(str(test_file))

    if "error" in result:
        print(f"❌ Error: {result['error']}")
        return False

    print(f"✅ Pixel sizes (µm): {result.get('pixel_sizes_um')}")
    print(f"✅ Dimensions (pixels): {result.get('dimensions_pixels')}")
    print(f"✅ Physical dimensions: {result.get('physical_dimensions')}")

    px_sizes = result.get('pixel_sizes_um', {})
    assert px_sizes['X'] is not None, "Expected X pixel size"
    assert px_sizes['Y'] is not None, "Expected Y pixel size"
    assert px_sizes['Z'] is not None, "Expected Z pixel size"

    # Check calculated dimensions
    phys_dims = result.get('physical_dimensions', {})
    assert 'width_um' in phys_dims, "Expected width calculation"
    assert 'height_um' in phys_dims, "Expected height calculation"
    assert 'depth_um' in phys_dims, "Expected depth calculation"

    print("✅ All assertions passed")
    return True


def test_list_scenes(test_file):
    """Test list_scenes tool."""
    print("\n" + "="*60)
    print("Testing: list_scenes")
    print("="*60)

    result = list_scenes(str(test_file))

    if "error" in result:
        print(f"❌ Error: {result['error']}")
        return False

    print(f"✅ Scenes: {result.get('scenes')}")
    print(f"✅ Num scenes: {result.get('num_scenes')}")
    print(f"✅ Current scene: {result.get('current_scene')}")

    # OME-TIFF files we create typically have 1 scene
    # This is expected behavior
    print("✅ Test passed")
    return True


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("Biology MCP Server Test Suite")
    print("="*60)

    # Create temporary directory for test files
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        test_file = tmpdir / "test_image.ome.tiff"

        # Create test file
        try:
            create_test_ome_tiff(test_file)
        except Exception as e:
            print(f"\n❌ Failed to create test file: {e}")
            return 1

        # Run all tests
        tests = [
            ("validate_microscopy_file", test_validate_microscopy_file),
            ("read_microscopy_metadata", test_read_microscopy_metadata),
            ("get_image_info", test_get_image_info),
            ("get_channel_info", test_get_channel_info),
            ("get_physical_dimensions", test_get_physical_dimensions),
            ("list_scenes", test_list_scenes),
        ]

        results = []
        for test_name, test_func in tests:
            try:
                success = test_func(test_file)
                results.append((test_name, success))
            except Exception as e:
                print(f"\n❌ Test failed with exception: {e}")
                import traceback
                traceback.print_exc()
                results.append((test_name, False))

        # Print summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)

        passed = sum(1 for _, success in results if success)
        total = len(results)

        for test_name, success in results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status} - {test_name}")

        print()
        print(f"Passed: {passed}/{total}")

        if passed == total:
            print("\n🎉 All tests passed!")
            return 0
        else:
            print(f"\n❌ {total - passed} test(s) failed")
            return 1


if __name__ == "__main__":
    sys.exit(main())
