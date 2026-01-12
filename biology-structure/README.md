# biology-structure

Biomolecular structure prediction plugin for Claude Code using Boltz-2.

Predict 3D structures of proteins, DNA, RNA, and biomolecular complexes. Supports both NVIDIA NIM cloud API and local GPU execution.

## Features

- **Structure Prediction**: Predict 3D structures of proteins, DNA, RNA, and multi-chain complexes
- **Binding Affinity**: Predict protein-ligand binding affinity (delta G)
- **Dual Mode**: Cloud API (NVIDIA NIM) or local GPU execution
- **Validation**: Input validation with resource estimation

## Prerequisites

### Cloud Mode (Recommended)

1. Get an API key from [NVIDIA NIM](https://build.nvidia.com/mit/boltz2)
2. Set the environment variable:
   ```bash
   export NVIDIA_API_KEY="your-api-key-here"
   ```

### Local Mode (Optional)

For local GPU execution (RTX 5090 or similar):

```bash
pip install boltz torch
```

Requirements:
- NVIDIA GPU with CUDA support
- 24GB+ VRAM recommended (32GB for larger proteins)
- CUDA 12.0+

## Installation

### Via Marketplace

```bash
/plugin marketplace add keejkrej/biology-agent
/plugin install biology-structure@keejkrej
```

### Local Development

```bash
/plugin  # Select "Add local plugin" -> select biology-structure/
```

## Usage

### Commands

| Command | Description |
|---------|-------------|
| `/predict-structure [sequence]` | Predict 3D structure |
| `/predict-affinity [protein] [ligand]` | Predict binding affinity |
| `/boltz-status` | Check service availability |

### MCP Tools

The plugin provides these MCP tools:

- `predict_structure` - Predict biomolecular structure
- `predict_binding_affinity` - Predict protein-ligand binding
- `get_prediction_status` - Check service status
- `validate_input` - Validate sequences and ligands

### Example: Predict Protein Structure

```
/predict-structure MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG
```

### Example: Predict Binding Affinity

```
/predict-affinity MKTVRQERLKSIVRIL... CC(=O)OC1=CC=CC=C1C(=O)O
```

## Configuration

Create `.claude/biology-structure.local.md` for persistent settings:

```yaml
---
mode: cloud  # or "local"
output_dir: ./structures
nvidia_api_key_env: NVIDIA_API_KEY
---
```

## Output Formats

- **Structure files**: mmCIF format (`.cif`)
- **Viewable in**: PyMOL, ChimeraX, Mol*

## Supported Input

| Type | Format | Example |
|------|--------|---------|
| Protein | Amino acids (A-Y) | `MKTVRQERLKSIVRIL...` |
| DNA | Nucleotides (ATCG) | `ATCGATCGATCG...` |
| RNA | Nucleotides (AUCG) | `AUCGAUCGAUCG...` |
| Ligand | SMILES | `CC(=O)OC1=CC=CC=C1C(=O)O` |

## Limitations

- Maximum 4,096 residues per chain
- Maximum 12 chains per prediction
- Binding affinity requires cloud API
- Local mode limited by GPU VRAM

## Resources

- [NVIDIA NIM Boltz-2](https://build.nvidia.com/mit/boltz2)
- [Boltz GitHub](https://github.com/jwohlwend/boltz)
- [NVIDIA NIM Documentation](https://docs.nvidia.com/nim/bionemo/boltz2/latest/)

## License

MIT License
