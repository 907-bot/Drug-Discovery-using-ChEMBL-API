"""ChEMBL Discovery - A comprehensive drug discovery platform."""

__version__ = "1.0.0"
__author__ = "Drug Discovery Team"

from chembldiscovery.services.drug_service import DrugService
from chembldiscovery.services.target_service import TargetService
from chembldiscovery.core.client import ChEMBLClient

__all__ = ["DrugService", "TargetService", "ChEMBLClient", "__version__"]