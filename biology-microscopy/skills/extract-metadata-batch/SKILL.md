---
name: Extract Metadata Batch
description: Extract metadata from all microscopy files in a folder and create a summary report
invocation: extract-metadata-batch
---

# Extract Metadata from Microscopy Files (Batch)

This skill helps you extract metadata from multiple microscopy files in a folder and create comprehensive summary reports.

## When to Use This Skill

Use this skill when you need to:
- Analyze a folder of microscopy images
- Create a metadata summary for multiple files
- Compare acquisition parameters across experiments
- Generate reports for documentation or analysis

## What This Skill Does

When invoked, this skill will:

1. **Ask for the folder path** containing microscopy files
2. **Scan for microscopy files** (OME-TIFF, ND2, CZI, etc.)
3. **Extract metadata from each file** using the biology MCP server tools
4. **Create a summary report** with key information
5. **Offer export options** (CSV, JSON, or formatted report)

## Workflow

### Step 1: Get Folder Path
Ask the user for the directory containing microscopy files. Use the MCP file system tools or ask them to provide the path.

### Step 2: Find Microscopy Files
Use file system tools to find all microscopy files. Look for these extensions:
- `.tiff`, `.tif`, `.ome.tiff`, `.ome.tif` (OME-TIFF files)
- `.nd2` (Nikon files)
- `.czi` (Zeiss files)
- `.lif` (Leica files)

### Step 3: Extract Metadata
For each file found, call the MCP tool `read_microscopy_metadata` or `get_image_info` to extract:
- Dimensions (TCZYX)
- Channel information
- Physical pixel sizes
- Timepoints and Z-slices
- Scene information (if multi-scene)

### Step 4: Aggregate Results
Create a structured summary with:
- File name
- Dimensions
- Number of channels and channel names
- Pixel sizes in micrometers
- Any warnings or errors

### Step 5: Offer Export Options
Ask the user how they want the results:

**CSV Export** (for spreadsheet analysis):
- Create a CSV file with one row per file
- Columns: filename, dimensions, channels, pixel_size_x, pixel_size_y, pixel_size_z, timepoints, z_slices

**JSON Export** (for programmatic use):
- Create a structured JSON file with complete metadata

**Formatted Report** (for documentation):
- Create a markdown report with:
  - Summary statistics
  - Table of files
  - Any issues or warnings found

## Example Output Structure

```markdown
# Microscopy Metadata Report

**Generated:** 2026-01-12

## Summary
- Total files: 15
- Successfully read: 14
- Errors: 1

## File Details

| File | Dimensions | Channels | Pixel Size (µm) | Timepoints | Z-slices |
|------|------------|----------|-----------------|------------|----------|
| image001.ome.tiff | 2048x2048 | 3 (DAPI, GFP, RFP) | 0.065 x 0.065 | 10 | 5 |
| image002.nd2 | 1024x1024 | 2 (GFP, mCherry) | 0.13 x 0.13 | 1 | 1 |
...
```

## Tips

- **Performance**: For large numbers of files, show progress as you go
- **Error Handling**: If a file fails, note it in the report but continue with others
- **Validation**: Mention if any files are missing critical metadata (e.g., pixel sizes)
- **Comparison**: If all files have similar parameters, highlight any outliers

## Alternative: Use the CLI Script

For batch processing outside of Claude Code, users can also use:
```bash
batch-convert-metadata /path/to/folder --format csv --output results.csv
```

This is useful for automation or when Claude Code isn't needed for the analysis.
