# Biology Agent - Microscopy Data Analysis Toolkit

A comprehensive toolkit for analyzing microscopy image data in Claude Code, built on [bioio](https://bioio-devs.github.io/bioio/).

## 📁 Repository Structure

```
biology-agent/                    # Marketplace root
├── .claude-plugin/
│   └── marketplace.json          # Marketplace manifest
├── biology-microscopy/           # The plugin
│   ├── .claude-plugin/
│   │   └── plugin.json           # Plugin metadata
│   ├── .mcp.json                 # MCP server configuration (uses uvx)
│   ├── mcp-server/               # Python MCP server package
│   │   ├── pyproject.toml        # Package configuration
│   │   └── biology_mcp_server/   # Server code
│   ├── scripts/                  # CLI tools
│   └── skills/                   # Claude Code skills
├── tests/                        # Test files
└── README.md
```

This repository is structured as a **Claude Code marketplace** containing the `biology-microscopy` plugin.

## 🎯 What Is This?

The Biology Agent provides an interactive microscopy data analysis assistant that integrates seamlessly with Claude Code. It enables you to:

- 📊 **Read metadata** from microscopy files (OME-TIFF, Nikon ND2, Zeiss CZI, etc.)
- 🔍 **Validate files** and check for data quality issues
- 📁 **Batch process** folders of images for metadata extraction
- 🎨 **Analyze images** interactively using natural language
- 🛠️ **Use standalone tools** for automation outside Claude Code

## 🏗️ Architecture

The toolkit uses a **hybrid approach** combining three components:

### 1. MCP Server (`biology-microscopy/mcp-server/`)
Exposes bioio capabilities as tools that Claude Code can call directly:
- `read_microscopy_metadata` - Extract complete metadata
- `get_image_info` - Quick summary information
- `list_scenes` - Multi-scene file support
- `get_channel_info` - Channel details
- `get_physical_dimensions` - Physical sizes in micrometers
- `validate_microscopy_file` - File validation and quality checks

### 2. Claude Code Skills (`biology-microscopy/skills/`)
Pre-packaged workflows for common tasks:
- `/extract-metadata-batch` - Process folders of files
- `/analyze-microscopy-file` - Comprehensive single-file analysis

### 3. Helper CLI Scripts (`biology-microscopy/scripts/`)
Standalone command-line tools:
- `microscopy-info` - Display file metadata
- `batch-convert-metadata` - Export metadata to CSV/JSON
- `validate-formats` - Validate bioio compatibility

## 📦 Installation

### ⚡ Via Claude Code Marketplace (Recommended)

Install directly from Claude Code using the `/plugin` command:

```
/plugin marketplace add keejkrej/biology-agent
/plugin install biology-microscopy@keejkrej
```

Then **restart Claude Code** (quit completely and reopen).

The MCP server uses `uvx` to automatically manage dependencies - no manual Python setup required.

### 📍 Local Installation (Development)

For development or testing:

1. Clone the repository:
   ```bash
   git clone https://github.com/keejkrej/biology-agent.git
   cd biology-agent
   ```

2. In Claude Code, run `/plugin` and select **"Add local plugin"**

3. Navigate to the `biology-microscopy/` directory and select it

4. Restart Claude Code

### Prerequisites

- **[uv](https://github.com/astral-sh/uv)** - Required for `uvx` (handles MCP server dependencies automatically)
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
- **[Claude Code](https://github.com/anthropics/claude-code)**

### Optional: Add CLI Tools to PATH

The plugin includes standalone CLI scripts. To use them from anywhere:

```bash
# Add to ~/.zshrc or ~/.bashrc
export PATH="$HOME/path/to/biology-agent/biology-microscopy/scripts:$PATH"

# Then use from anywhere:
microscopy-info /path/to/image.tif
batch-convert-metadata /path/to/folder --format csv
validate-formats /path/to/file.nd2
```

### Optional: Install Additional Format Support

By default, OME-TIFF and ND2 formats are supported. For additional formats:

```bash
# Zeiss CZI files
uvx --from biology-mcp-server[czi] biology-mcp-server

# Leica LIF files
uvx --from biology-mcp-server[lif] biology-mcp-server

# All formats
uvx --from biology-mcp-server[all] biology-mcp-server
```

## 🚀 Usage

### In Claude Code

Once configured, you can use the MCP tools interactively:

```
You: Read metadata from /data/experiment_001.ome.tiff
Claude: [Uses read_microscopy_metadata tool]
        This is a 2048x2048 pixel image with 3 channels (DAPI, GFP, RFP)...

You: What are the physical dimensions?
Claude: [Uses get_physical_dimensions tool]
        The pixel size is 0.065 µm, giving a field of view of 133.1 × 133.1 µm...
```

Use skills for batch operations:

```
You: /extract-metadata-batch
Claude: I'll help you extract metadata from a folder of microscopy files.
        What folder would you like to analyze?
```

### Using CLI Scripts

**Quick file info:**
```bash
microscopy-info /path/to/image.ome.tiff
microscopy-info /path/to/image.nd2 --verbose
microscopy-info /path/to/image.ome.tiff --json
```

**Batch metadata extraction:**
```bash
# Export to CSV
batch-convert-metadata /data/microscopy/ --format csv --output results.csv

# Export to JSON (recursive search)
batch-convert-metadata /data/microscopy/ --format json --recursive
```

**Validate files:**
```bash
# Validate single file
validate-formats /path/to/image.ome.tiff

# Validate entire folder (recursive)
validate-formats /data/microscopy/ --recursive
```

## 🔧 Supported Formats

Through bioio plugins, the toolkit supports:

| Format | Extension | Plugin | Status |
|--------|-----------|--------|--------|
| OME-TIFF | `.ome.tiff`, `.ome.tif` | bioio-ome-tiff | ✅ Installed |
| Nikon ND2 | `.nd2` | bioio-nd2 | ✅ Installed |
| Zeiss CZI | `.czi` | bioio-czi | ⬜ Not installed |
| Leica LIF | `.lif` | bioio-lif | ⬜ Not installed |
| Standard TIFF | `.tiff`, `.tif` | bioio-ome-tiff | ✅ Installed |

To add support for additional formats:

```bash
# Zeiss CZI files
uv pip install bioio-czi

# Leica LIF files
uv pip install bioio-lif
```

See [bioio documentation](https://bioio-devs.github.io/bioio/) for all supported formats.

## 📚 Examples

### Example 1: Validate a Folder of Files

```bash
$ validate-formats /data/experiment_2026/ --recursive

🔍 Searching for microscopy files in: /data/experiment_2026/
   (recursive search enabled)
📁 Found 15 file(s)

[1/15] Validating: sample_01.ome.tiff
------------------------------------------------------------
✅ Valid - Readable by bioio
   Size: 145.3 MB

📊 Summary:
   Dimensions: TCZYX = (10, 3, 5, 2048, 2048)
   Channels: 3
   Timepoints: 10
   Z-slices: 5

...

📊 VALIDATION SUMMARY
============================================================
Total files: 15
✅ Valid: 14
❌ Invalid: 1
⚠️  Total warnings: 3
```

### Example 2: Extract Metadata to CSV

```bash
$ batch-convert-metadata /data/experiment_2026/ --format csv --output metadata.csv

🔍 Searching for microscopy files in: /data/experiment_2026/
📁 Found 15 file(s)

Processing [1/15]: sample_01.ome.tiff...
  ✓ Success
Processing [2/15]: sample_02.ome.tiff...
  ✓ Success
...

✅ Saved CSV to: metadata.csv

📊 Summary: 14 successful, 1 failed
```

Then open `metadata.csv` in Excel/Sheets for analysis!

### Example 3: Interactive Analysis in Claude Code

```
You: Analyze the file /data/experiment_2026/sample_01.ome.tiff

Claude: [Uses validate_microscopy_file and read_microscopy_metadata]

# Microscopy File Analysis

## File: sample_01.ome.tiff

### Overview
- **Size:** 145.3 MB
- **Format:** OME-TIFF
- **Status:** ✅ Valid

### Dimensions
- **Shape:** (10, 3, 5, 2048, 2048)
- **Timepoints:** 10
- **Channels:** 3 (DAPI, GFP, RFP)
- **Z-slices:** 5
- **XY:** 2048 × 2048 pixels

### Physical Calibration
- **Pixel Size:** 0.065 µm × 0.065 µm
- **Z-spacing:** 0.2 µm
- **Field of View:** 133.1 × 133.1 µm

### Suggested Next Steps
This is a 4D dataset (time-lapse with Z-stacks). Consider:
1. Creating maximum projections for each timepoint
2. Tracking objects across time
3. Analyzing channel colocalization
```

## 🧪 Testing

### Test the MCP Server

```bash
# Test via uvx (recommended)
uvx --from ./biology-microscopy/mcp-server biology-mcp-server

# Or install and run locally
cd biology-microscopy/mcp-server
uv pip install -e .
biology-mcp-server
```

The server will listen for MCP protocol messages on stdin. Press Ctrl+C to stop.

### Verify Plugin Installation

In Claude Code:
```
/mcp
# Should show "biology" server as connected
```

### Test with Sample Files

If you don't have microscopy files, you can download test data:

**OME-TIFF samples:**
- [OME-TIFF sample files](https://downloads.openmicroscopy.org/images/)

**Create a simple test:**
```python
from bioio import BioImage
import numpy as np
from bioio_ome_tiff import OmeTiffWriter

# Create test data
data = np.random.randint(0, 255, (3, 512, 512), dtype=np.uint8)

# Write as OME-TIFF
writer = OmeTiffWriter("test_image.ome.tiff")
writer.write_image(data, "CYX", channel_names=["DAPI", "GFP", "RFP"])

print("Created test_image.ome.tiff")
```

Then test:
```bash
microscopy-info test_image.ome.tiff
```

## 🐛 Troubleshooting

### MCP Server Not Found in Claude Code

**Issue:** Claude Code doesn't see the biology MCP server.

**Solutions:**
1. Run `/mcp` in Claude Code to check server status
2. Ensure `uv` is installed (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
3. Restart Claude Code completely after plugin installation
4. Test server manually: `uvx --from ./biology-microscopy/mcp-server biology-mcp-server`

### Import Errors

**Issue:** `ModuleNotFoundError: No module named 'bioio'`

**Solution:**
The uvx command should handle dependencies automatically. If issues persist:
```bash
# Clear uvx cache and retry
uvx cache clean
```

### File Format Not Supported

**Issue:** `bioio.exceptions.UnsupportedFileFormatError`

**Solution:**
Install the appropriate plugin extras:
```bash
# Install with all format support
uvx --from "biology-mcp-server[all]" biology-mcp-server
```

### Permission Errors on Scripts

**Issue:** `Permission denied` when running CLI scripts

**Solution:**
```bash
chmod +x biology-microscopy/scripts/microscopy-info
chmod +x biology-microscopy/scripts/batch-convert-metadata
chmod +x biology-microscopy/scripts/validate-formats
```

## 🔮 Future Enhancements

Planned features for future releases:

- **Image processing tools**: Crop, filter, registration, segmentation
- **Visualization**: Maximum projections, channel overlays, 3D rendering
- **Analysis integration**: scikit-image, napari, CellProfiler
- **Additional formats**: More bioio plugins (CZI, LIF, VSI)
- **Batch processing**: Parallel processing for large datasets
- **Export formats**: OME-ZARR, HDF5 for cloud storage

## 📖 Resources

- [bioio Documentation](https://bioio-devs.github.io/bioio/)
- [OME-TIFF Specification](https://docs.openmicroscopy.org/ome-model/latest/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [Claude Code](https://github.com/anthropics/claude-code)

## 📄 License

[Add your license here]

## 🤝 Contributing

Contributions welcome! Please open an issue or PR.

## Support

For issues or questions:
1. Check the Troubleshooting section above
2. Open an issue on GitHub
3. Consult the bioio documentation

---

**Built with ❤️ for the biology research community**
