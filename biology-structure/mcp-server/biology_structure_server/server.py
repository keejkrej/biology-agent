"""
Biology Structure MCP Server

Provides tools for biomolecular structure prediction using Boltz-2.
Supports NVIDIA NIM cloud API and local GPU execution.
"""

import os
from typing import Optional, Dict, Any, List

from fastmcp import FastMCP

from .nvidia_nim import NvidiaNimClient, Polymer, Ligand, NvidiaAPIError
from .local_boltz import LocalBoltzRunner, check_gpu_available, estimate_vram_requirement
from .utils import (
    validate_sequence,
    validate_smiles,
    save_structure,
    generate_output_path,
    estimate_prediction_time,
    parse_fasta
)


# Initialize FastMCP server
mcp = FastMCP("Biology Structure Server")

# Global clients (lazy initialized)
_nim_client: Optional[NvidiaNimClient] = None
_local_runner: Optional[LocalBoltzRunner] = None


def get_nim_client() -> NvidiaNimClient:
    """Get or create NVIDIA NIM client."""
    global _nim_client
    if _nim_client is None:
        _nim_client = NvidiaNimClient()
    return _nim_client


def get_local_runner() -> LocalBoltzRunner:
    """Get or create local Boltz runner."""
    global _local_runner
    if _local_runner is None:
        _local_runner = LocalBoltzRunner()
    return _local_runner


