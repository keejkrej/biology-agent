---
name: boltz-status
description: Check the status of Boltz structure prediction services (cloud API and local GPU)
allowed-tools: ["mcp__biology-structure__get_prediction_status"]
---

# Check Boltz Service Status

Check the availability and configuration of structure prediction services.

## Workflow

1. Call `get_prediction_status` to check both services

2. Report status for each service:

**Cloud (NVIDIA NIM)**:
- API key configured: Yes/No
- Service available: Yes/No
- Error message if any

**Local (GPU)**:
- Boltz installed: Yes/No
- GPU available: Yes/No
- GPU name and VRAM (if available)

3. Recommend the best mode based on availability

## Troubleshooting Guidance

If cloud is unavailable:
- Guide user to get API key from build.nvidia.com
- Show how to set NVIDIA_API_KEY environment variable

If local is unavailable:
- Show installation command: `pip install boltz torch`
- Check CUDA availability

## Example Output

```
Boltz Service Status
====================

Cloud (NVIDIA NIM):
  API Key: Configured
  Status: Available

Local (GPU):
  Boltz: Installed (v1.0.0)
  GPU: NVIDIA RTX 5090 (32GB)
  Status: Available

Recommended: Cloud mode (faster, handles larger structures)
```
