"""
Database Synchronization System

Real-time synchronization of viral taxonomy across major sequence databases.
Detects mismatches and generates corrections to keep databases in sync with ICTV.
"""

import asyncio
import aiohttp
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import logging

try:
    from Bio import Entrez, SeqIO
    HAS_BIOPYTHON = True
except ImportError:
    HAS_BIOPYTHON = False


@dataclass
class TaxonomyMismatch:
    """Represents a taxonomy mismatch between databases"""
    database: str
    accession: str
    species_name: str
    current_classification: Dict[str, str]
    correct_classification: Dict[str, str]
    entries_affected: int
    last_updated: datetime
    severity: str  # 'low', 'medium', 'high', 'critical'


@dataclass
class SyncReport:
    """Report of synchronization operations"""
    database: str
    total_checked: int
    mismatches_found: int
    corrections_submitted: int
    corrections_accepted: int
    execution_time: float
    timestamp: datetime


class DatabaseAdapter:
    """Base class for database-specific adapters"""
    
    def __init__(self, name: str):
        self.name = name
        self.api_calls_today = 0
        self.rate_limit = 1000  # Default daily limit
    
    async def get_classification(self, species_name: str) -> Optional[Dict[str, str]]:
        """Get current classification for a species"""
        raise NotImplementedError
    
    async def submit_correction(self, correction: Dict[str, Any]) -> bool:
        """Submit taxonomy correction"""
        raise NotImplementedError
    
    async def get_entries_count(self, species_name: str) -> int:
        """Count entries for a species"""
        raise NotImplementedError


class GenBankAdapter(DatabaseAdapter):
    """Adapter for NCBI GenBank database"""
    
    def __init__(self, email: str):
        super().__init__("GenBank")
        self.email = email
        if HAS_BIOPYTHON:
            Entrez.email = email
        self.rate_limit = 3  # NCBI allows 3 requests per second
        self.last_request = 0
    
    async def _rate_limit_check(self):
        """Ensure we don't exceed rate limits"""
        current_time = time.time()
        time_since_last = current_time - self.last_request
        
        if time_since_last < (1.0 / self.rate_limit):
            await asyncio.sleep((1.0 / self.rate_limit) - time_since_last)
        
        self.last_request = time.time()
    
    async def get_classification(self, species_name: str) -> Optional[Dict[str, str]]:
        """Get GenBank taxonomy for species"""
        if not HAS_BIOPYTHON:
            return None
        
        await self._rate_limit_check()
        
        try:
            # Search for species in taxonomy database
            handle = Entrez.esearch(db="taxonomy", term=species_name)
            search_results = Entrez.read(handle)
            handle.close()
            
            if not search_results["IdList"]:
                return None
            
            # Get taxonomy details
            tax_id = search_results["IdList"][0]
            handle = Entrez.efetch(db="taxonomy", id=tax_id)
            tax_record = Entrez.read(handle)
            handle.close()
            
            if tax_record:
                lineage = tax_record[0]["Lineage"]
                return self._parse_lineage(lineage)
        
        except Exception as e:
            logging.error(f"GenBank lookup failed for {species_name}: {e}")
        
        return None
    
    def _parse_lineage(self, lineage: str) -> Dict[str, str]:
        """Parse GenBank lineage into taxonomic ranks"""
        # This is a simplified parser - real implementation would be more robust
        parts = [part.strip() for part in lineage.split(';')]
        
        classification = {}
        
        # Try to identify common viral families and orders
        for part in parts:
            if part.endswith('viridae'):
                classification['family'] = part
            elif part.endswith('virales'):
                classification['order'] = part
            elif part.endswith('virus'):
                classification['genus'] = part
        
        return classification
    
    async def submit_correction(self, correction: Dict[str, Any]) -> bool:
        """Submit taxonomy correction to GenBank"""
        # GenBank doesn't have a public API for taxonomy updates
        # This would require manual submission or specialized access
        logging.info(f"GenBank correction would be submitted manually: {correction}")
        return False  # Placeholder
    
    async def get_entries_count(self, species_name: str) -> int:
        """Count GenBank entries for species"""
        if not HAS_BIOPYTHON:
            return 0
        
        await self._rate_limit_check()
        
        try:
            handle = Entrez.esearch(db="nucleotide", term=f'"{species_name}"[organism]')
            search_results = Entrez.read(handle)
            handle.close()
            
            return int(search_results["Count"])
        
        except Exception as e:
            logging.error(f"GenBank count failed for {species_name}: {e}")
            return 0


