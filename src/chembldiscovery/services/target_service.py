"""Target service for protein target queries."""

import logging
from typing import Optional, List, Dict, Any

from chembldiscovery.core.client import ChEMBLClient, get_client
from chembldiscovery.models import Target, BioActivity


logger = logging.getLogger(__name__)


class TargetService:
    """Service for target-related queries."""
    
    def __init__(self, client: Optional[ChEMBLClient] = None):
        """Initialize service.
        
        Args:
            client: Optional ChEMBL client
        """
        self._client = client or get_client()
    
    def search_targets(self, target_name: str, 
                       max_results: int = 20) -> List[Target]:
        """Search for protein targets by name.
        
        Args:
            target_name: Name to search for
            max_results: Maximum results
            
        Returns:
            List of Target objects
        """
        if not target_name:
            raise ValueError("Target name is required")
        
        logger.info(f"Searching for targets: {target_name}")
        
        targets = []
        for tgt_data in self._client.find_targets(target_name, max_results):
            target = Target(
                target_chembl_id=tgt_data.get('target_chembl_id'),
                target_name=tgt_data.get('target_name'),
                organism=tgt_data.get('organism'),
                target_type=tgt_data.get('target_type'),
                protein_classification=tgt_data.get('protein_classification')
            )
            targets.append(target)
        
        return targets
    
    def get_target_details(self, target_chembl_id: str) -> Optional[Target]:
        """Get detailed target information.
        
        Args:
            target_chembl_id: Target ChEMBL ID
            
        Returns:
            Target object or None
        """
        try:
            targets = self._client.target.filter(
                target_chembl_id=target_chembl_id
            )
            tgt_data = next(iter(targets), None)
            
            if not tgt_data:
                return None
            
            return Target(
                target_chembl_id=tgt_data.get('target_chembl_id'),
                target_name=tgt_data.get('target_name'),
                organism=tgt_data.get('organism'),
                target_type=tgt_data.get('target_type'),
                protein_classification=tgt_data.get('protein_classification')
            )
        except Exception as e:
            logger.error(f"Failed to get target details: {e}")
            return None
    
    def get_bioactivities(self, target_name: str, organism: str = 'Human',
                        max_results: int = 100) -> List[BioActivity]:
        """Get all bioactivities for a target.
        
        Args:
            target_name: Target name
            organism: Organism name
            max_results: Maximum results
            
        Returns:
            List of BioActivity objects
        """
        if not target_name:
            raise ValueError("Target name required")
        
        activities = []
        
        for act in self._client.get_activities(target_name, organism, max_results=max_results):
            activity = BioActivity(
                molecule_chembl_id=act.get('molecule_chembl_id'),
                target_chembl_id=act.get('target_chembl_id'),
                standard_value=act.get('standard_value'),
                standard_units=act.get('standard_units'),
                standard_type=act.get('standard_type'),
                assay_description=act.get('assay_description')
            )
            activities.append(activity)
        
        return activities
    
    def find_druggable_targets(self, target_name_pattern: str) -> List[Target]:
        """Find druggable targets matching a pattern.
        
        Args:
            target_name_pattern: Pattern to search
            
        Returns:
            List of Target objects
        """
        targets = self.search_targets(target_name_pattern, max_results=50)
        # Filter for proteins that are typically druggable
        return [t for t in targets if t.target_type == 'Protein']