"""
REST Server - FastAPI implementation for ICTV-git API

Provides RESTful endpoints for all taxonomy, historical, AI, and search features
with proper error handling, documentation, and performance optimization.
"""

from fastapi import FastAPI, HTTPException, Query, Body, Path as FastAPIPath
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
import asyncio
import traceback
from pathlib import Path
import os

# Import our API classes
from .taxonomy_api import TaxonomyAPI
from .historical_api import HistoricalAPI
from .ai_api import AIAPI
from .search_api import SearchAPI


# Pydantic models for request/response validation
class SpeciesSearchRequest(BaseModel):
    query: str = Field(..., description="Search query for species")
    family_filter: Optional[str] = Field(None, description="Filter by family name")
    genus_filter: Optional[str] = Field(None, description="Filter by genus name")
    exact_match: bool = Field(False, description="Require exact match")
    limit: int = Field(100, description="Maximum results to return")


class ClassificationRequest(BaseModel):
    organism_name: Optional[str] = Field(None, description="Name of organism")
    genome_sequence: Optional[str] = Field(None, description="DNA/RNA sequence")
    metadata: Optional[Dict] = Field(None, description="Additional metadata")


class NLQueryRequest(BaseModel):
    query: str = Field(..., description="Natural language query")
    use_cache: bool = Field(True, description="Use cached results if available")


class AdvancedSearchRequest(BaseModel):
    query: Optional[str] = Field(None, description="Text search query")
    filters: Dict = Field(default_factory=dict, description="Search filters")
    sort_by: str = Field("relevance", description="Sort order")
    limit: int = Field(100, description="Maximum results")


class DatabaseSyncRequest(BaseModel):
    databases: Optional[List[str]] = Field(None, description="Databases to sync")
    species_list: Optional[List[str]] = Field(None, description="Specific species")


# Initialize FastAPI app
app = FastAPI(
    title="ICTV-Git API",
    description="RESTful API for 20-year viral taxonomy history and AI-powered features",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global API instances (initialized on startup)
taxonomy_api: Optional[TaxonomyAPI] = None
historical_api: Optional[HistoricalAPI] = None
ai_api: Optional[AIAPI] = None
search_api: Optional[SearchAPI] = None

# Configuration
TAXONOMY_REPO_PATH = os.environ.get('ICTV_REPO_PATH', '/Users/scotthandley/Code/ICTV-git/output/ictv_complete_20_year_taxonomy')


@app.on_event("startup")
async def startup_event():
    """Initialize API instances on startup"""
    global taxonomy_api, historical_api, ai_api, search_api
    
    try:
        # Verify repository path exists
        repo_path = Path(TAXONOMY_REPO_PATH)
        if not repo_path.exists():
            raise ValueError(f"Taxonomy repository not found: {TAXONOMY_REPO_PATH}")
        
        # Initialize API instances
        taxonomy_api = TaxonomyAPI(TAXONOMY_REPO_PATH)
        historical_api = HistoricalAPI(TAXONOMY_REPO_PATH)
        ai_api = AIAPI(TAXONOMY_REPO_PATH)
        search_api = SearchAPI(TAXONOMY_REPO_PATH)
        
        # Build search index for better performance
        search_api.build_search_index()
        
        print(f"✅ ICTV-Git API initialized successfully")
        print(f"📂 Repository: {TAXONOMY_REPO_PATH}")
        print(f"🔍 Search index built")
        
    except Exception as e:
        print(f"❌ Failed to initialize API: {e}")
        print(traceback.format_exc())
        raise


# Error handlers
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "type": type(exc).__name__
        }
    )


# Health and status endpoints
@app.get("/", summary="API Root", description="Basic API information")
async def root():
    return {
        "name": "ICTV-Git API",
        "version": "1.0.0",
        "description": "RESTful API for 20-year viral taxonomy history",
        "repository_path": TAXONOMY_REPO_PATH,
        "endpoints": {
            "taxonomy": "/taxonomy/*",
            "historical": "/historical/*", 
            "ai": "/ai/*",
            "search": "/search/*",
            "docs": "/docs"
        }
    }


@app.get("/health", summary="Health Check", description="API health status")
async def health_check():
    """Comprehensive health check"""
    if not all([taxonomy_api, historical_api, ai_api, search_api]):
        raise HTTPException(status_code=503, detail="API not fully initialized")
    
    health_data = {
        "status": "healthy",
        "repository_path": TAXONOMY_REPO_PATH,
        "api_components": {
            "taxonomy_api": taxonomy_api is not None,
            "historical_api": historical_api is not None,
            "ai_api": ai_api is not None,
            "search_api": search_api is not None
        }
    }
    
    # Get AI health check
    try:
        ai_health = ai_api.get_ai_health_check()
        health_data["ai_features"] = ai_health
    except Exception as e:
        health_data["ai_features"] = {"error": str(e)}
    
    return health_data


