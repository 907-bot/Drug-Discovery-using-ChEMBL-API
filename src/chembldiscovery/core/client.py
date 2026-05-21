"""Core ChEMBL API client."""

import logging
from typing import Optional, Any, Dict, Iterator, List
from functools import lru_cache

from chembl_webresource_client.new_client import new_client
from chembl_webresource_client.settings import Settings
from chembl_webresource_client.utils import utils


logger = logging.getLogger(__name__)


class ChEMBLClient:
    """Client for interacting with ChEMBL database."""
    
    # Class-level cache for client instances
    _instance: Optional['ChEMBLClient'] = None
    
    def __new__(cls) -> 'ChEMBLClient':
        """Singleton pattern to reuse API connections."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self) -> None:
        """Initialize the ChEMBL client."""
        if self._initialized:
            return
        
        logger.info("Initializing ChEMBL client...")
        
        # Configure the client with custom settings
        try:
            Settings.Instance().set_timeout(60)
            Settings.Instance().set_max_threads(4)
        except Exception as e:
            logger.warning(f"Could not configure client settings: {e}")
        
        # Initialize API endpoints
        self._molecule = new_client.molecule
        self._drug_indication = new_client.drug_indication
        self._target = new_client.target
        self._activity = new_client.activity
        self._mechanism = new_client.mechanism
        self._link = new_client.link
        
        self._initialized = True
        logger.info("ChEMBL client initialized successfully")
    
    @property
    def molecule(self):
        """Molecule endpoint."""
        return self._molecule
    
    @property
    def drug_indication(self):
        """Drug indication endpoint."""
        return self._drug_indication
    
    @property
    def target(self):
        """Target endpoint."""
        return self._target
    
    @property
    def activity(self):
        """Activity endpoint."""
        return self._activity
    
    @property
    def mechanism(self):
        """Mechanism endpoint."""
        return self._mechanism
    
    def get_molecule(self, chembl_id: str) -> Optional[Dict[str, Any]]:
        """Get molecule details by ChEMBL ID.
        
        Args:
            chembl_id: The ChEMBL ID to lookup
            
        Returns:
            Molecule data dictionary or None
        """
        try:
            result = self._molecule.get(chembl_id)
            if result:
                return dict(result)
            return None
        except Exception as e:
            logger.error(f"Failed to get molecule {chembl_id}: {e}")
            return None
    
    def get_drug_indications(self, disease_name: str, 
                          max_results: int = 100) -> Iterator[Dict[str, Any]]:
        """Search for drug indications by disease name.
        
        Args:
            disease_name: Name of disease to search
            max_results: Maximum number of results
            
        Yields:
            Drug indication dictionaries
        """
        try:
            indications = self._drug_indication.filter(
                disease_efo__icontains=disease_name
            )
            
            count = 0
            for ind in indications:
                if count >= max_results:
                    break
                yield dict(ind)
                count += 1
        except Exception as e:
            logger.error(f"Failed to search indications for {disease_name}: {e}")
    
    def get_activities(self, target_name: str, organism: str = 'Human',
                     max_results: int = 50) -> Iterator[Dict[str, Any]]:
        """Search for activities by target.
        
        Args:
            target_name: Target protein name
            organism: Organism name
            max_results: Maximum results to return
            
        Yields:
            Activity dictionaries
        """
        try:
            activities = self._activity.filter(
                target_name__icontains=target_name,
                organism__icontains=organism
            )
            
            count = 0
            for act in activities:
                if count >= max_results:
                    break
                yield dict(act)
                count += 1
        except Exception as e:
            logger.error(f"Failed to get activities for {target_name}: {e}")
    
    def find_targets(self, target_name: str, 
                    max_results: int = 20) -> Iterator[Dict[str, Any]]:
        """Find targets by name.
        
        Args:
            target_name: Target name to search
            max_results: Maximum results
            
        Yields:
            Target dictionaries
        """
        try:
            targets = self._target.filter(
                target_name__icontains=target_name
            )
            
            count = 0
            for tgt in targets:
                if count >= max_results:
                    break
                yield dict(tgt)
                count += 1
        except Exception as e:
            logger.error(f"Failed to find targets {target_name}: {e}")
    
    def get_mechanisms(self, chembl_id: str) -> List[Dict[str, Any]]:
        """Get mechanism of action for a molecule.
        
        Args:
            chembl_id: Molecule ChEMBL ID
            
        Returns:
            List of mechanism dictionaries
        """
        try:
            mechanisms = self._mechanism.filter(
                molecule_chembl_id=chembl_id
            )
            return [dict(m) for m in mechanisms]
        except Exception as e:
            logger.error(f"Failed to get mechanisms for {chembl_id}: {e}")
            return []
    
    def search_similar_molecules(self, smiles: str,
                                max_results: int = 10) -> List[Dict[str, Any]]:
        """Find similar molecules based on SMILES.
        
        Args:
            smiles: SMILES string
            max_results: Maximum results
            
        Returns:
            List of similar molecule dictionaries
        """
        try:
            from rdkit import Chem
            from rdkit.Chem import AllChem
            
            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                logger.warning(f"Invalid SMILES: {smiles}")
                return []
            
            fp = AllChem.GetMorganFingerprintAsBitVect(mol, 2)
            # Use similarity search via link endpoint
            similar = self._link.mechanismsimilarity.filter(
                molecule_smiles__=smiles
            ).limit(max_results)
            
            return [dict(s) for s in similar]
        except Exception as e:
            logger.error(f"Failed to search similar molecules: {e}")
            return []


def get_client() -> ChEMBLClient:
    """Get a singleton ChEMBL client instance.
    
    Returns:
        Configured ChEMBLClient instance
    """
    return ChEMBLClient()