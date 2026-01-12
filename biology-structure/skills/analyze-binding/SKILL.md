---
name: analyze-binding
description: This skill should be used when the user wants to analyze protein-ligand binding, predict binding affinity, perform molecular docking, or understand drug-protein interactions. Use this when the user mentions "binding affinity", "drug docking", "ligand binding", "delta G", "binding energy", or wants to understand how small molecules interact with proteins.
---

# Binding Affinity Analysis Workflow

Guide the user through predicting and analyzing protein-ligand binding using Boltz-2's binding affinity prediction capabilities.

## Overview

Boltz-2 can predict:
- **Binding affinity** (delta G in kcal/mol)
- **Binding pose** (3D structure of protein-ligand complex)
- **Confidence metrics** for the prediction

This is useful for:
- Drug discovery screening
- Understanding drug-target interactions
- Comparing binding of different ligands
- Validating computational docking results

## Step 1: Gather Protein Information

Collect the target protein sequence:

1. **Protein sequence**: Amino acid sequence (one-letter codes)
2. **Binding site** (optional): If known, identify the binding pocket region

Accept input as:
- Raw sequence string
- FASTA format
- UniProt ID (help user fetch sequence)
- PDB ID (extract sequence from structure)

## Step 2: Gather Ligand Information

Collect the ligand as a SMILES string:

**What is SMILES?**
SMILES (Simplified Molecular Input Line Entry System) is a text representation of molecular structure.

Examples:
| Molecule | SMILES |
|----------|--------|
| Aspirin | `CC(=O)OC1=CC=CC=C1C(=O)O` |
| Caffeine | `CN1C=NC2=C1C(=O)N(C(=O)N2C)C` |
| Glucose | `OC[C@H]1OC(O)[C@H](O)[C@@H](O)[C@@H]1O` |

Help users find SMILES:
- PubChem: Search by name, copy SMILES
- ChEMBL: Drug database with SMILES
- DrugBank: Pharmaceutical database

## Step 3: Validate Inputs

Use `validate_input` to check:

```
validate_input(
    sequences=[{"id": "A", "molecule_type": "protein", "sequence": "..."}],
    ligands=[{"smiles": "..."}]
)
```

Common SMILES issues:
- Unbalanced parentheses or brackets
- Invalid atom symbols
- Missing bonds

## Step 4: Run Binding Prediction

Use `predict_binding_affinity`:

```python
predict_binding_affinity(
    protein_sequence="MKTVRQERLKSIVRIL...",
    ligand_smiles="CC(=O)OC1=CC=CC=C1C(=O)O",
    output_path="./docking/complex.cif"
)
```

This runs on NVIDIA NIM cloud API (requires API key).

## Step 5: Interpret Binding Affinity

**Understanding delta G values:**

| Delta G (kcal/mol) | Kd (approximate) | Binding Strength |
|--------------------|------------------|------------------|
| -6 | ~40 uM | Weak |
| -8 | ~1 uM | Moderate |
| -10 | ~30 nM | Strong |
| -12 | ~1 nM | Very strong |
| -14 | ~30 pM | Extremely strong |

**Context matters:**
- Drug candidates typically need Kd < 1 uM
- Enzyme inhibitors often need nM range
- Some therapeutics work at uM range

## Step 6: Analyze the Complex Structure

The output mmCIF file contains the docked structure. Guide the user to:

1. **View in molecular viewer**:
   - PyMOL: `load complex.cif`
   - ChimeraX: `open complex.cif`

2. **Identify interactions**:
   - Hydrogen bonds
   - Hydrophobic contacts
   - Pi-stacking
   - Salt bridges

3. **Check binding pose quality**:
   - Is ligand in a reasonable pocket?
   - Are interactions chemically sensible?

## Common Use Cases

### Screen multiple ligands
```
User: "I want to test 5 different compounds against my protein"
-> Loop through predict_binding_affinity for each ligand
-> Compare delta G values
-> Rank by binding strength
```

### Compare to known drugs
```
User: "How does my compound compare to ibuprofen?"
-> Run prediction for both compounds
-> Compare delta G and binding poses
```

### Understand binding mechanism
```
User: "Why does this drug bind strongly?"
-> Predict structure
-> Analyze binding pocket interactions
-> Identify key residues involved
```

## Limitations

1. **Accuracy**: Predictions are estimates, not experimental values
   - Use for ranking compounds, not absolute affinity
   - Validate important predictions experimentally

2. **Protein flexibility**: Model assumes rigid protein
   - May miss induced-fit binding
   - Consider multiple conformations for flexible targets

3. **Covalent binding**: Not supported
   - Model handles non-covalent interactions only

4. **Large ligands**: May have reduced accuracy
   - Best for drug-like molecules (MW < 500)

## Tips for Better Predictions

1. **Use full-length protein** when possible
   - Context helps binding site identification

2. **Provide correct protonation state** in SMILES
   - Charged groups affect binding

3. **Consider multiple binding modes**
   - Run multiple predictions if unsure

4. **Validate with known data**
   - Test on compounds with known binding affinity first