# Taxonomy endpoints
@app.get("/taxonomy/species/{scientific_name}", summary="Get Species", description="Get species by scientific name")
async def get_species(scientific_name: str, msl_version: Optional[str] = None):
    """Get species data by scientific name"""
    result = taxonomy_api.get_species(scientific_name, msl_version)
    if not result:
        raise HTTPException(status_code=404, detail=f"Species '{scientific_name}' not found")
    return result


@app.get("/taxonomy/family/{family_name}", summary="Get Family", description="Get complete family data")
async def get_family(family_name: str):
    """Get complete family data including genera and species"""
    result = taxonomy_api.get_family(family_name)
    if not result or 'error' in result:
        raise HTTPException(status_code=404, detail=f"Family '{family_name}' not found")
    return result


@app.get("/taxonomy/hierarchy", summary="Get Hierarchy", description="Get complete taxonomy hierarchy")
async def get_hierarchy():
    """Get complete taxonomy hierarchy structure"""
    return taxonomy_api.get_taxonomy_hierarchy()


@app.get("/taxonomy/families", summary="List Families", description="Get list of all family names")
async def list_families():
    """Get list of all family names"""
    return {"families": taxonomy_api.get_families_list()}


@app.get("/taxonomy/genera", summary="List Genera", description="Get list of genera")
async def list_genera(family: Optional[str] = Query(None, description="Filter by family")):
    """Get list of genera, optionally filtered by family"""
    return {"genera": taxonomy_api.get_genera_list(family)}


@app.post("/taxonomy/validate", summary="Validate Classification", description="Validate taxonomic classification")
async def validate_classification(classification_data: Dict = Body(...)):
    """Validate a taxonomic classification"""
    return taxonomy_api.validate_classification(classification_data)


# Historical endpoints
@app.get("/historical/releases", summary="List Releases", description="Get all MSL releases")
async def get_releases():
    """Get all MSL releases with metadata"""
    return {"releases": historical_api.get_msl_releases()}


@app.get("/historical/releases/{msl_version}", summary="Get Release Details", description="Get detailed release info")
async def get_release_details(msl_version: str = FastAPIPath(..., description="MSL version (e.g., MSL35)")):
    """Get detailed information about a specific MSL release"""
    result = historical_api.get_release_details(msl_version)
    if not result:
        raise HTTPException(status_code=404, detail=f"MSL version '{msl_version}' not found")
    return result


@app.get("/historical/compare/{from_version}/{to_version}", summary="Compare Releases", description="Compare two MSL releases")
async def compare_releases(
    from_version: str = FastAPIPath(..., description="Starting MSL version"),
    to_version: str = FastAPIPath(..., description="Ending MSL version")
):
    """Compare two MSL releases"""
    try:
        return historical_api.compare_releases(from_version, to_version)
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/historical/species/{scientific_name}/history", summary="Species History", description="Get species evolution history")
async def get_species_history(scientific_name: str = FastAPIPath(..., description="Scientific name of species")):
    """Get complete history of a species across all releases"""
    return {"species": scientific_name, "history": historical_api.get_species_history(scientific_name)}


@app.get("/historical/family/{family_name}/evolution", summary="Family Evolution", description="Track family evolution")
async def get_family_evolution(family_name: str = FastAPIPath(..., description="Name of viral family")):
    """Track evolution of a viral family across releases"""
    return historical_api.get_family_evolution(family_name)


@app.get("/historical/caudovirales-dissolution", summary="Caudovirales Dissolution", description="Historic reorganization details")
async def get_caudovirales_dissolution():
    """Get detailed information about the historic Caudovirales dissolution"""
    return historical_api.get_caudovirales_dissolution()


@app.get("/historical/timeline", summary="Timeline Summary", description="20-year timeline overview")
async def get_timeline_summary():
    """Get high-level summary of the 20-year timeline"""
    return historical_api.get_timeline_summary()


# AI endpoints
@app.get("/ai/features", summary="Available AI Features", description="List available AI capabilities")
async def get_ai_features():
    """Get list of available AI features"""
    return ai_api.get_available_features()


@app.post("/ai/query", summary="Natural Language Query", description="Ask questions in natural language")
async def natural_language_query(request: NLQueryRequest):
    """Process natural language query about taxonomy"""
    return ai_api.query_natural_language(request.query, request.use_cache)