@mcp.tool()
def predict_structure(
    sequences: List[Dict[str, Any]],
    ligands: Optional[List[Dict[str, str]]] = None,
    output_path: Optional[str] = None,
    mode: str = "cloud"
) -> Dict[str, Any]:
    """
    Predict 3D structure of a biomolecular complex using Boltz-2.

    Args:
        sequences: List of polymers, each with:
            - id: Chain identifier (e.g., "A", "B")
            - molecule_type: "protein", "dna", or "rna"
            - sequence: Amino acid or nucleotide sequence
        ligands: Optional list of ligands, each with:
            - smiles: SMILES string of the molecule
        output_path: Path to save the structure file (mmCIF format)
        mode: "cloud" for NVIDIA NIM API, "local" for local GPU

    Returns:
        Dictionary with:
        - success: Whether prediction succeeded
        - structure: Structure in mmCIF format (if not saved to file)
        - output_file: Path to saved file (if output_path provided)
        - confidence_scores: Per-residue confidence metrics
        - binding_affinity: Predicted binding affinity (if ligands provided)

    Example:
        >>> predict_structure(
        ...     sequences=[{"id": "A", "molecule_type": "protein", "sequence": "MKTVRQERLKSIVRIL..."}],
        ...     ligands=[{"smiles": "CC(=O)OC1=CC=CC=C1C(=O)O"}],
        ...     output_path="./structures/complex.cif"
        ... )
    """
    # Validate inputs
    validation_errors = []
    total_residues = 0

    for seq in sequences:
        is_valid, error = validate_sequence(seq["sequence"], seq["molecule_type"])
        if not is_valid:
            validation_errors.append(f"Sequence {seq['id']}: {error}")
        total_residues += len(seq["sequence"])

    if ligands:
        for lig in ligands:
            is_valid, error = validate_smiles(lig["smiles"])
            if not is_valid:
                validation_errors.append(f"Ligand SMILES: {error}")

    if validation_errors:
        return {
            "success": False,
            "error": "Validation failed",
            "validation_errors": validation_errors
        }

    # Estimate time
    time_estimate = estimate_prediction_time(
        total_residues=total_residues,
        num_polymers=len(sequences),
        has_ligand=bool(ligands)
    )

    try:
        if mode == "cloud":
            return _predict_cloud(sequences, ligands, output_path, time_estimate)
        elif mode == "local":
            return _predict_local(sequences, output_path, time_estimate)
        else:
            return {
                "success": False,
                "error": f"Unknown mode: {mode}. Use 'cloud' or 'local'"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def _predict_cloud(
    sequences: List[Dict[str, Any]],
    ligands: Optional[List[Dict[str, str]]],
    output_path: Optional[str],
    time_estimate: Dict[str, Any]
) -> Dict[str, Any]:
    """Run prediction via NVIDIA NIM cloud API."""
    client = get_nim_client()

    # Check availability
    status = client.is_available()
    if not status["available"]:
        return {
            "success": False,
            "error": f"NVIDIA NIM not available: {status.get('error')}",
            "hint": "Set NVIDIA_API_KEY environment variable or use mode='local'"
        }

    # Convert to Polymer objects
    polymers = [
        Polymer(id=seq["id"], molecule_type=seq["molecule_type"], sequence=seq["sequence"])
        for seq in sequences
    ]

    # Convert ligands if provided
    lig_objects = None
    if ligands:
        lig_objects = [Ligand(smiles=lig["smiles"]) for lig in ligands]

    # Run prediction
    result = client.predict_structure(polymers, lig_objects)

    # Save structure if output_path provided
    output_info = None
    if output_path and result.structure:
        output_info = save_structure(result.structure, output_path)

    return {
        "success": True,
        "mode": "cloud",
        "structure": result.structure if not output_path else None,
        "output_file": output_info.get("path") if output_info else None,
        "confidence_scores": result.confidence_scores,
        "binding_affinity": result.binding_affinity,
        "runtime_metrics": result.runtime_metrics,
        "time_estimate": time_estimate
    }


def _predict_local(
    sequences: List[Dict[str, Any]],
    output_path: Optional[str],
    time_estimate: Dict[str, Any]
) -> Dict[str, Any]:
    """Run prediction locally on GPU."""
    runner = get_local_runner()

    # Check availability
    status = runner.is_available()
    if not status["available"]:
        return {
            "success": False,
            "error": "Local Boltz not available",
            "details": status,
            "hint": "Install with: pip install boltz torch"
        }

    # Estimate VRAM requirement
    total_residues = sum(len(seq["sequence"]) for seq in sequences)
    vram_estimate = estimate_vram_requirement(total_residues, len(sequences))

    # Run prediction
    result = runner.predict_structure(sequences)

    if not result.success:
        return {
            "success": False,
            "error": result.error,
            "vram_estimate": vram_estimate
        }

    # Save structure if output_path provided
    output_info = None
    if output_path and result.structure:
        output_info = save_structure(result.structure, output_path)

    return {
        "success": True,
        "mode": "local",
        "structure": result.structure if not output_path else None,
        "output_file": output_info.get("path") if output_info else None,
        "confidence_scores": result.confidence_scores,
        "output_dir": result.output_dir,
        "vram_estimate": vram_estimate,
        "time_estimate": time_estimate
    }


@mcp.tool()
def predict_binding_affinity(
    protein_sequence: str,
    ligand_smiles: str,
    output_path: Optional[str] = None,
    protein_id: str = "A"
) -> Dict[str, Any]:
    """
    Predict binding affinity between a protein and small molecule ligand.

    Uses Boltz-2's binding affinity prediction capability to estimate
    the binding free energy (delta G) between a protein and ligand.

    Args:
        protein_sequence: Amino acid sequence of the protein
        ligand_smiles: SMILES string of the ligand molecule
        output_path: Path to save the docked structure
        protein_id: Chain ID for the protein (default "A")

    Returns:
        Dictionary with:
        - success: Whether prediction succeeded
        - binding_affinity: Predicted delta G in kcal/mol
        - structure: Docked complex structure (mmCIF)
        - confidence: Confidence in the prediction

    Example:
        >>> predict_binding_affinity(
        ...     protein_sequence="MKTVRQERLKSIVRIL...",
        ...     ligand_smiles="CC(=O)OC1=CC=CC=C1C(=O)O",
        ...     output_path="./docking/aspirin_complex.cif"
        ... )
    """
    # Validate inputs
    is_valid, error = validate_sequence(protein_sequence, "protein")
    if not is_valid:
        return {"success": False, "error": f"Invalid protein sequence: {error}"}

    is_valid, error = validate_smiles(ligand_smiles)
    if not is_valid:
        return {"success": False, "error": f"Invalid SMILES: {error}"}

    client = get_nim_client()

    # Check availability
    status = client.is_available()
    if not status["available"]:
        return {
            "success": False,
            "error": f"NVIDIA NIM not available: {status.get('error')}",
            "hint": "Set NVIDIA_API_KEY environment variable"
        }

    try:
        result = client.predict_binding_affinity(
            protein_sequence=protein_sequence,
            ligand_smiles=ligand_smiles,
            protein_id=protein_id
        )

        # Save structure if output_path provided
        output_info = None
        if output_path and result.get("structure"):
            output_info = save_structure(result["structure"], output_path)

        return {
            "success": True,
            "binding_affinity": result.get("binding_affinity"),
            "structure": result.get("structure") if not output_path else None,
            "output_file": output_info.get("path") if output_info else None,
            "confidence_scores": result.get("confidence_scores", {})
        }

    except NvidiaAPIError as e:
        return {
            "success": False,
            "error": e.message,
            "status_code": e.status_code
        }


@mcp.tool()
def get_prediction_status() -> Dict[str, Any]:
    """
    Check the status of structure prediction services.

    Returns availability and configuration status for both
    NVIDIA NIM cloud API and local GPU prediction.

    Returns:
        Dictionary with:
        - cloud: NVIDIA NIM API status
        - local: Local GPU/Boltz status
        - recommended_mode: Suggested mode based on availability

    Example:
        >>> get_prediction_status()
    """
    # Check cloud API
    nim_client = get_nim_client()
    cloud_status = nim_client.is_available()

    # Check local GPU
    local_runner = get_local_runner()
    local_status = local_runner.is_available()

    # Determine recommended mode
    if cloud_status["available"]:
        recommended = "cloud"
        reason = "Cloud API is available and handles large complexes efficiently"
    elif local_status["available"]:
        recommended = "local"
        reason = "Cloud API unavailable, using local GPU"
    else:
        recommended = None
        reason = "No prediction service available"

    return {
        "cloud": {
            "available": cloud_status["available"],
            "api_key_configured": cloud_status["api_key_configured"],
            "error": cloud_status.get("error")
        },
        "local": {
            "available": local_status["available"],
            "boltz_installed": local_status.get("boltz", {}).get("installed", False),
            "gpu": local_status.get("gpu", {})
        },
        "recommended_mode": recommended,
        "recommendation_reason": reason
    }


@mcp.tool()
def validate_input(
    sequences: Optional[List[Dict[str, Any]]] = None,
    ligands: Optional[List[Dict[str, str]]] = None,
    fasta_content: Optional[str] = None
) -> Dict[str, Any]:
    """
    Validate sequences and ligands before prediction.

    Checks that all inputs are valid and estimates resource requirements.

    Args:
        sequences: List of polymers (id, molecule_type, sequence)
        ligands: List of ligands (smiles)
        fasta_content: Alternative input as FASTA format string

    Returns:
        Dictionary with:
        - valid: Overall validation result
        - sequences: Per-sequence validation results
        - ligands: Per-ligand validation results
        - estimates: Time and resource estimates

    Example:
        >>> validate_input(
        ...     sequences=[{"id": "A", "molecule_type": "protein", "sequence": "INVALID123"}]
        ... )
    """
    results = {
        "valid": True,
        "sequences": [],
        "ligands": [],
        "estimates": {}
    }

    # Parse FASTA if provided
    if fasta_content:
        parsed = parse_fasta(fasta_content)
        if sequences is None:
            sequences = []
        for seq in parsed:
            # Assume protein if not specified
            sequences.append({
                "id": seq["id"],
                "molecule_type": "protein",
                "sequence": seq["sequence"]
            })

    # Validate sequences
    total_residues = 0
    if sequences:
        for seq in sequences:
            is_valid, error = validate_sequence(seq["sequence"], seq["molecule_type"])
            seq_result = {
                "id": seq["id"],
                "molecule_type": seq["molecule_type"],
                "length": len(seq["sequence"]),
                "valid": is_valid,
                "error": error
            }
            results["sequences"].append(seq_result)
            if not is_valid:
                results["valid"] = False
            total_residues += len(seq["sequence"])

    # Validate ligands
    if ligands:
        for i, lig in enumerate(ligands):
            is_valid, error = validate_smiles(lig["smiles"])
            lig_result = {
                "index": i,
                "smiles": lig["smiles"][:50] + "..." if len(lig["smiles"]) > 50 else lig["smiles"],
                "valid": is_valid,
                "error": error
            }
            results["ligands"].append(lig_result)
            if not is_valid:
                results["valid"] = False

    # Add estimates if valid
    if results["valid"] and sequences:
        results["estimates"]["time"] = estimate_prediction_time(
            total_residues=total_residues,
            num_polymers=len(sequences),
            has_ligand=bool(ligands)
        )
        results["estimates"]["vram"] = estimate_vram_requirement(
            total_residues=total_residues,
            num_chains=len(sequences)
        )

    return results


def main():
    """Run the MCP server with stdio transport."""
    mcp.run()


if __name__ == "__main__":
    main()
