---
name: Analyze Microscopy File
description: Perform comprehensive analysis of a single microscopy file with visualization and validation
invocation: analyze-microscopy-file
---

# Analyze Microscopy File

This skill provides comprehensive analysis of a single microscopy image file, including metadata extraction, validation, and suggestions for next steps.

## When to Use This Skill

Use this skill when you need to:
- Understand a new microscopy file
- Validate acquisition parameters
- Check for data quality issues
- Plan analysis workflows

## What This Skill Does

When invoked, this skill will:

1. **Ask for the file path** to analyze
2. **Validate the file** using bioio
3. **Extract comprehensive metadata**
4. **Identify potential issues** (missing metadata, unusual dimensions, etc.)
5. **Suggest next steps** for analysis

## Workflow

### Step 1: Get File Path
Ask the user for the microscopy file path. Validate that the file exists.

### Step 2: Validate File
Use the MCP tool `validate_microscopy_file` to:
- Check if file exists and is readable
- Verify bioio can open it
- Identify any immediate issues

### Step 3: Extract Full Metadata
Use `read_microscopy_metadata` to get complete information:
- All dimensions (T, C, Z, Y, X)
- Channel names and properties
- Physical pixel sizes
- Scene information
- Format-specific metadata

### Step 4: Analyze and Report

Create a comprehensive report including:

**File Information:**
- File name and path
- File size
- Format detected

**Dimensions:**
- Image dimensions with clear labels
- Number of timepoints, channels, Z-slices
- XY dimensions in pixels
- Physical dimensions in micrometers (if available)

**Channels:**
- List all channels with names
- Note if channel names are generic (e.g., "Channel_0")

**Physical Calibration:**
- Pixel sizes in X, Y, Z
- Calculate total image size in micrometers
- Flag if pixel sizes are missing

**Multi-Scene Support:**
- List all scenes if present
- Note current active scene

**Quality Checks:**
- ✅ Has physical pixel sizes
- ⚠️  Missing Z pixel size
- ❌ Generic channel names
- ✅ Reasonable dimensions

### Step 5: Suggest Next Steps

Based on the analysis, suggest relevant workflows:

**For time-series data (T > 1):**
- "This appears to be a time-lapse. Consider analyzing dynamics over time."

**For multi-channel data (C > 1):**
- "Multiple channels detected. You might want to analyze channel colocalization or separate channels for individual analysis."

**For Z-stacks (Z > 1):**
- "This is a 3D volume. Consider creating maximum intensity projections or 3D reconstructions."

**For missing metadata:**
- "Physical pixel sizes are missing. You may need to manually set the scale for quantitative measurements."

## Example Output

```markdown
# Microscopy File Analysis

## File: experiment_001.ome.tiff

### Overview
- **Path:** /data/microscopy/experiment_001.ome.tiff
- **Size:** 145.3 MB
- **Format:** OME-TIFF
- **Status:** ✅ Valid and readable

### Dimensions
- **Order:** TCZYX
- **Shape:** (10, 3, 5, 2048, 2048)
- **Timepoints (T):** 10 frames
- **Channels (C):** 3
- **Z-slices (Z):** 5 slices
- **XY Size:** 2048 × 2048 pixels

### Channels
1. **DAPI** - Nuclear stain
2. **GFP** - Protein of interest
3. **RFP** - Marker protein

### Physical Calibration
- **Pixel Size (XY):** 0.065 µm/pixel
- **Pixel Size (Z):** 0.2 µm/slice
- **Field of View:** 133.1 × 133.1 µm
- **Z-depth:** 1.0 µm (5 slices × 0.2 µm)

### Quality Assessment
✅ All metadata present
✅ Physical pixel sizes available
✅ Named channels
✅ Reasonable dimensions

### Suggested Next Steps
1. **Time-lapse analysis**: Track objects across 10 timepoints
2. **Multi-channel analysis**: Analyze colocalization between DAPI, GFP, and RFP
3. **3D rendering**: Create maximum intensity projections from Z-stack
4. **Export**: Consider extracting specific channels or timepoints for focused analysis
```

## Tips

- **Be thorough but concise**: Focus on actionable information
- **Flag issues clearly**: Use ✅ ⚠️ ❌ to highlight quality checks
- **Context matters**: Tailor suggestions to the data type (time-lapse, Z-stack, etc.)
- **Validate assumptions**: If something looks unusual (e.g., 1000 timepoints), mention it

## Alternative: Use CLI for Quick Checks

For quick file inspection without opening Claude Code:
```bash
microscopy-info /path/to/file.ome.tiff --verbose
```

Or validate multiple files:
```bash
validate-formats /path/to/folder --recursive
```