@app.get("/ai/cache-stats", summary="Cache Statistics", description="Get NLQ cache statistics")
async def get_cache_stats():
    """Get Natural Language Query cache statistics"""
    return ai_api.get_cache_stats()


@app.post("/ai/classify", summary="AI Classification", description="Get AI classification suggestions")
async def classify_organism(request: ClassificationRequest):
    """Get AI classification suggestions for an organism"""
    return ai_api.classify_organism(
        genome_sequence=request.genome_sequence,
        metadata=request.metadata,
        organism_name=request.organism_name
    )


@app.get("/ai/stability/{family_name}", summary="Family Stability", description="Get family stability score")
async def get_family_stability(family_name: str = FastAPIPath(..., description="Name of viral family")):
    """Get stability score for a viral family"""
    return ai_api.get_family_stability_score(family_name)


@app.get("/ai/sync-status", summary="Database Sync Status", description="Get synchronization status")
async def get_sync_status():
    """Get current database synchronization status"""
    return ai_api.get_database_sync_status()


@app.post("/ai/sync", summary="Sync Databases", description="Synchronize with external databases")
async def sync_databases(request: DatabaseSyncRequest):
    """Synchronize with external databases"""
    return await ai_api.sync_databases(
        databases=request.databases,
        species_list=request.species_list
    )


@app.get("/ai/health", summary="AI Health Check", description="Comprehensive AI system health")
async def get_ai_health():
    """Comprehensive health check of all AI features"""
    return ai_api.get_ai_health_check()


@app.get("/ai/examples", summary="Example Queries", description="Get example usage for AI features")
async def get_ai_examples():
    """Get example queries for each AI feature"""
    return ai_api.get_example_queries()


# Search endpoints
@app.post("/search/species", summary="Search Species", description="Search species with filters")
async def search_species(request: SpeciesSearchRequest):
    """Search species with advanced filtering"""
    return search_api.search_species(
        query=request.query,
        family_filter=request.family_filter,
        genus_filter=request.genus_filter,
        exact_match=request.exact_match,
        limit=request.limit
    )


@app.get("/search/facets", summary="Search Facets", description="Get available search filters")
async def get_search_facets():
    """Get search facets for filtering options"""
    return search_api.get_facets()


@app.post("/search/faceted", summary="Faceted Search", description="Search using faceted filters")
async def faceted_search(facet_filters: Dict = Body(...), limit: int = Query(100)):
    """Search using faceted filters"""
    return search_api.search_by_facets(facet_filters, limit)


@app.get("/search/family/{family_name}/summary", summary="Family Summary", description="Comprehensive family summary")
async def get_family_summary(family_name: str = FastAPIPath(..., description="Name of viral family")):
    """Get comprehensive summary of a viral family"""
    result = search_api.get_family_summary(family_name)
    if 'error' in result:
        raise HTTPException(status_code=404, detail=result['error'])
    return result


@app.post("/search/advanced", summary="Advanced Search", description="Advanced search with multiple parameters")
async def advanced_search(request: AdvancedSearchRequest):
    """Advanced search with multiple parameters"""
    return search_api.advanced_search(request.dict())


@app.get("/search/statistics", summary="Search Statistics", description="Search index statistics")
async def get_search_statistics():
    """Get comprehensive search index statistics"""
    return search_api.get_search_statistics()


@app.get("/search/rebuild-index", summary="Rebuild Search Index", description="Force rebuild search index")
async def rebuild_search_index():
    """Force rebuild of search index"""
    return search_api.build_search_index(force_rebuild=True)


# Development and testing endpoints
@app.get("/dev/test-all", summary="Test All Features", description="Test all API functionality")
async def test_all_features():
    """Comprehensive test of all API features"""
    results = {
        "taxonomy": {},
        "historical": {},
        "ai": {},
        "search": {}
    }
    
    try:
        # Test taxonomy
        hierarchy = taxonomy_api.get_taxonomy_hierarchy()
        results["taxonomy"]["hierarchy"] = {"families_count": hierarchy.get("total_families", 0)}
        
        # Test historical
        timeline = historical_api.get_timeline_summary()
        results["historical"]["timeline"] = {"releases_count": timeline.get("total_releases", 0)}
        
        # Test AI
        ai_health = ai_api.get_ai_health_check()
        results["ai"]["health"] = ai_health.get("overall_status", "unknown")
        
        # Test search
        search_stats = search_api.get_search_statistics()
        results["search"]["statistics"] = {"species_indexed": search_stats.get("coverage", {}).get("species_indexed", 0)}
        
        results["overall_status"] = "success"
        
    except Exception as e:
        results["error"] = str(e)
        results["overall_status"] = "failed"
    
    return results


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)