"""
NVIDIA NIM Boltz-2 API Client

Handles authentication and API calls to NVIDIA's hosted Boltz-2 service.
API documentation: https://build.nvidia.com/mit/boltz2
"""

import os
import json
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

import httpx


# NVIDIA NIM API endpoints
NIM_API_BASE = "https://health.api.nvidia.com/v1/biology/mit/boltz2"
NIM_PREDICT_ENDPOINT = f"{NIM_API_BASE}/predict"
NIM_HEALTH_ENDPOINT = "https://health.api.nvidia.com/v1/health/ready"


@dataclass
class Polymer:
    """A polymer (protein, DNA, or RNA) for structure prediction."""
    id: str
    molecule_type: str  # "protein", "dna", or "rna"
    sequence: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "molecule_type": self.molecule_type,
            "sequence": self.sequence
        }


@dataclass
class Ligand:
    """A small molecule ligand for binding prediction."""
    smiles: str
    predict_affinity: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "smiles": self.smiles,
            "predict_affinity": self.predict_affinity
        }


@dataclass
class PredictionResult:
    """Result from a Boltz-2 structure prediction."""
    structure: str  # mmCIF format
    confidence_scores: Dict[str, Any]
    binding_affinity: Optional[float] = None
    runtime_metrics: Optional[Dict[str, Any]] = None


class NvidiaAPIError(Exception):
    """Exception raised for NVIDIA NIM API errors."""
    def __init__(self, message: str, status_code: Optional[int] = None, response: Optional[str] = None):
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(self.message)


class NvidiaNimClient:
    """Client for NVIDIA NIM Boltz-2 API."""

    def __init__(self, api_key: Optional[str] = None, timeout: float = 300.0):
        """
        Initialize the NVIDIA NIM client.

        Args:
            api_key: NVIDIA API key. If not provided, reads from NVIDIA_API_KEY env var.
            timeout: Request timeout in seconds (default 5 minutes for long predictions)
        """
        self.api_key = api_key or os.environ.get("NVIDIA_API_KEY")
        self.timeout = timeout
        self._client: Optional[httpx.Client] = None

    @property
    def client(self) -> httpx.Client:
        """Lazy initialization of HTTP client."""
        if self._client is None:
            self._client = httpx.Client(
                timeout=httpx.Timeout(self.timeout),
                headers=self._get_headers()
            )
        return self._client

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers including authorization."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def is_available(self) -> Dict[str, Any]:
        """
        Check if the NVIDIA NIM API is available.

        Returns:
            Dictionary with availability status and details
        """
        result = {
            "available": False,
            "api_key_configured": bool(self.api_key),
            "error": None
        }

        if not self.api_key:
            result["error"] = "NVIDIA_API_KEY not configured"
            return result

        try:
            response = self.client.get(NIM_HEALTH_ENDPOINT)
            result["available"] = response.status_code == 200
            if not result["available"]:
                result["error"] = f"API returned status {response.status_code}"
        except httpx.RequestError as e:
            result["error"] = f"Connection error: {str(e)}"

        return result

    def predict_structure(
        self,
        polymers: List[Polymer],
        ligands: Optional[List[Ligand]] = None,
        recycling_steps: int = 3,
        sampling_steps: int = 200,
        diffusion_samples: int = 1,
    ) -> PredictionResult:
        """
        Predict the 3D structure of a biomolecular complex.

        Args:
            polymers: List of polymers (proteins, DNA, RNA) to predict
            ligands: Optional list of small molecule ligands
            recycling_steps: Number of recycling steps (default 3)
            sampling_steps: Number of diffusion sampling steps (default 200)
            diffusion_samples: Number of structure samples to generate (default 1)

        Returns:
            PredictionResult with structure in mmCIF format and confidence scores

        Raises:
            NvidiaAPIError: If the API call fails
        """
        if not self.api_key:
            raise NvidiaAPIError("NVIDIA_API_KEY not configured")

        if not polymers:
            raise NvidiaAPIError("At least one polymer is required")

        if len(polymers) > 12:
            raise NvidiaAPIError("Maximum 12 polymers allowed")

        # Build request payload
        payload = {
            "polymers": [p.to_dict() for p in polymers],
            "recycling_steps": recycling_steps,
            "sampling_steps": sampling_steps,
            "diffusion_samples": diffusion_samples,
            "output_format": "mmcif"
        }

        if ligands:
            payload["ligands"] = [lig.to_dict() for lig in ligands]

        try:
            response = self.client.post(NIM_PREDICT_ENDPOINT, json=payload)

            if response.status_code != 200:
                raise NvidiaAPIError(
                    f"API request failed",
                    status_code=response.status_code,
                    response=response.text
                )

            data = response.json()

            # Extract binding affinity if present
            binding_affinity = None
            if ligands and "binding_affinity" in data:
                binding_affinity = data["binding_affinity"]

            return PredictionResult(
                structure=data.get("structure", ""),
                confidence_scores=data.get("scores", {}),
                binding_affinity=binding_affinity,
                runtime_metrics=data.get("runtime_metrics")
            )

        except httpx.RequestError as e:
            raise NvidiaAPIError(f"Request failed: {str(e)}")

    def predict_binding_affinity(
        self,
        protein_sequence: str,
        ligand_smiles: str,
        protein_id: str = "A"
    ) -> Dict[str, Any]:
        """
        Predict binding affinity between a protein and ligand.

        This is a convenience method that calls predict_structure with
        affinity prediction enabled.

        Args:
            protein_sequence: Amino acid sequence of the protein
            ligand_smiles: SMILES string of the ligand
            protein_id: Chain ID for the protein (default "A")

        Returns:
            Dictionary with binding affinity and structure
        """
        polymer = Polymer(id=protein_id, molecule_type="protein", sequence=protein_sequence)
        ligand = Ligand(smiles=ligand_smiles, predict_affinity=True)

        result = self.predict_structure([polymer], [ligand])

        return {
            "binding_affinity": result.binding_affinity,
            "structure": result.structure,
            "confidence_scores": result.confidence_scores
        }

    def close(self):
        """Close the HTTP client."""
        if self._client is not None:
            self._client.close()
            self._client = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
