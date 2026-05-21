"""Unit tests for ChEMBL Discovery models."""

import pytest
from chembldiscovery.models import Drug, Target, BioActivity, SearchResult, DrugPhase


class TestDrug:
    """Tests for Drug model."""
    
    def test_drug_creation(self):
        """Test basic drug creation."""
        drug = Drug(
            chembl_id="CHEM123",
            drug_name="Aspirin",
            indication="Pain",
            max_phase=5,
            smiles="CC(=O)OC1=CC=CC=C1C(=O)O"
        )
        
        assert drug.chembl_id == "CHEM123"
        assert drug.drug_name == "Aspirin"
        assert drug.max_phase == 5
        assert drug.is_approved is True
    
    def test_drug_default_max_phase(self):
        """Test default max phase."""
        drug = Drug(chembl_id="CHEM999")
        
        assert drug.max_phase == -1
        assert drug.phase_status == DrugPhase.UNKNOWN
    
    def test_drug_to_dict(self):
        """Test serialization."""
        drug = Drug(
            chembl_id="CHEM123",
            drug_name="TestDrug",
            max_phase=3
        )
        
        data = drug.to_dict()
        
        assert data['chembl_id'] == "CHEM123"
        assert data['drug_name'] == "TestDrug"
        assert data['max_phase'] == 3
        assert data['is_approved'] is False


class TestTarget:
    """Tests for Target model."""
    
    def test_target_creation(self):
        """Test target creation."""
        target = Target(
            target_chembl_id="TARG123",
            target_name="ACE2",
            organism="Human",
            target_type="Protein"
        )
        
        assert target.target_chembl_id == "TARG123"
        assert target.target_name == "ACE2"
        assert target.organism == "Human"
    
    def test_target_to_dict(self):
        """Test target serialization."""
        target = Target(
            target_chembl_id="TARG123",
            target_name="Test Target"
        )
        
        data = target.to_dict()
        
        assert 'target_chembl_id' in data
        assert data['target_name'] == "Test Target"


class TestBioActivity:
    """Tests for BioActivity model."""
    
    def test_activity_creation(self):
        """Test activity creation."""
        activity = BioActivity(
            molecule_chembl_id="CHEM123",
            target_chembl_id="TARG456",
            standard_value=10.5,
            standard_units="nM",
            standard_type="IC50"
        )
        
        assert activity.molecule_chembl_id == "CHEM123"
        assert activity.standard_value == 10.5
        assert activity.standard_units == "nM"
    
    def test_activity_serialization(self):
        """Test activity serialization."""
        activity = BioActivity(
            molecule_chembl_id="CHEM123",
            target_chembl_id="TARG456"
        )
        
        data = activity.to_dict()
        
        assert data['molecule_chembl_id'] == "CHEM123"
        assert data['target_chembl_id'] == "TARG456"


class TestSearchResult:
    """Tests for SearchResult model."""
    
    def test_search_result_creation(self):
        """Test search result creation."""
        drugs = [
            Drug(chembl_id="CHEM1", drug_name="Drug1", max_phase=3),
            Drug(chembl_id="CHEM2", drug_name="Drug2", max_phase=4),
        ]
        
        result = SearchResult(
            drugs=drugs,
            total_count=2,
            query="cancer"
        )
        
        assert len(result.drugs) == 2
        assert result.total_count == 2
        assert result.query == "cancer"
    
    def test_has_more(self):
        """Test pagination."""
        drugs = [Drug(chembl_id=f"CHEM{i}") for i in range(10)]
        
        result = SearchResult(
            drugs=drugs,
            total_count=100,
            query="test",
            page=1,
            page_size=10
        )
        
        assert result.has_more is True
        
        result_full_page = SearchResult(
            drugs=drugs,
            total_count=10,
            query="test",
            page=1,
            page_size=10
        )
        
        assert result_full_page.has_more is False