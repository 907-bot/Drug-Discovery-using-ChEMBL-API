"""Models for drug discovery data structures."""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum


class DrugPhase(Enum):
    """Clinical trial phase statuses."""
    PHASE_0 = 0
    PHASE_1 = 1
    PHASE_2 = 2
    PHASE_3 = 3
    PHASE_4 = 4
    APPROVED = 5
    UNKNOWN = -1


@dataclass
class Drug:
    """Represents a drug compound from ChEMBL."""
    chembl_id: str
    drug_name: Optional[str] = None
    indication: Optional[str] = None
    max_phase: Optional[int] = None
    smiles: Optional[str] = None
    molecule_type: Optional[str] = None
    synonyms: List[str] = field(default_factory=list)
    mechanism: Optional[str] = None
    
    def __post_init__(self):
        if self.max_phase is None:
            self.max_phase = -1
    
    @property
    def phase_status(self) -> DrugPhase:
        """Get the phase status enum."""
        if self.max_phase == -1:
            return DrugPhase.UNKNOWN
        return DrugPhase(self.max_phase) if self.max_phase <= 5 else DrugPhase.APPROVED
    
    @property
    def is_approved(self) -> bool:
        """Check if the drug is approved."""
        return self.max_phase == 5
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'chembl_id': self.chembl_id,
            'drug_name': self.drug_name,
            'indication': self.indication,
            'max_phase': self.max_phase,
            'smiles': self.smiles,
            'molecule_type': self.molecule_type,
            'synonyms': self.synonyms,
            'mechanism': self.mechanism,
            'is_approved': self.is_approved
        }


@dataclass
class Target:
    """Represents a protein target."""
    target_chembl_id: str
    target_name: str
    organism: Optional[str] = None
    target_type: Optional[str] = None
    protein_classification: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'target_chembl_id': self.target_chembl_id,
            'target_name': self.target_name,
            'organism': self.organism,
            'target_type': self.target_type,
            'protein_classification': self.protein_classification
        }


@dataclass 
class BioActivity:
    """Represents a bioactivity measurement."""
    molecule_chembl_id: str
    target_chembl_id: str
    standard_value: Optional[float] = None
    standard_units: Optional[str] = None
    standard_type: Optional[str] = None
    assay_description: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'molecule_chembl_id': self.molecule_chembl_id,
            'target_chembl_id': self.target_chembl_id,
            'standard_value': self.standard_value,
            'standard_units': self.standard_units,
            'standard_type': self.standard_type,
            'assay_description': self.assay_description
        }


@dataclass
class SearchResult:
    """Container for search results with metadata."""
    drugs: List[Drug]
    total_count: int
    query: str
    page: int = 1
    page_size: int = 100
    
    @property
    def has_more(self) -> bool:
        """Check if there are more results."""
        return self.page * self.page_size < self.total_count
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'drugs': [d.to_dict() for d in self.drugs],
            'total_count': self.total_count,
            'query': self.query,
            'page': self.page,
            'page_size': self.page_size,
            'has_more': self.has_more
        }