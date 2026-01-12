# Biology Agent - Microscopy Data Analysis Toolkit

A comprehensive toolkit for analyzing microscopy image data in Claude Code, built on [bioio](https://bioio-devs.github.io/bioio/).

## 📁 Repository Structure

```
biology-agent/
├── plugin/              # Plugin files (installed to ~/.claude/plugins/repos/)
│   ├── .claude-plugin/  # Plugin metadata
│   ├── .mcp.json        # MCP server configuration
│   ├── mcp-server/      # Python MCP server
│   ├── scripts/         # CLI tools
│   └── skills/          # Claude Code skills
├── tests/               # Test files and examples
├── install.sh           # Installation script
└── README.md
```

**Note:** The `plugin/` directory contains all files that get installed globally. This keeps your development workspace clean - Claude will use the installed version from `~/.claude/plugins/repos/biology-microscopy`, not the local files.

## 🎯 What Is This?

The Biology Agent provides an interactive microscopy data analysis assistant that integrates seamlessly with Claude Code. It enables you to:

- 📊 **Read metadata** from microscopy files (OME-TIFF, Nikon ND2, Zeiss CZI, etc.)
- 🔍 **Validate files** and check for data quality issues
- 📁 **Batch process** folders of images for metadata extraction
- 🎨 **Analyze images** interactively using natural language
- 🛠️ **Use standalone tools** for automation outside Claude Code

## 🏗️ Architecture

The toolkit uses a **hybrid approach** combining three components:

### 1. MCP Server (`plugin/mcp-server/`)
Exposes bioio capabilities as tools that Claude Code can call directly:
- `read_microscopy_metadata` - Extract complete metadata
- `get_image_info` - Quick summary information
- `list_scenes` - Multi-scene file support
- `get_channel_info` - Channel details
- `get_physical_dimensions` - Physical sizes in micrometers
- `validate_microscopy_file` - File validation and quality checks

### 2. Claude Code Skills (`plugin/skills/`)
Pre-packaged workflows for common tasks:
- `/extract-metadata-batch` - Process folders of files
- `/analyze-microscopy-file` - Comprehensive single-file analysis

### 3. Helper CLI Scripts (`plugin/scripts/`)
Standalone command-line tools:
- `microscopy-info` - Display file metadata
- `batch-convert-metadata` - Export metadata to CSV/JSON
- `validate-formats` - Validate bioio compatibility

## 📦 Installation

### ⚡ Quick Install (Recommended)

**One command to set up everything:**

```bash
# Clone and install
git clone <your-repo-url> ~/workspace/biology-agent
cd ~/workspace/biology-agent
./install.sh
```

The installer automatically:
- ✅ Checks for Python 3.12+ and uv
- ✅ Creates virtual environment
- ✅ Installs dependencies (bioio, fastmcp, plugins)
- ✅ Sets up Claude Code plugin
- ✅ Makes CLI scripts executable
- ✅ Tests the MCP server

**After installation: Restart Claude Code** (quit completely and reopen).

### Prerequisites

- **[uv](https://github.com/astral-sh/uv)** - Fast Python package manager
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
- **[Claude Code](https://github.com/anthropics/claude-code)**

### Optional: Add CLI Tools to PATH

```bash
# Add to ~/.zshrc or ~/.bashrc
export PATH="$HOME/workspace/biology-agent/scripts:$PATH"

# Then use from anywhere:
microscopy-info /path/to/image.tif
batch-convert-metadata /path/to/folder --format csv
validate-formats /path/to/file.nd2
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
# Activate the virtual environment
source .venv/bin/activate

# Run the server (it should start without errors)
python mcp-server/server.py
```

The server will listen for MCP protocol messages on stdin. Press Ctrl+C to stop.

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
1. Check the config file path: `~/.config/claude/config.json`
2. Verify paths are absolute (no `~` in JSON)
3. Restart Claude Code after config changes
4. Check server starts: `python mcp-server/server.py`

### Import Errors

**Issue:** `ModuleNotFoundError: No module named 'bioio'`

**Solution:**
```bash
# Make sure you're in the virtual environment
source .venv/bin/activate

# Reinstall dependencies
uv pip install -r mcp-server/requirements.txt
```

### File Format Not Supported

**Issue:** `bioio.exceptions.UnsupportedFileFormatError`

**Solution:**
Install the appropriate plugin:
```bash
# For CZI files
uv pip install bioio-czi

# For LIF files
uv pip install bioio-lif
```

### Permission Errors on Scripts

**Issue:** `Permission denied` when running scripts

**Solution:**
```bash
chmod +x scripts/microscopy-info
chmod +x scripts/batch-convert-metadata
chmod +x scripts/validate-formats
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
