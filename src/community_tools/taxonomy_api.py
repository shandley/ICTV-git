"""
RESTful API for programmatic access to ICTV git-based taxonomy.

Provides endpoints for:
- Species lookup and search
- Taxonomic hierarchy navigation
- Version comparison
- Change history
- Bulk data access
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Optional, Set
from pathlib import Path
import yaml
import json
from datetime import datetime
import io
import csv

# Import our existing tools
from ..parsers.virus_species import VirusSpecies
from .version_comparator import VersionComparator
from .citation_generator import CitationGenerator

app = FastAPI(
    title="ICTV Git Taxonomy API",
    description="RESTful API for accessing ICTV viral taxonomy data",
    version="1.0.0"
)

# Global variables for data storage
REPO_PATH: Optional[Path] = None
TAXONOMY_DATA: Dict[str, Dict] = {}
VERSION_COMPARATOR: Optional[VersionComparator] = None
CITATION_GENERATOR: Optional[CitationGenerator] = None


class TaxonomyAPI:
    """API handler for taxonomy data."""
    
    def __init__(self, git_repo_path: str):
        global REPO_PATH, TAXONOMY_DATA, VERSION_COMPARATOR, CITATION_GENERATOR
        
        REPO_PATH = Path(git_repo_path)
        self.repo_path = REPO_PATH
        
        # Initialize tools
        VERSION_COMPARATOR = VersionComparator(git_repo_path)
        CITATION_GENERATOR = CitationGenerator(git_repo_path)
        
        # Load all taxonomy data
        self._load_all_data()
    
    def _load_all_data(self):
        """Load all taxonomy data into memory for fast access."""
        global TAXONOMY_DATA
        
        output_dir = self.repo_path / 'output'
        for version_dir in sorted(output_dir.glob('MSL*')):
            if version_dir.is_dir():
                version = version_dir.name
                TAXONOMY_DATA[version] = self._load_version_data(version_dir)
                print(f"Loaded {len(TAXONOMY_DATA[version]['species'])} species from {version}")
    
    def _load_version_data(self, version_dir: Path) -> Dict:
        """Load all species data for a version."""
        species_dict = {}
        species_list = []
        
        for yaml_file in version_dir.rglob('*.yaml'):
            try:
                with open(yaml_file, 'r') as f:
                    species = yaml.safe_load(f)
                    if species and 'scientific_name' in species:
                        name = species['scientific_name']
                        species['_id'] = name.lower().replace(' ', '_')
                        species['_file_path'] = str(yaml_file.relative_to(version_dir))
                        species_dict[name] = species
                        species_list.append(species)
            except Exception as e:
                print(f"Error loading {yaml_file}: {e}")
        
        # Build indexes
        indexes = self._build_indexes(species_list)
        
        return {
            'species': species_dict,
            'list': species_list,
            'indexes': indexes,
            'total': len(species_list)
        }
    
    def _build_indexes(self, species_list: List[Dict]) -> Dict:
        """Build various indexes for fast lookup."""
        indexes = {
            'by_genus': {},
            'by_family': {},
            'by_order': {},
            'by_realm': {},
            'by_host': {},
            'by_genome_type': {}
        }
        
        for species in species_list:
            classification = species.get('classification', {})
            
            # Taxonomic indexes
            for rank in ['genus', 'family', 'order', 'realm']:
                if rank in classification and classification[rank]:
                    value = classification[rank]
                    if value not in indexes[f'by_{rank}']:
                        indexes[f'by_{rank}'][value] = []
                    indexes[f'by_{rank}'][value].append(species['scientific_name'])
            
            # Host index
            for host in species.get('hosts', []):
                if host not in indexes['by_host']:
                    indexes['by_host'][host] = []
                indexes['by_host'][host].append(species['scientific_name'])
            
            # Genome type index
            genome_type = species.get('genome', {}).get('type')
            if genome_type:
                if genome_type not in indexes['by_genome_type']:
                    indexes['by_genome_type'][genome_type] = []
                indexes['by_genome_type'][genome_type].append(species['scientific_name'])
        
        return indexes


# Pydantic models for API responses
class SpeciesInfo(BaseModel):
    scientific_name: str
    classification: Dict[str, str]
    genome: Optional[Dict[str, str]] = None
    hosts: List[str] = []
    evidence: Optional[Dict] = None
    history: Optional[Dict] = None


class SearchResult(BaseModel):
    query: str
    version: str
    total_results: int
    results: List[SpeciesInfo]


class TaxonomicGroup(BaseModel):
    rank: str
    name: str
    version: str
    species_count: int
    species_names: List[str]


class VersionInfo(BaseModel):
    version: str
    total_species: int
    total_genera: int
    total_families: int
    total_orders: int
    total_realms: int
    year: Optional[int] = None


class ComparisonSummary(BaseModel):
    version1: str
    version2: str
    species_added: int
    species_removed: int
    species_reclassified: int
    species_renamed: int


# API Endpoints

@app.get("/")
async def root():
    """API root endpoint with basic info."""
    return {
        "title": "ICTV Git Taxonomy API",
        "version": "1.0.0",
        "description": "RESTful API for ICTV viral taxonomy data",
        "endpoints": {
            "versions": "/api/v1/versions",
            "species": "/api/v1/species/{version}/{species_name}",
            "search": "/api/v1/search",
            "taxonomy": "/api/v1/taxonomy/{version}/{rank}/{name}",
            "compare": "/api/v1/compare/{version1}/{version2}",
            "history": "/api/v1/history/{species_name}",
            "citation": "/api/v1/citation"
        }
    }


@app.get("/api/v1/versions", response_model=List[VersionInfo])
async def get_versions():
    """Get all available taxonomy versions with statistics."""
    versions = []
    
    for version, data in sorted(TAXONOMY_DATA.items()):
        # Calculate stats
        genera = set()
        families = set()
        orders = set()
        realms = set()
        
        for species in data['list']:
            classification = species.get('classification', {})
            if classification.get('genus'):
                genera.add(classification['genus'])
            if classification.get('family'):
                families.add(classification['family'])
            if classification.get('order'):
                orders.add(classification['order'])
            if classification.get('realm'):
                realms.add(classification['realm'])
        
        # Extract year from version
        try:
            year = int(version.replace('MSL', '')) + 1987
        except:
            year = None
        
        versions.append(VersionInfo(
            version=version,
            total_species=data['total'],
            total_genera=len(genera),
            total_families=len(families),
            total_orders=len(orders),
            total_realms=len(realms),
            year=year
        ))
    
    return versions


@app.get("/api/v1/species/{version}/{species_name}", response_model=SpeciesInfo)
async def get_species(version: str, species_name: str):
    """Get detailed information for a specific species."""
    if version not in TAXONOMY_DATA:
        raise HTTPException(status_code=404, detail=f"Version {version} not found")
    
    species_dict = TAXONOMY_DATA[version]['species']
    
    # Try exact match first
    if species_name in species_dict:
        return SpeciesInfo(**species_dict[species_name])
    
    # Try case-insensitive match
    for name, species in species_dict.items():
        if name.lower() == species_name.lower():
            return SpeciesInfo(**species)
    
    raise HTTPException(status_code=404, detail=f"Species '{species_name}' not found in {version}")


@app.get("/api/v1/search", response_model=SearchResult)
async def search_species(
    q: str = Query(..., description="Search query"),
    version: str = Query(..., description="MSL version to search"),
    field: str = Query("all", description="Field to search: all, name, genus, family, host"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum results to return")
):
    """Search for species matching query."""
    if version not in TAXONOMY_DATA:
        raise HTTPException(status_code=404, detail=f"Version {version} not found")
    
    results = []
    query_lower = q.lower()
    
    for species in TAXONOMY_DATA[version]['list']:
        matched = False
        
        if field == "all" or field == "name":
            if query_lower in species.get('scientific_name', '').lower():
                matched = True
        
        if not matched and (field == "all" or field == "genus"):
            if query_lower in species.get('classification', {}).get('genus', '').lower():
                matched = True
        
        if not matched and (field == "all" or field == "family"):
            if query_lower in species.get('classification', {}).get('family', '').lower():
                matched = True
        
        if not matched and (field == "all" or field == "host"):
            for host in species.get('hosts', []):
                if query_lower in host.lower():
                    matched = True
                    break
        
        if matched:
            results.append(SpeciesInfo(**species))
            if len(results) >= limit:
                break
    
    return SearchResult(
        query=q,
        version=version,
        total_results=len(results),
        results=results
    )


@app.get("/api/v1/taxonomy/{version}/{rank}/{name}", response_model=TaxonomicGroup)
async def get_taxonomic_group(version: str, rank: str, name: str):
    """Get all species in a taxonomic group."""
    if version not in TAXONOMY_DATA:
        raise HTTPException(status_code=404, detail=f"Version {version} not found")
    
    valid_ranks = ['realm', 'kingdom', 'phylum', 'class', 'order', 'family', 'genus']
    if rank not in valid_ranks:
        raise HTTPException(status_code=400, detail=f"Invalid rank. Must be one of: {valid_ranks}")
    
    indexes = TAXONOMY_DATA[version]['indexes']
    index_key = f'by_{rank}'
    
    if index_key not in indexes or name not in indexes[index_key]:
        raise HTTPException(status_code=404, detail=f"{rank.title()} '{name}' not found in {version}")
    
    species_names = indexes[index_key][name]
    
    return TaxonomicGroup(
        rank=rank,
        name=name,
        version=version,
        species_count=len(species_names),
        species_names=sorted(species_names)
    )


@app.get("/api/v1/compare/{version1}/{version2}", response_model=ComparisonSummary)
async def compare_versions(version1: str, version2: str):
    """Get summary comparison between two versions."""
    if version1 not in TAXONOMY_DATA or version2 not in TAXONOMY_DATA:
        raise HTTPException(status_code=404, detail="One or both versions not found")
    
    # Use the version comparator
    changes = VERSION_COMPARATOR.compare_versions(version1, version2)
    
    return ComparisonSummary(
        version1=version1,
        version2=version2,
        species_added=len(changes['added']),
        species_removed=len(changes['removed']),
        species_reclassified=len(changes['reclassified']),
        species_renamed=len(changes['renamed'])
    )


@app.get("/api/v1/compare/{version1}/{version2}/details")
async def compare_versions_detailed(
    version1: str, 
    version2: str,
    change_type: str = Query("all", description="Type of changes: all, added, removed, reclassified, renamed")
):
    """Get detailed comparison between two versions."""
    if version1 not in TAXONOMY_DATA or version2 not in TAXONOMY_DATA:
        raise HTTPException(status_code=404, detail="One or both versions not found")
    
    # Generate full comparison report
    report = VERSION_COMPARATOR.generate_comparison_report(version1, version2)
    
    if change_type == "all":
        return report
    elif change_type in report['changes']:
        return {
            'metadata': report['metadata'],
            'statistics': report['statistics'],
            change_type: report['changes'][change_type]
        }
    else:
        raise HTTPException(status_code=400, detail=f"Invalid change type: {change_type}")


@app.get("/api/v1/history/{species_name}")
async def get_species_history(species_name: str):
    """Get complete history of a species across all versions."""
    history = []
    
    for version in sorted(TAXONOMY_DATA.keys()):
        species_dict = TAXONOMY_DATA[version]['species']
        
        # Look for species (exact or fuzzy match)
        found_species = None
        for name, species in species_dict.items():
            if name == species_name or name.lower() == species_name.lower():
                found_species = species
                break
        
        if found_species:
            history.append({
                'version': version,
                'found': True,
                'classification': found_species.get('classification', {}),
                'genome': found_species.get('genome', {}),
                'hosts': found_species.get('hosts', [])
            })
        else:
            history.append({
                'version': version,
                'found': False
            })
    
    return {
        'species_name': species_name,
        'history': history,
        'first_appearance': next((h['version'] for h in history if h['found']), None),
        'last_appearance': next((h['version'] for h in reversed(history) if h['found']), None)
    }


@app.post("/api/v1/citation")
async def generate_citation(
    species_name: Optional[str] = None,
    version: str = Query(..., description="MSL version"),
    format: str = Query("standard", description="Citation format: standard, bibtex, ris, git"),
    taxonomic_group: Optional[Dict[str, str]] = None
):
    """Generate citation for species or taxonomic group."""
    if species_name:
        citation = CITATION_GENERATOR.cite_species(species_name, version, format)
    elif taxonomic_group:
        citation = CITATION_GENERATOR.cite_taxonomic_group(
            taxonomic_group['rank'],
            taxonomic_group['name'],
            version,
            format
        )
    else:
        raise HTTPException(status_code=400, detail="Must provide either species_name or taxonomic_group")
    
    return {
        "citation": citation,
        "format": format,
        "version": version
    }


@app.get("/api/v1/bulk/species/{version}")
async def bulk_download_species(
    version: str,
    format: str = Query("json", description="Output format: json, csv, yaml"),
    family: Optional[str] = Query(None, description="Filter by family"),
    genus: Optional[str] = Query(None, description="Filter by genus"),
    realm: Optional[str] = Query(None, description="Filter by realm")
):
    """Bulk download species data with optional filters."""
    if version not in TAXONOMY_DATA:
        raise HTTPException(status_code=404, detail=f"Version {version} not found")
    
    # Apply filters
    species_list = TAXONOMY_DATA[version]['list']
    filtered_species = []
    
    for species in species_list:
        classification = species.get('classification', {})
        
        # Check filters
        if family and classification.get('family') != family:
            continue
        if genus and classification.get('genus') != genus:
            continue
        if realm and classification.get('realm') != realm:
            continue
        
        filtered_species.append(species)
    
    # Format output
    if format == "json":
        return JSONResponse(content=filtered_species)
    
    elif format == "csv":
        # Create CSV in memory
        output = io.StringIO()
        
        if filtered_species:
            # Get all unique fields
            fieldnames = set()
            for species in filtered_species:
                fieldnames.update(species.keys())
                if 'classification' in species:
                    for k, v in species['classification'].items():
                        fieldnames.add(f"classification_{k}")
            
            fieldnames = sorted(list(fieldnames))
            
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            
            for species in filtered_species:
                row = {}
                for field in fieldnames:
                    if field.startswith('classification_'):
                        rank = field.replace('classification_', '')
                        row[field] = species.get('classification', {}).get(rank, '')
                    elif field == 'hosts':
                        row[field] = '; '.join(species.get('hosts', []))
                    elif field == 'classification':
                        continue  # Skip nested dict
                    else:
                        row[field] = species.get(field, '')
                
                writer.writerow(row)
        
        output.seek(0)
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode()),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=species_{version}.csv"}
        )
    
    elif format == "yaml":
        yaml_content = yaml.dump(filtered_species, default_flow_style=False)
        return StreamingResponse(
            io.BytesIO(yaml_content.encode()),
            media_type="application/x-yaml",
            headers={"Content-Disposition": f"attachment; filename=species_{version}.yaml"}
        )
    
    else:
        raise HTTPException(status_code=400, detail=f"Invalid format: {format}")


@app.get("/api/v1/stats/diversity/{version}")
async def get_diversity_stats(version: str):
    """Get diversity statistics for a version."""
    if version not in TAXONOMY_DATA:
        raise HTTPException(status_code=404, detail=f"Version {version} not found")
    
    data = TAXONOMY_DATA[version]
    
    # Calculate various diversity metrics
    stats = {
        'version': version,
        'total_species': data['total'],
        'taxonomic_ranks': {},
        'genome_types': {},
        'host_distribution': {},
        'largest_families': [],
        'most_diverse_genera': []
    }
    
    # Count by taxonomic rank
    for rank in ['realm', 'kingdom', 'phylum', 'class', 'order', 'family', 'genus']:
        index_key = f'by_{rank}'
        if index_key in data['indexes']:
            stats['taxonomic_ranks'][rank] = len(data['indexes'][index_key])
    
    # Genome type distribution
    for genome_type, species in data['indexes']['by_genome_type'].items():
        stats['genome_types'][genome_type] = len(species)
    
    # Host distribution (top 20)
    host_counts = [(host, len(species)) for host, species in data['indexes']['by_host'].items()]
    host_counts.sort(key=lambda x: x[1], reverse=True)
    stats['host_distribution'] = dict(host_counts[:20])
    
    # Largest families
    family_sizes = [(family, len(species)) for family, species in data['indexes']['by_family'].items()]
    family_sizes.sort(key=lambda x: x[1], reverse=True)
    stats['largest_families'] = [{'family': f[0], 'species_count': f[1]} for f in family_sizes[:10]]
    
    # Most diverse genera (by host range)
    genus_diversity = []
    for genus, species_names in data['indexes']['by_genus'].items():
        hosts = set()
        for species_name in species_names:
            species = data['species'].get(species_name, {})
            hosts.update(species.get('hosts', []))
        genus_diversity.append({'genus': genus, 'species_count': len(species_names), 'host_count': len(hosts)})
    
    genus_diversity.sort(key=lambda x: x['host_count'], reverse=True)
    stats['most_diverse_genera'] = genus_diversity[:10]
    
    return stats


def run_api(git_repo_path: str, host: str = "0.0.0.0", port: int = 8000):
    """Run the API server."""
    import uvicorn
    
    # Initialize the API with repo path
    api = TaxonomyAPI(git_repo_path)
    
    # Run the server
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        repo_path = sys.argv[1]
    else:
        repo_path = "output/git_taxonomy"
    
    run_api(repo_path)