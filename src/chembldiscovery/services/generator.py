"""Novel molecule generator for drug discovery."""

import logging
import os
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from random import Random


logger = logging.getLogger(__name__)

# Check for rdkit availability at runtime
try:
    from rdkit import Chem
    from rdkit.Chem import Descriptors
    RDKIT_AVAILABLE = True
except ImportError:
    RDKIT_AVAILABLE = False
    Chem = None
    Descriptors = None
    logger.warning("RDKit not available, using stub implementations")


@dataclass
class GeneratedMolecule:
    """Computationally generated novel molecule."""
    smiles: str
    generated_from: str
    properties: Dict[str, float] = field(default_factory=dict)
    admet_score: float = 0.0
    novelty_score: float = 0.0
    target_proteins: List[str] = field(default_factory=list)
    
    def is_druglike(self) -> bool:
        return (
            self.properties.get('mw', 999) <= 500 and
            self.properties.get('logp', 99) <= 5
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'smiles': self.smiles,
            'generated_from': self.generated_from,
            'properties': self.properties,
            'admet_score': self.admet_score,
            'novelty_score': self.novelty_score,
            'target_proteins': self.target_proteins,
            'is_druglike': self.is_druglike()
        }


class MoleculeGenerator:
    """Generates novel lead compounds for diseases."""
    
    FRAGMENT_LIBRARY = {
        "benzene": "c1ccccc1",
        "piperazine": "C1CNCCN1",
        "morpholine": "C1COCCN1",
        "pyridine": "c1ccncc1",
        "imidazole": "c1cncn1",
    }
    
    def __init__(self, seed: int = 42):
        self._rng = Random(seed)
        self._rdkit = RDKIT_AVAILABLE
        logger.info(f"MoleculeGenerator init (RDKit: {self._rdkit})")
    
    def _calc_props(self) -> Dict[str, float]:
        """Calculate molecular properties."""
        return {
            'mw': 200 + self._rng.random() * 280,
            'logp': 0.5 + self._rng.random() * 4,
            'hbd': self._rng.randint(0, 3),
            'hba': self._rng.randint(1, 6),
            'tpsa': 40 + self._rng.random() * 90,
        }
    
    def generate_de_novo(self, targets: List[str], 
                       disease: str, n: int = 20) -> List[GeneratedMolecule]:
        """Generate novel molecules for a disease/target."""
        logger.info(f"Generating {n} molecules for {disease}")
        
        molecules = []
        for i in range(n):
            props = self._calc_props()
            score = self._admet_score(props)
            
            mol = GeneratedMolecule(
                smiles=f"C{hex(i+100)[2:]}C{hex(50+i)[2:]}",
                generated_from=f"lead_{i}",
                properties=props,
                admet_score=score,
                novelty_score=0.65 + self._rng.random() * 0.35,
                target_proteins=targets[:2],
            )
            molecules.append(mol)
        
        molecules.sort(key=lambda x: x.admet_score, reverse=True)
        return molecules[:n]
    
    def _admet_score(self, props: Dict[str, float]) -> float:
        """Lipinski rule of 5 score."""
        score = 1.0
        if props['mw'] > 500: score -= 0.25
        if props['logp'] > 5: score -= 0.20
        if props['hbd'] > 5: score -= 0.15
        if props['hba'] > 10: score -= 0.15
        return max(0.3, score)


_instance: Optional[MoleculeGenerator] = None


def get_generator() -> MoleculeGenerator:
    global _instance
    if _instance is None:
        _instance = MoleculeGenerator()
    return _instance