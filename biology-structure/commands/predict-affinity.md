---
name: predict-affinity
description: Predict binding affinity between a protein and small molecule ligand
argument-hint: "[protein sequence] [ligand SMILES]"
allowed-tools: ["Read", "Write", "mcp__biology-structure__predict_binding_affinity", "mcp__biology-structure__validate_input", "mcp__biology-structure__get_prediction_status"]
---

# Predict Binding Affinity

Predict the binding affinity (delta G) between a protein and small molecule ligand using Boltz-2.

## Input Handling

Parse the user's input for:
1. **Protein sequence**: Amino acid sequence or file path
2. **Ligand SMILES**: SMILES string representing the small molecule

If inputs are missing, prompt the user for:
- Protein sequence (or file path to FASTA)
- Ligand SMILES (or help them find it on PubChem)

## Workflow

1. **Validate inputs** using `validate_input`
   - Check protein sequence validity
   - Verify SMILES format

2. **Check API availability** using `get_prediction_status`
   - Binding affinity requires cloud API

3. **Run prediction** using `predict_binding_affinity`
   - Save docked structure to `./docking/` directory

4. **Interpret results**:
   - Report delta G in kcal/mol
   - Convert to approximate Kd
   - Assess binding strength (weak/moderate/strong)

## Example Usage

```
/predict-affinity MKTVRQERLKSIVRIL... CC(=O)OC1=CC=CC=C1C(=O)O

/predict-affinity ./protein.fasta "aspirin SMILES"
```

## Output

Report:
- Delta G (kcal/mol)
- Estimated Kd
- Binding strength assessment
- Path to docked structure file
