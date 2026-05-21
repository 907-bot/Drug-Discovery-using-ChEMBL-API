"""FastAPI application for ChEMBL Discovery API."""

import logging
from typing import Optional, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from chembldiscovery import __version__
from chembldiscovery.services import DrugService, TargetService
from chembldiscovery.core import get_client


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting ChEMBL Discovery API...")
    # Initialize client on startup
    try:
        client = get_client()
        logger.info("ChEMBL client initialized")
    except Exception as e:
        logger.error(f"Failed to initialize client: {e}")
    yield
    logger.info("Shutting down ChEMBL Discovery API...")


# Create FastAPI app
app = FastAPI(
    title="ChEMBL Discovery API",
    description="""
    Pharmaceutical Research Platform API
    
    Access the ChEMBL bioactivity database for drug discovery research.
    Search drugs by disease, target, or compound identifiers.
    """,
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Service dependencies
def get_drug_service() -> DrugService:
    """Get drug service instance."""
    return DrugService()


def get_target_service() -> TargetService:
    """Get target service instance."""
    return TargetService()


# Request/Response Models
class DrugSearchRequest(BaseModel):
    """Request model for drug search."""
    disease_name: str = Field(..., description="Name of disease to search")
    max_results: int = Field(100, ge=1, le=500, description="Maximum results")


class TargetSearchRequest(BaseModel):
    """Request model for target search."""
    target_name: str = Field(..., description="Target protein name")
    organism: str = Field("Human", description="Organism name")
    max_results: int = Field(20, ge=1, le=100, description="Max results")


class DrugDetailsResponse(BaseModel):
    """Response model for drug details."""
    chembl_id: str
    drug_name: Optional[str] = None
    indication: Optional[str] = None
    max_phase: Optional[int] = None
    smiles: Optional[str] = None
    molecule_type: Optional[str] = None
    synonyms: List[str] = []
    is_approved: bool = False


class SearchResultResponse(BaseModel):
    """Response for search results."""
    drugs: List[DrugDetailsResponse]
    total_count: int
    query: str
    has_more: bool = False


class TargetResponse(BaseModel):
    """Response model for targets."""
    target_chembl_id: str
    target_name: str
    organism: Optional[str] = None
    target_type: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str


# Routes
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {
        "message": "ChEMBL Discovery API",
        "version": __version__,
        "docs": "/docs"
    }


@app.get("/health", tags=["Health"], response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(status="healthy", version=__version__)


@app.get("/api/v1/drugs/search", tags=["Drugs"], response_model=SearchResultResponse)
async def search_drugs_by_disease(
    disease: str = Query(..., description="Disease name"),
    max_results: int = Query(100, ge=1, le=500),
    service: DrugService = Depends(get_drug_service)
):
    """Search for drugs by disease indication.
    
    Returns drugs that are indicated for the given disease.
    """
    try:
        result = service.search_by_disease(disease, max_results)
        
        drugs = [
            DrugDetailsResponse(
                chembl_id=d.chembl_id,
                drug_name=d.drug_name,
                indication=d.indication,
                max_phase=d.max_phase,
                smiles=d.smiles,
                molecule_type=d.molecule_type,
                synonyms=d.synonyms,
                is_approved=d.is_approved
            )
            for d in result.drugs
        ]
        
        return SearchResultResponse(
            drugs=drugs,
            total_count=result.total_count,
            query=result.query,
            has_more=result.has_more
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail="Search failed")


@app.get("/api/v1/drugs/{chembl_id}", tags=["Drugs"], response_model=DrugDetailsResponse)
async def get_drug(
    chembl_id: str,
    service: DrugService = Depends(get_drug_service)
):
    """Get detailed drug information by ChEMBL ID."""
    try:
        drug = service.get_drug_details(chembl_id)
        
        if not drug:
            raise HTTPException(
                status_code=404, 
                detail=f"Drug not found: {chembl_id}"
            )
        
        return DrugDetailsResponse(
            chembl_id=drug.chembl_id,
            drug_name=drug.drug_name,
            indication=drug.indication,
            max_phase=drug.max_phase,
            smiles=drug.smiles,
            molecule_type=drug.molecule_type,
            synonyms=drug.synonyms,
            is_approved=drug.is_approved
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting drug: {e}")
        raise HTTPException(status_code=500, detail="Failed to get drug details")


@app.get("/api/v1/drugs/{chembl_id}/approved", tags=["Drugs"], response_model=bool)
async def check_drug_approved(
    chembl_id: str,
    service: DrugService = Depends(get_drug_service)
):
    """Check if a drug is FDA approved."""
    try:
        drug = service.get_drug_details(chembl_id)
        
        if not drug:
            raise HTTPException(
                status_code=404,
                detail=f"Drug not found: {chembl_id}"
            )
        
        return drug.is_approved
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking approval: {e}")
        raise HTTPException(status_code=500, detail="Check failed")


@app.get("/api/v1/targets/search", tags=["Targets"], response_model=List[TargetResponse])
async def search_targets(
    target: str = Query(..., description="Target name"),
    max_results: int = Query(20, ge=1, le=100),
    service: TargetService = Depends(get_target_service)
):
    """Search for protein targets by name."""
    try:
        targets = service.search_targets(target, max_results)
        
        return [
            TargetResponse(
                target_chembl_id=t.target_chembl_id,
                target_name=t.target_name,
                organism=t.organism,
                target_type=t.target_type
            )
            for t in targets
        ]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Target search error: {e}")
        raise HTTPException(status_code=500, detail="Target search failed")


@app.get("/api/v1/targets/{target_chembl_id}", tags=["Targets"], response_model=TargetResponse)
async def get_target(
    target_chembl_id: str,
    service: TargetService = Depends(get_target_service)
):
    """Get detailed target information."""
    try:
        target = service.get_target_details(target_chembl_id)
        
        if not target:
            raise HTTPException(
                status_code=404,
                detail=f"Target not found: {target_chembl_id}"
            )
        
        return TargetResponse(
            target_chembl_id=target.target_chembl_id,
            target_name=target.target_name,
            organism=target.organism,
            target_type=target.target_type
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting target: {e}")
        raise HTTPException(status_code=500, detail="Failed to get target")


@app.post("/api/v1/drugs/compare", tags=["Drugs"])
async def compare_drugs(
    chembl_ids: List[str] = Query(..., description="List of ChEMBL IDs"),
    service: DrugService = Depends(get_drug_service)
):
    """Compare multiple drugs side by side."""
    try:
        if not chembl_ids or len(chembl_ids) > 20:
            raise HTTPException(
                status_code=400,
                detail="Provide 1-20 ChEMBL IDs"
            )
        
        result = service.compare_drugs(chembl_ids)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Compare error: {e}")
        raise HTTPException(status_code=500, detail="Comparison failed")


@app.get("/api/v1/research/untreatable", tags=["Research"])
async def list_untreatable_diseases():
    """List untreatable diseases for research."""
    from chembldiscovery.services import UNTREATABLE_DISEASES
    return {"diseases": UNTREATABLE_DISEASES}


@app.get("/api/v1/research/generate", tags=["Research"])
async def generate_molecules(
    disease: str = Query(..., description="Disease key (e.g., als, huntington)"),
    leads: int = Query(20, ge=1, le=100, description="Number of leads"),
    service: "VirtualScreeningService" = Depends(lambda: None)
):
    """Generate novel lead compounds for untreatable diseases."""
    from chembldiscovery.services.screening import get_screening_service
    
    svc = get_screening_service()
    try:
        result = svc.screen_disease(disease, leads)
        return result.to_dict()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Generation error: {e}")
        raise HTTPException(status_code=500, detail="Generation failed")


@app.get("/api/v1/research/leads/{disease}", tags=["Research"])
async def get_top_leads(
    disease: str,
    n: int = Query(5, ge=1, le=20),
    service: "VirtualScreeningService" = Depends(lambda: None)
):
    """Get top lead compounds for a disease."""
    from chembldiscovery.services.screening import get_screening_service
    
    svc = get_screening_service()
    try:
        leads = svc.get_top_leads(disease, n)
        return {"leads": leads}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Leads error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get leads")