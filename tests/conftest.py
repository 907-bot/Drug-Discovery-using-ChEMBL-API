"""Pytest configuration."""

import pytest
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


@pytest.fixture(scope="session")
def sample_disease():
    """Sample disease name for testing."""
    return "dengue"


@pytest.fixture(scope="session")
def sample_target():
    """Sample target name for testing."""
    return "ACE2"


@pytest.fixture(scope="session")
def sample_chembl_id():
    """Sample ChEMBL ID for testing."""
    return "CHEM126921"


@pytest.fixture
def mock_molecule_data():
    """Mock molecule data for testing."""
    return {
        "molecule_chembl_id": "CHEM123",
        "pref_name": "Test Drug",
        "max_phase": 4,
        "molecule_type": "Small molecule",
        "molecule_structures": {
            "canonical_smiles": "CCO"
        }
    }