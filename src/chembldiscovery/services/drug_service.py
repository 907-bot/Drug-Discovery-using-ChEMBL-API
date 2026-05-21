"""Drug service for querying drug compounds."""

import logging
from typing import Optional, List, Dict, Any

from chembldiscovery.core.client import ChEMBLClient, get_client
from chembldiscovery.models import Drug, SearchResult, DrugPhase


logger = logging.getLogger(__name__)


class DrugService:
    """Service for drug-related queries."""
    
    def __init__(self, client: Optional[ChEMBLClient] = None):
        """Initialize service with optional client.
        
        Args:
            client: Optional ChEMBL client instance
        """
        self._client = client or get_client()
    
    def search_by_disease(self, disease_name: str, 
                         max_results: int = 100) -> SearchResult:
        """Search for drugs indicated for a disease.
        
        Args:
            disease_name: Name of the disease
            max_results: Maximum results to return
            
        Returns:
            SearchResult with list of Drugs
        """
        if not disease_name or not isinstance(disease_name, str):
            raise ValueError("Invalid disease name")
        
        disease_name = disease_name.strip()
        if not disease_name:
            raise ValueError("Disease name cannot be empty")
        
        logger.info(f"Searching for drugs for disease: {disease_name}")
        
        drugs = []
        seen_ids = set()
        
        # Get indications for the disease
        for ind in self._client.get_drug_indications(disease_name, max_results):
            chembl_id = ind.get('molecule_chembl_id')
            
            # Skip duplicates
            if chembl_id in seen_ids:
                continue
            seen_ids.add(chembl_id)
            
            # Get molecule details
            mol_data = self._client.get_molecule(chembl_id)
            if not mol_data:
                continue
            
            # Get molecule structure
            molecule_structures = mol_data.get('molecule_structures') or {}
            
            # Create Drug object
            drug = Drug(
                chembl_id=chembl_id,
                drug_name=mol_data.get('pref_name'),
                indication=ind.get('efo_term'),
                max_phase=mol_data.get('max_phase'),
                smiles=molecule_structures.get('canonical_smiles'),
                molecule_type=mol_data.get('molecule_type'),
                synonyms=mol_data.get('synonyms', [])
            )
            drugs.append(drug)
            
            if len(drugs) >= max_results:
                break
        
        logger.info(f"Found {len(drugs)} drugs for {disease_name}")
        
        return SearchResult(
            drugs=drugs,
            total_count=len(drugs),
            query=disease_name
        )
    
    def get_drug_details(self, chembl_id: str) -> Optional[Drug]:
        """Get detailed information for a specific drug.
        
        Args:
            chembl_id: ChEMBL ID of the drug
            
        Returns:
            Drug object or None
        """
        if not chembl_id:
            raise ValueError("ChEMBL ID is required")
        
        mol_data = self._client.get_molecule(chembl_id)
        if not mol_data:
            return None
        
        molecule_structures = mol_data.get('molecule_structures') or {}
        
        # Get mechanisms
        mechanisms = self._client.get_mechanisms(chembl_id)
        mechanism = None
        if mechanisms:
            mechanism = mechanisms[0].get('mechanism')
        
        return Drug(
            chembl_id=chembl_id,
            drug_name=mol_data.get('pref_name'),
            indication=None,  # Would need separate query
            max_phase=mol_data.get('max_phase'),
            smiles=molecule_structures.get('canonical_smiles'),
            molecule_type=mol_data.get('molecule_type'),
            synonyms=mol_data.get('synonyms', []),
            mechanism=mechanism
        )
    
    def search_by_target(self, target_name: str, organism: str = 'Human',
                     max_results: int = 50) -> List[Drug]:
        """Search for drugs targeting a specific protein.
        
        Args:
            target_name: Name of target protein
            organism: Organism name
            max_results: Maximum results
            
        Returns:
            List of Drug objects
        """
        if not target_name:
            raise ValueError("Target name is required")
        
        logger.info(f"Searching for drugs targeting: {target_name}")
        
        drugs = []
        seen_ids = set()
        
        for act in self._client.get_activities(target_name, organism, max_results):
            chembl_id = act.get('molecule_chembl_id')
            
            if chembl_id in seen_ids:
                continue
            seen_ids.add(chembl_id)
            
            mol_data = self._client.get_molecule(chembl_id)
            if not mol_data:
                continue
            
            molecule_structures = mol_data.get('molecule_structures') or {}
            
            drug = Drug(
                chembl_id=chembl_id,
                drug_name=mol_data.get('pref_name'),
                max_phase=mol_data.get('max_phase'),
                smiles=molecule_structures.get('canonical_smiles'),
                molecule_type=mol_data.get('molecule_type'),
                synonyms=mol_data.get('synonyms', [])
            )
            drugs.append(drug)
        
        return drugs
    
    def get_approved_drugs_for_indication(self, disease_name: str) -> List[Drug]:
        """Get only approved drugs for a disease.
        
        Args:
            disease_name: Name of disease
            
        Returns:
            List of approved Drug objects
        """
        result = self.search_by_disease(disease_name)
        return [d for d in result.drugs if d.max_phase == 5]
    
    def compare_drugs(self, chembl_ids: List[str]) -> Dict[str, Any]:
        """Compare multiple drugs side by side.
        
        Args:
            chembl_ids: List of ChEMBL IDs
            
        Returns:
            Dictionary with comparison data
        """
        drugs = []
        for cid in chembl_ids:
            drug = self.get_drug_details(cid)
            if drug:
                drugs.append(drug.to_dict())
        
        return {
            'comparison': drugs,
            'count': len(drugs)
        }