"""
Utility functions for biology-structure plugin.

Includes sequence validation, SMILES validation, and file handling.
"""

import re
import os
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime


# Valid amino acid codes (standard 20 + X for unknown)
VALID_AMINO_ACIDS = set("ACDEFGHIKLMNPQRSTVWYX")

# Valid nucleotide codes
VALID_DNA_BASES = set("ATCGN")
VALID_RNA_BASES = set("AUCGN")

# Maximum sequence length for NVIDIA NIM
MAX_SEQUENCE_LENGTH = 4096


def validate_protein_sequence(sequence: str) -> Tuple[bool, Optional[str]]:
    """
    Validate a protein amino acid sequence.

    Args:
        sequence: Amino acid sequence string

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not sequence:
        return False, "Sequence is empty"

    sequence = sequence.upper().strip()

    if len(sequence) > MAX_SEQUENCE_LENGTH:
        return False, f"Sequence too long ({len(sequence)} chars, max {MAX_SEQUENCE_LENGTH})"

    invalid_chars = set(sequence) - VALID_AMINO_ACIDS
    if invalid_chars:
        return False, f"Invalid amino acid characters: {', '.join(sorted(invalid_chars))}"

    return True, None


def validate_dna_sequence(sequence: str) -> Tuple[bool, Optional[str]]:
    """
    Validate a DNA nucleotide sequence.

    Args:
        sequence: DNA sequence string

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not sequence:
        return False, "Sequence is empty"

    sequence = sequence.upper().strip()

    if len(sequence) > MAX_SEQUENCE_LENGTH:
        return False, f"Sequence too long ({len(sequence)} chars, max {MAX_SEQUENCE_LENGTH})"

    invalid_chars = set(sequence) - VALID_DNA_BASES
    if invalid_chars:
        return False, f"Invalid DNA characters: {', '.join(sorted(invalid_chars))}"

    return True, None


def validate_rna_sequence(sequence: str) -> Tuple[bool, Optional[str]]:
    """
    Validate an RNA nucleotide sequence.

    Args:
        sequence: RNA sequence string

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not sequence:
        return False, "Sequence is empty"

    sequence = sequence.upper().strip()

    if len(sequence) > MAX_SEQUENCE_LENGTH:
        return False, f"Sequence too long ({len(sequence)} chars, max {MAX_SEQUENCE_LENGTH})"

    invalid_chars = set(sequence) - VALID_RNA_BASES
    if invalid_chars:
        return False, f"Invalid RNA characters: {', '.join(sorted(invalid_chars))}"

    return True, None


def validate_sequence(sequence: str, molecule_type: str) -> Tuple[bool, Optional[str]]:
    """
    Validate a sequence based on molecule type.

    Args:
        sequence: Sequence string
        molecule_type: One of "protein", "dna", or "rna"

    Returns:
        Tuple of (is_valid, error_message)
    """
    molecule_type = molecule_type.lower()

    if molecule_type == "protein":
        return validate_protein_sequence(sequence)
    elif molecule_type == "dna":
        return validate_dna_sequence(sequence)
    elif molecule_type == "rna":
        return validate_rna_sequence(sequence)
    else:
        return False, f"Unknown molecule type: {molecule_type}"


def validate_smiles(smiles: str) -> Tuple[bool, Optional[str]]:
    """
    Basic SMILES string validation.

    Note: This is a basic syntactic check. For full validation,
    use a cheminformatics library like RDKit.

    Args:
        smiles: SMILES string

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not smiles:
        return False, "SMILES string is empty"

    smiles = smiles.strip()

    # Check for minimum length
    if len(smiles) < 1:
        return False, "SMILES string is too short"

    # Check for balanced parentheses and brackets
    paren_count = 0
    bracket_count = 0

    for char in smiles:
        if char == '(':
            paren_count += 1
        elif char == ')':
            paren_count -= 1
        elif char == '[':
            bracket_count += 1
        elif char == ']':
            bracket_count -= 1

        if paren_count < 0 or bracket_count < 0:
            return False, "Unbalanced parentheses or brackets in SMILES"

    if paren_count != 0:
        return False, "Unbalanced parentheses in SMILES"
    if bracket_count != 0:
        return False, "Unbalanced brackets in SMILES"

    return True, None


def generate_output_path(
    base_dir: str,
    prefix: str = "structure",
    extension: str = "cif"
) -> str:
    """
    Generate a unique output file path with timestamp.

    Args:
        base_dir: Directory to save the file
        prefix: Filename prefix
        extension: File extension

    Returns:
        Full path to the output file
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{prefix}_{timestamp}.{extension}"
    return os.path.join(base_dir, filename)


def save_structure(
    structure: str,
    output_path: str,
    create_dirs: bool = True
) -> Dict[str, Any]:
    """
    Save a structure to a file.

    Args:
        structure: Structure content (mmCIF format)
        output_path: Path to save the file
        create_dirs: Create parent directories if they don't exist

    Returns:
        Dictionary with save status and file info
    """
    try:
        if create_dirs:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, 'w') as f:
            f.write(structure)

        return {
            "success": True,
            "path": output_path,
            "size_bytes": len(structure)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def parse_fasta(fasta_content: str) -> List[Dict[str, str]]:
    """
    Parse FASTA format content into sequences.

    Args:
        fasta_content: FASTA format string

    Returns:
        List of dicts with 'id' and 'sequence' keys
    """
    sequences = []
    current_id = None
    current_seq = []

    for line in fasta_content.strip().split('\n'):
        line = line.strip()
        if not line:
            continue

        if line.startswith('>'):
            # Save previous sequence if exists
            if current_id is not None:
                sequences.append({
                    "id": current_id,
                    "sequence": ''.join(current_seq)
                })
            # Start new sequence
            current_id = line[1:].split()[0]  # Take first word after >
            current_seq = []
        else:
            current_seq.append(line)

    # Don't forget the last sequence
    if current_id is not None:
        sequences.append({
            "id": current_id,
            "sequence": ''.join(current_seq)
        })

    return sequences


def estimate_prediction_time(
    total_residues: int,
    num_polymers: int,
    has_ligand: bool = False
) -> Dict[str, Any]:
    """
    Estimate prediction time based on input complexity.

    This is a rough estimate - actual times vary based on:
    - Server load
    - GPU type
    - Sequence complexity

    Args:
        total_residues: Total number of residues across all polymers
        num_polymers: Number of polymer chains
        has_ligand: Whether ligand is included

    Returns:
        Dictionary with estimated time range
    """
    # Base time: ~20 seconds for small proteins on NVIDIA NIM
    base_time = 20

    # Add time for residues (roughly linear)
    residue_time = total_residues * 0.1  # ~0.1 sec per residue

    # Add time for complexity (multi-chain)
    if num_polymers > 1:
        complexity_factor = 1.5 + (num_polymers - 1) * 0.3
    else:
        complexity_factor = 1.0

    # Add time for ligand docking
    ligand_time = 30 if has_ligand else 0

    estimated_time = (base_time + residue_time) * complexity_factor + ligand_time

    return {
        "estimated_seconds": int(estimated_time),
        "estimated_minutes": round(estimated_time / 60, 1),
        "confidence": "low" if total_residues > 500 else "medium",
        "note": "Actual time may vary based on server load"
    }
