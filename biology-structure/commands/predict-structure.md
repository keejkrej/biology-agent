---
name: predict-structure
description: Predict the 3D structure of proteins, DNA, RNA, or biomolecular complexes using Boltz-2
argument-hint: "[sequence or FASTA file path]"
allowed-tools: ["Read", "Write", "Bash", "mcp__biology-structure__predict_structure", "mcp__biology-structure__validate_input", "mcp__biology-structure__get_prediction_status"]
---

# Predict Biomolecular Structure

Predict the 3D structure of a protein, DNA, RNA, or complex using Boltz-2.

## Input Handling

Parse the user's input to determine:

1. **If a file path is provided**: Read the file (FASTA format expected)
2. **If a raw sequence is provided**: Use directly
3. **If no input**: Ask the user for a sequence

## Workflow

1. **Validate the input** using `validate_input` tool
   - Check sequence validity
   - Estimate time and resources

2. **Check service status** using `get_prediction_status`
   - Verify cloud API or local GPU is available

3. **Run prediction** using `predict_structure`
   - Default to cloud mode unless user specifies local
   - Save output to `./structures/` directory with timestamp

4. **Report results**:
   - Output file location
   - Confidence scores summary
   - Binding affinity (if ligands provided)

## Example Usage

```
/predict-structure MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG

/predict-structure ./sequences/my_protein.fasta

/predict-structure  # Will prompt for sequence
```

## Output

Save structures to `./structures/` directory in mmCIF format. Report:
- File path
- Prediction confidence (pLDDT scores)
- Time taken