class RefSeqAdapter(DatabaseAdapter):
    """Adapter for NCBI RefSeq database"""
    
    def __init__(self, email: str):
        super().__init__("RefSeq")
        self.email = email
    
    async def get_classification(self, species_name: str) -> Optional[Dict[str, str]]:
        """Get RefSeq taxonomy - similar to GenBank but curated"""
        # RefSeq uses same taxonomy as GenBank but is more curated
        # Implementation would be similar but focus on RefSeq entries
        return None  # Placeholder
    
    async def submit_correction(self, correction: Dict[str, Any]) -> bool:
        """Submit RefSeq taxonomy correction"""
        # RefSeq corrections require evidence and formal submission
        return False  # Placeholder


class UniProtAdapter(DatabaseAdapter):
    """Adapter for UniProt protein database"""
    
    def __init__(self):
        super().__init__("UniProt")
        self.base_url = "https://rest.uniprot.org"
    
    async def get_classification(self, species_name: str) -> Optional[Dict[str, str]]:
        """Get UniProt taxonomy for viral proteins"""
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/uniprotkb/search"
            params = {
                "query": f"organism:{species_name}",
                "format": "json",
                "size": 1
            }
            
            try:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data["results"]:
                            organism = data["results"][0]["organism"]
                            return self._parse_uniprot_taxonomy(organism)
            
            except Exception as e:
                logging.error(f"UniProt lookup failed for {species_name}: {e}")
        
        return None
    
    def _parse_uniprot_taxonomy(self, organism: Dict) -> Dict[str, str]:
        """Parse UniProt organism info to taxonomy"""
        classification = {}
        
        if "lineage" in organism:
            for rank in organism["lineage"]:
                rank_name = rank.get("scientificName", "")
                if rank_name.endswith("viridae"):
                    classification["family"] = rank_name
                elif rank_name.endswith("virales"):
                    classification["order"] = rank_name
        
        return classification


class MismatchDetector:
    """Detect taxonomy mismatches across databases"""
    
    def __init__(self, ictv_git_path: str):
        self.ictv_git_path = ictv_git_path
        self.adapters = {}
    
    def add_adapter(self, adapter: DatabaseAdapter):
        """Add database adapter"""
        self.adapters[adapter.name] = adapter
    
    async def scan_species(self, species_name: str) -> List[TaxonomyMismatch]:
        """Scan for mismatches for a single species"""
        mismatches = []
        
        # Get ICTV canonical classification
        ictv_classification = self._get_ictv_classification(species_name)
        if not ictv_classification:
            return mismatches
        
        # Check each database
        for db_name, adapter in self.adapters.items():
            try:
                db_classification = await adapter.get_classification(species_name)
                
                if db_classification and db_classification != ictv_classification:
                    entries_count = await adapter.get_entries_count(species_name)
                    
                    mismatch = TaxonomyMismatch(
                        database=db_name,
                        accession="",  # Would get specific accessions
                        species_name=species_name,
                        current_classification=db_classification,
                        correct_classification=ictv_classification,
                        entries_affected=entries_count,
                        last_updated=datetime.now(),
                        severity=self._calculate_severity(db_classification, ictv_classification, entries_count)
                    )
                    
                    mismatches.append(mismatch)
            
            except Exception as e:
                logging.error(f"Error checking {db_name} for {species_name}: {e}")
        
        return mismatches
    
    def _get_ictv_classification(self, species_name: str) -> Optional[Dict[str, str]]:
        """Get current ICTV classification from git repo"""
        # This would search the git repository for the species
        # For now, return placeholder
        return {
            "family": "Coronaviridae",
            "genus": "Betacoronavirus",
            "order": "Nidovirales"
        }
    
    def _calculate_severity(self, current: Dict, correct: Dict, entries_count: int) -> str:
        """Calculate severity of mismatch"""
        if entries_count > 1000:
            return "critical"
        elif entries_count > 100:
            return "high"
        elif entries_count > 10:
            return "medium"
        else:
            return "low"


