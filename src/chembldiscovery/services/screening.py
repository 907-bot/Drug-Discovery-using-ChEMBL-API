"""Virtual screening service for untreatable diseases."""

import logging
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime

from chembldiscovery.services.generator import MoleculeGenerator, get_generator
from chembldiscovery.services.drug_service import DrugService


logger = logging.getLogger(__name__)


# Orphan diseases - high unmet need
UNTREATABLE_DISEASES = {
    "huntington": {
        "name": "Huntington Disease",
        "description": "Neurodegenerative genetic disorder",
        "target_proteins": ["HTT", "Caspase-3", "mTOR"],
        "current_treatments": "Tetrabenazine, deutetrabenazine",
        "clinical_trials": 47,
        "unmet_need": "High"
    },
    "als": {
        "name": "Amyotrophic Lateral Sclerosis", 
        "description": "Motor neuron disease",
        "target_proteins": ["SOD1", "TDP-43", "FUS", "C9orf72"],
        "current_treatments": "Riluzole, edaravone",
        "clinical_trials": 156,
        "unmet_need": "Critical"
    },
    "duchenne": {
        "name": "Duchenne Muscular Dystrophy",
        "description": "Genetic muscle disorder",
        "target_proteins": ["DMD", "Utrophin", "Myostatin"],
        "current_treatments": "Prednisone, deflazacort, eteplirsen",
        "clinical_trials": 89,
        "unmet_need": "High"
    },
    "cf": {
        "name": "Cystic Fibrosis",
        "description": "Genetic lung disease",
        "target_proteins": ["CFTR", "ENaC", "Sodium channel"],
        "current_treatments": "Ivacaftor, lumacaftor, elexacaftor",
        "clinical_trials": 234,
        "unmet_need": "Medium"
    },
    "sickle_cell": {
        "name": "Sickle Cell Disease",
        "description": "Blood disorder",
        "target_proteins": ["Hemoglobin", "BCL11A", "Fetal hemoglobin"],
        "current_treatments": "Hydroxyurea, voxelotor, L-Glutamine",
        "clinical_trials": 67,
        "unmet_need": "High"
    },
    "parkinson": {
        "name": "Parkinson Disease",
        "description": "Neurodegenerative movement disorder",
        "target_proteins": ["Alpha-synuclein", "LRRK2", "DJ-1", "PINK1"],
        "current_treatments": "Levodopa, carbidopa, ropininirole",
        "clinical_trials": 412,
        "unmet_need": "High"
    },
    "alzheimers": {
        "name": "Alzheimer Disease",
        "description": "Neurodegenerative dementia",
        "target_proteins": ["Amyloid-beta", "Tau", "BACE1", "APP"],
        "current_treatments": "Donepezil, memantine, lecanemab",
        "clinical_trials": 589,
        "unmet_need": "Critical"
    },
    "multiple_sclerosis": {
        "name": "Multiple Sclerosis",
        "description": "Autoimmune demyelinating disease",
        "target_proteins": ["Myelin", "CD20", "IL-17", "IFN-beta"],
        "current_treatments": "Interferon, glatiramer, ocrelizumab",
        "clinical_trials": 345,
        "unmet_need": "High"
    }
}


@dataclass
class LeadCompound:
    """A lead compound for drug development."""
    id: str
    smiles: str
    disease: str
    target_proteins: List[str]
    affinity: float
    admet_score: float
    novelty_score: float
    synthesis_score: float
    patentability: float
    priority: str = "medium"
    notes: str = ""
    
    @property
    def total_score(self) -> float:
        """Combined lead score."""
        return (
            self.affinity * 0.35 +
            self.admet_score * 0.25 +
            self.novelty_score * 0.15 +
            self.synthesis_score * 0.15 +
            self.patentability * 0.10
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'smiles': self.smiles,
            'disease': self.disease,
            'target_proteins': self.target_proteins,
            'priority': self.priority,
            'scores': {
                'affinity': self.affinity,
                'admet': self.admet_score,
                'novelty': self.novelty_score,
                'synthesis': self.synthesis_score,
                'patentability': self.patentability,
                'total': self.total_score
            },
            'notes': self.notes
        }


@dataclass
class ScreeningResult:
    """Results from virtual screening campaign."""
    campaign_id: str
    disease: str
    initiated: datetime
    leads: List[LeadCompound]
    molecules_generated: int
    computational_time_seconds: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'campaign_id': self.campaign_id,
            'disease': self.disease,
            'initiated': self.initiated.isoformat(),
            'leads': [l.to_dict() for l in self.leads],
            'total_leads': len(self.leads),
            'molecules_generated': self.molecules_generated,
            'computational_time_seconds': self.computational_time_seconds,
            'top_score': self.leads[0].total_score if self.leads else 0.0
        }


class VirtualScreeningService:
    """Virtual screening for untreatable diseases."""
    
    def __init__(self):
        """Initialize screening service."""
        self._generator = get_generator()
        self._drug_service = DrugService()
        logger.info("Initialized Virtual Screening Service")
    
    def list_untreatable_diseases(self) -> Dict[str, Dict]:
        """List available untreatable diseases."""
        return UNTREATABLE_DISEASES
    
    def screen_disease(self, disease_key: str, n_leads: int = 20) -> ScreeningResult:
        """Run virtual screening for a disease.
        
        Args:
            disease_key: Key from UNTREATABLE_DISEASES
            n_leads: Number of leads to generate
            
        Returns:
            ScreeningResult with lead compounds
        """
        import time
        start = time.time()
        
        if disease_key not in UNTREATABLE_DISEASES:
            raise ValueError(f"Unknown disease: {disease_key}")
        
        disease_info = UNTREATABLE_DISEASES[disease_key]
        target_proteins = disease_info["target_proteins"]
        
        logger.info(f"Screen {disease_key}: targets={target_proteins}")
        
        # Generate novel molecules
        molecules = self._generator.generate_de_novo(
            target_proteins, 
            disease_info["name"],
            n_leads * 2
        )
        
        # Convert to leads
        leads = []
        for i, mol in enumerate(molecules[:n_leads]):
            lead = LeadCompound(
                id=f"LEAD-{disease_key.upper()}-{i+1:03d}",
                smiles=mol.smiles,
                disease=disease_info["name"],
                target_proteins=target_proteins,
                affinity=0.7 + (mol.novelty_score * 0.3),
                admet_score=mol.admet_score,
                novelty_score=mol.novelty_score,
                synthesis_score=0.6 + (mol.is_druglike() * 0.4),
                patentability=mol.novelty_score,
                priority="high" if mol.admet_score > 0.7 else "medium"
            )
            leads.append(lead)
        
        # Sort by total score
        leads.sort(key=lambda x: x.total_score, reverse=True)
        
        elapsed = time.time() - start
        
        result = ScreeningResult(
            campaign_id=f"SCREEN-{disease_key}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            disease=disease_info["name"],
            initiated=datetime.now(),
            leads=leads,
            molecules_generated=len(molecules),
            computational_time_seconds=elapsed
        )
        
        logger.info(f"Screening complete: {len(leads)} leads, {elapsed:.1f}s")
        return result
    
    def get_top_leads(self, disease_key: str, n: int = 5) -> List[Dict]:
        """Get top N leads for a disease."""
        result = self.screen_disease(disease_key)
        return [l.to_dict() for l in result.leads[:n]]


_screen_service: Optional[VirtualScreeningService] = None


def get_screening_service() -> VirtualScreeningService:
    """Get screening service singleton."""
    global _screen_service
    if _screen_service is None:
        _screen_service = VirtualScreeningService()
    return _screen_service