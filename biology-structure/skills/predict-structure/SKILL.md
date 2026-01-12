---
name: predict-structure
description: This skill should be used when the user wants to predict the 3D structure of proteins, DNA, RNA, or biomolecular complexes. Use this skill when the user mentions "protein folding", "structure prediction", "3D structure", "Boltz", "AlphaFold", or wants to visualize molecular structures. Also use when analyzing protein sequences for structural features.
---

# Structure Prediction Workflow

Guide the user through predicting biomolecular structures using Boltz-2. This workflow handles protein, DNA, RNA, and multi-chain complexes with optional small molecule ligands.

## Step 1: Gather Input Sequences

Collect the sequences to predict. Ask the user for:

1. **Sequence(s)**: Accept one of these formats:
   - Raw sequence string (amino acids for protein, nucleotides for DNA/RNA)
   - FASTA format (single or multiple sequences)
   - File path to a FASTA file

2. **Molecule type** for each sequence:
   - `protein`: Amino acid sequence (letters A-Y)
   - `dna`: DNA nucleotide sequence (A, T, C, G)
   - `rna`: RNA nucleotide sequence (A, U, C, G)

3. **Chain IDs**: Assign identifiers (A, B, C...) if multiple chains

Example input formats:
```
# Single protein
MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG

# FASTA format
>ChainA
MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG
>ChainB
KALTARQQEVFDLIRDHISQTGMPPTRAEIAQRLGFRSPNAAEEHLKALARKGVIEIVSGASRG
```

## Step 2: Validate Input

Before prediction, validate all sequences using the `validate_input` tool:

```
Use the validate_input tool with the sequences to check:
- Sequence validity (correct characters for molecule type)
- Sequence length (max 4,096 residues per chain)
- Resource estimates (time and VRAM requirements)
```

If validation fails, help the user fix the issues.

## Step 3: Check Service Availability

Use `get_prediction_status` to verify prediction services are ready:

```
Use get_prediction_status to check:
- Cloud API availability (requires NVIDIA_API_KEY)
- Local GPU availability (requires boltz package + CUDA)
```

If neither service is available, guide the user to:
- Set `NVIDIA_API_KEY` environment variable for cloud mode
- Install `pip install boltz torch` for local mode

## Step 4: Choose Prediction Mode

Based on availability and input size:

| Input Size | Recommended Mode | Reason |
|------------|------------------|--------|
| Small (<300 residues) | Cloud or Local | Both work well |
| Medium (300-800 residues) | Cloud preferred | Faster, more reliable |
| Large (>800 residues) | Cloud only | May exceed local VRAM |
| With ligands | Cloud only | Binding affinity requires NIM |

Let the user override if they prefer a specific mode.

## Step 5: Run Prediction

Call `predict_structure` with:

```python
predict_structure(
    sequences=[
        {"id": "A", "molecule_type": "protein", "sequence": "..."},
        {"id": "B", "molecule_type": "protein", "sequence": "..."}
    ],
    ligands=[{"smiles": "..."}],  # Optional
    output_path="./structures/prediction.cif",
    mode="cloud"  # or "local"
)
```

## Step 6: Interpret Results

After prediction completes, explain the results:

1. **Structure file**: Saved in mmCIF format, viewable in:
   - PyMOL
   - ChimeraX
   - Mol* (web-based)

2. **Confidence scores**: Interpret pLDDT values:
   - >90: Very high confidence (blue in visualization)
   - 70-90: Confident (cyan)
   - 50-70: Low confidence (yellow)
   - <50: Very low confidence (orange/red)

3. **Binding affinity** (if ligand provided):
   - Reported in kcal/mol
   - More negative = stronger binding

## Common Use Cases

### Predict a single protein structure
```
User: "Predict the structure of this protein: MKTVRQERLKSIVRIL..."
-> Use predict_structure with mode="cloud", one sequence
```

### Predict a protein complex
```
User: "I have two proteins that form a complex"
-> Collect both sequences, use predict_structure with multiple chains
```

### Dock a small molecule
```
User: "How does aspirin bind to my protein?"
-> Use predict_binding_affinity with protein sequence and aspirin SMILES
```

### Use local GPU
```
User: "Run prediction on my local GPU"
-> Set mode="local", check VRAM requirements first
```

## Troubleshooting

**"NVIDIA_API_KEY not configured"**
- User needs to set environment variable with API key from build.nvidia.com

**"Sequence too long"**
- Maximum 4,096 residues per chain
- Consider truncating or using domains

**"VRAM insufficient"**
- Switch to cloud mode for large structures
- Or reduce sequence length for local mode

**"Invalid characters in sequence"**
- Check for numbers or special characters
- Ensure correct molecule type (protein vs DNA vs RNA)
