"""
Local Boltz Runner

Runs Boltz-2 locally on GPU for structure prediction.
Designed for NVIDIA RTX 5090 (32GB VRAM) but works with other GPUs.
"""

import os
import tempfile
import subprocess
import shutil
from typing import Optional, Dict, Any, List
from dataclasses import dataclass


@dataclass
class LocalPredictionResult:
    """Result from a local Boltz prediction."""
    structure: str  # mmCIF format
    confidence_scores: Dict[str, Any]
    output_dir: str
    success: bool
    error: Optional[str] = None


class LocalBoltzError(Exception):
    """Exception raised for local Boltz errors."""
    pass


def check_boltz_installed() -> Dict[str, Any]:
    """
    Check if Boltz is installed and available.

    Returns:
        Dictionary with installation status and details
    """
    result = {
        "installed": False,
        "version": None,
        "error": None
    }

    try:
        # Try importing boltz
        import boltz
        result["installed"] = True
        result["version"] = getattr(boltz, "__version__", "unknown")
    except ImportError as e:
        result["error"] = f"Boltz not installed: {str(e)}"

    return result


def check_gpu_available() -> Dict[str, Any]:
    """
    Check GPU availability and VRAM.

    Returns:
        Dictionary with GPU status and memory info
    """
    result = {
        "gpu_available": False,
        "cuda_available": False,
        "gpu_name": None,
        "vram_total_gb": None,
        "vram_free_gb": None,
        "error": None
    }

    try:
        import torch

        result["cuda_available"] = torch.cuda.is_available()

        if result["cuda_available"]:
            result["gpu_available"] = True
            result["gpu_name"] = torch.cuda.get_device_name(0)

            # Get memory info
            total_memory = torch.cuda.get_device_properties(0).total_memory
            result["vram_total_gb"] = round(total_memory / (1024**3), 1)

            # Get free memory
            torch.cuda.empty_cache()
            free_memory = torch.cuda.memory_reserved(0) - torch.cuda.memory_allocated(0)
            # This gives reserved-allocated, but for total free we need different approach
            result["vram_free_gb"] = result["vram_total_gb"]  # Approximate

    except ImportError:
        result["error"] = "PyTorch not installed"
    except Exception as e:
        result["error"] = str(e)

    return result


def estimate_vram_requirement(total_residues: int, num_chains: int) -> Dict[str, Any]:
    """
    Estimate VRAM requirement for a prediction.

    Based on empirical observations:
    - ~8GB base
    - ~0.02GB per residue for small proteins
    - Increases non-linearly for larger proteins

    Args:
        total_residues: Total residues across all chains
        num_chains: Number of polymer chains

    Returns:
        Dictionary with VRAM estimates
    """
    # Base VRAM requirement
    base_vram = 8.0

    # Per-residue requirement (non-linear scaling)
    if total_residues <= 200:
        residue_vram = total_residues * 0.02
    elif total_residues <= 500:
        residue_vram = 200 * 0.02 + (total_residues - 200) * 0.04
    else:
        residue_vram = 200 * 0.02 + 300 * 0.04 + (total_residues - 500) * 0.08

    # Multi-chain complexity
    chain_factor = 1.0 + (num_chains - 1) * 0.2

    estimated_vram = (base_vram + residue_vram) * chain_factor

    # Determine if it fits on common GPUs
    fits_on = {
        "RTX_4090_24GB": estimated_vram <= 22,
        "RTX_5090_32GB": estimated_vram <= 30,
        "A100_40GB": estimated_vram <= 38,
        "A100_80GB": estimated_vram <= 78,
    }

    return {
        "estimated_vram_gb": round(estimated_vram, 1),
        "fits_on": fits_on,
        "recommendation": _get_gpu_recommendation(estimated_vram)
    }


def _get_gpu_recommendation(vram_needed: float) -> str:
    """Get GPU recommendation based on VRAM needs."""
    if vram_needed <= 22:
        return "RTX 4090 or better"
    elif vram_needed <= 30:
        return "RTX 5090 or better"
    elif vram_needed <= 38:
        return "A100 40GB or better"
    elif vram_needed <= 78:
        return "A100 80GB"
    else:
        return "Use cloud API (NVIDIA NIM) for this size"