class DatabaseSync:
    """Main database synchronization system"""
    
    def __init__(self, ictv_git_path: str, email: str):
        self.ictv_git_path = ictv_git_path
        self.email = email
        self.detector = MismatchDetector(ictv_git_path)
        self.sync_reports = []
        
        # Initialize adapters
        self._setup_adapters()
    
    def _setup_adapters(self):
        """Setup database adapters"""
        if HAS_BIOPYTHON:
            genbank = GenBankAdapter(self.email)
            refseq = RefSeqAdapter(self.email)
            self.detector.add_adapter(genbank)
            self.detector.add_adapter(refseq)
        
        uniprot = UniProtAdapter()
        self.detector.add_adapter(uniprot)
    
    async def scan_all_databases(self, species_list: List[str] = None) -> List[TaxonomyMismatch]:
        """Scan all databases for mismatches"""
        if species_list is None:
            species_list = self._get_all_species()
        
        all_mismatches = []
        
        for species in species_list:
            mismatches = await self.detector.scan_species(species)
            all_mismatches.extend(mismatches)
        
        return all_mismatches
    
    def _get_all_species(self) -> List[str]:
        """Get all species from ICTV git repository"""
        # This would scan the git repo for all species
        # For now, return sample species
        return [
            "SARS-CoV-2",
            "Tobacco mosaic virus",
            "Human immunodeficiency virus 1",
            "Influenza A virus"
        ]
    
    async def generate_corrections(self, mismatches: List[TaxonomyMismatch]) -> List[Dict[str, Any]]:
        """Generate correction submissions for mismatches"""
        corrections = []
        
        for mismatch in mismatches:
            correction = {
                "database": mismatch.database,
                "species": mismatch.species_name,
                "current": mismatch.current_classification,
                "corrected": mismatch.correct_classification,
                "priority": mismatch.severity,
                "entries_affected": mismatch.entries_affected,
                "submission_type": self._determine_submission_type(mismatch)
            }
            
            corrections.append(correction)
        
        return corrections
    
    def _determine_submission_type(self, mismatch: TaxonomyMismatch) -> str:
        """Determine how to submit correction"""
        if mismatch.database == "GenBank":
            return "manual_submission"  # Requires manual process
        elif mismatch.database == "RefSeq":
            return "evidence_based"     # Requires evidence package
        elif mismatch.database == "UniProt":
            return "automated"          # May have API
        else:
            return "manual"
    
    async def run_continuous_sync(self, check_interval_hours: int = 24):
        """Run continuous synchronization monitoring"""
        logging.info("Starting continuous database synchronization...")
        
        while True:
            try:
                start_time = time.time()
                
                # Scan for mismatches
                mismatches = await self.scan_all_databases()
                
                # Generate corrections
                corrections = await self.generate_corrections(mismatches)
                
                # Log results
                execution_time = time.time() - start_time
                
                report = SyncReport(
                    database="All",
                    total_checked=len(self._get_all_species()),
                    mismatches_found=len(mismatches),
                    corrections_submitted=len(corrections),
                    corrections_accepted=0,  # Would track actual submissions
                    execution_time=execution_time,
                    timestamp=datetime.now()
                )
                
                self.sync_reports.append(report)
                
                logging.info(f"Sync complete: {len(mismatches)} mismatches found, {len(corrections)} corrections generated")
                
                # Wait for next check
                await asyncio.sleep(check_interval_hours * 3600)
            
            except Exception as e:
                logging.error(f"Sync error: {e}")
                await asyncio.sleep(3600)  # Wait 1 hour on error
    
    def get_sync_dashboard_data(self) -> Dict[str, Any]:
        """Get data for sync status dashboard"""
        if not self.sync_reports:
            return {"status": "No sync data available"}
        
        latest = self.sync_reports[-1]
        
        return {
            "last_sync": latest.timestamp.isoformat(),
            "total_species": latest.total_checked,
            "mismatches_found": latest.mismatches_found,
            "corrections_pending": latest.corrections_submitted - latest.corrections_accepted,
            "execution_time": latest.execution_time,
            "sync_frequency": "24 hours",
            "databases_monitored": list(self.detector.adapters.keys()),
            "status": "active"
        }


# For testing
if __name__ == "__main__":
    async def test_sync():
        """Test the synchronization system"""
        sync = DatabaseSync("output/git_taxonomy", "test@example.com")
        
        # Test species scan
        test_species = ["SARS-CoV-2", "Tobacco mosaic virus"]
        mismatches = await sync.scan_all_databases(test_species)
        
        print(f"Found {len(mismatches)} mismatches")
        for mismatch in mismatches:
            print(f"- {mismatch.database}: {mismatch.species_name} ({mismatch.severity})")
        
        # Test dashboard data
        dashboard = sync.get_sync_dashboard_data()
        print(f"Dashboard: {dashboard}")
    
    # Run test
    asyncio.run(test_sync())