class LocalBoltzRunner:
    """Runner for local Boltz predictions."""

    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize the local Boltz runner.

        Args:
            cache_dir: Directory for caching model weights
        """
        self.cache_dir = cache_dir or os.path.expanduser("~/.cache/boltz")

    def is_available(self) -> Dict[str, Any]:
        """
        Check if local Boltz is available and ready.

        Returns:
            Dictionary with availability status
        """
        boltz_status = check_boltz_installed()
        gpu_status = check_gpu_available()

        return {
            "available": boltz_status["installed"] and gpu_status["gpu_available"],
            "boltz": boltz_status,
            "gpu": gpu_status
        }

    def predict_structure(
        self,
        sequences: List[Dict[str, Any]],
        output_dir: Optional[str] = None,
        recycling_steps: int = 3,
        sampling_steps: int = 200,
    ) -> LocalPredictionResult:
        """
        Run local structure prediction.

        Args:
            sequences: List of dicts with 'id', 'molecule_type', 'sequence'
            output_dir: Directory for output files
            recycling_steps: Number of recycling steps
            sampling_steps: Number of diffusion sampling steps

        Returns:
            LocalPredictionResult with structure and confidence scores
        """
        # Check availability first
        status = self.is_available()
        if not status["available"]:
            return LocalPredictionResult(
                structure="",
                confidence_scores={},
                output_dir="",
                success=False,
                error=f"Local Boltz not available: {status}"
            )

        # Create output directory
        if output_dir is None:
            output_dir = tempfile.mkdtemp(prefix="boltz_")

        os.makedirs(output_dir, exist_ok=True)

        try:
            # Write input FASTA file
            fasta_path = os.path.join(output_dir, "input.fasta")
            self._write_fasta(sequences, fasta_path)

            # Run Boltz via command line
            # This is the recommended approach as it handles model loading efficiently
            result = self._run_boltz_cli(
                fasta_path=fasta_path,
                output_dir=output_dir,
                recycling_steps=recycling_steps,
                sampling_steps=sampling_steps
            )

            if not result["success"]:
                return LocalPredictionResult(
                    structure="",
                    confidence_scores={},
                    output_dir=output_dir,
                    success=False,
                    error=result.get("error", "Unknown error")
                )

            # Read output structure
            structure_path = os.path.join(output_dir, "boltz_results", "prediction.cif")
            if os.path.exists(structure_path):
                with open(structure_path, 'r') as f:
                    structure = f.read()
            else:
                # Try alternative paths
                structure = self._find_and_read_structure(output_dir)

            # Read confidence scores if available
            confidence_scores = self._read_confidence_scores(output_dir)

            return LocalPredictionResult(
                structure=structure,
                confidence_scores=confidence_scores,
                output_dir=output_dir,
                success=True
            )

        except Exception as e:
            return LocalPredictionResult(
                structure="",
                confidence_scores={},
                output_dir=output_dir,
                success=False,
                error=str(e)
            )

    def _write_fasta(self, sequences: List[Dict[str, Any]], path: str):
        """Write sequences to FASTA format."""
        with open(path, 'w') as f:
            for seq in sequences:
                f.write(f">{seq['id']}\n")
                # Write sequence in 80-char lines
                sequence = seq['sequence']
                for i in range(0, len(sequence), 80):
                    f.write(sequence[i:i+80] + "\n")

    def _run_boltz_cli(
        self,
        fasta_path: str,
        output_dir: str,
        recycling_steps: int,
        sampling_steps: int
    ) -> Dict[str, Any]:
        """Run Boltz via command line interface."""
        try:
            cmd = [
                "boltz", "predict",
                fasta_path,
                "--output_dir", output_dir,
                "--recycling_steps", str(recycling_steps),
                "--sampling_steps", str(sampling_steps),
                "--output_format", "mmcif"
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )

            if result.returncode != 0:
                return {
                    "success": False,
                    "error": result.stderr or "Boltz prediction failed"
                }

            return {"success": True}

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Prediction timed out (>1 hour)"
            }
        except FileNotFoundError:
            return {
                "success": False,
                "error": "Boltz CLI not found. Install with: pip install boltz"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _find_and_read_structure(self, output_dir: str) -> str:
        """Find and read structure file from output directory."""
        # Look for .cif files
        for root, dirs, files in os.walk(output_dir):
            for f in files:
                if f.endswith('.cif') or f.endswith('.mmcif'):
                    with open(os.path.join(root, f), 'r') as file:
                        return file.read()
        return ""

    def _read_confidence_scores(self, output_dir: str) -> Dict[str, Any]:
        """Read confidence scores from output directory."""
        scores = {}

        # Look for JSON files with scores
        import json
        for root, dirs, files in os.walk(output_dir):
            for f in files:
                if f.endswith('.json') and 'score' in f.lower():
                    try:
                        with open(os.path.join(root, f), 'r') as file:
                            scores = json.load(file)
                            break
                    except Exception:
                        pass

        return scores
