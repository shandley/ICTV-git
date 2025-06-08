"""
Citation generator for ICTV taxonomy versions.

Generates proper citations for:
- Specific species at specific versions
- Taxonomic groups at specific versions
- Version comparisons
- Git commits for reproducibility
"""

from pathlib import Path
import yaml
import json
from datetime import datetime
from typing import Dict, List, Optional
import git

class CitationGenerator:
    """Generate standardized citations for ICTV taxonomy."""
    
    # ICTV publication info by version
    ICTV_PUBLICATIONS = {
        'MSL36': {
            'year': 2021,
            'doi': '10.1007/s00705-021-05156-1',
            'authors': 'Walker PJ, Siddell SG, Lefkowitz EJ, et al.',
            'title': 'Recent changes to virus taxonomy ratified by the International Committee on Taxonomy of Viruses (2021)',
            'journal': 'Archives of Virology',
            'volume': '166',
            'pages': '2633-2648'
        },
        'MSL37': {
            'year': 2022,
            'doi': '10.1007/s00705-022-05516-5',
            'authors': 'Walker PJ, Siddell SG, Lefkowitz EJ, et al.',
            'title': 'Recent changes to virus taxonomy ratified by the International Committee on Taxonomy of Viruses (2022)',
            'journal': 'Archives of Virology',
            'volume': '167',
            'pages': '2429-2440'
        },
        'MSL38': {
            'year': 2023,
            'doi': '10.1007/s00705-023-05796-5',
            'authors': 'Zerbini FM, Siddell SG, Lefkowitz EJ, et al.',
            'title': 'Changes to virus taxonomy and the ICTV Statutes ratified by the International Committee on Taxonomy of Viruses (2023)',
            'journal': 'Archives of Virology',
            'volume': '168',
            'pages': '175'
        }
    }
    
    def __init__(self, git_repo_path: str):
        self.repo_path = Path(git_repo_path)
        self.repo = None
        self.version_data = {}
        
        # Try to load git repo
        try:
            self.repo = git.Repo(self.repo_path)
        except:
            print("Warning: Not a git repository. Git-specific citations unavailable.")
        
        self._load_version_metadata()
    
    def _load_version_metadata(self):
        """Load metadata for all versions."""
        metadata_file = self.repo_path / 'output' / 'version_metadata.json'
        if metadata_file.exists():
            with open(metadata_file, 'r') as f:
                self.version_data = json.load(f)
    
    def cite_species(self, species_name: str, version: str, 
                    format: str = 'standard') -> str:
        """Generate citation for a specific species at a specific version.
        
        Args:
            species_name: Scientific name of the species
            version: MSL version (e.g., 'MSL38')
            format: Citation format ('standard', 'bibtex', 'ris', 'git')
        
        Returns:
            Formatted citation string
        """
        # Load species data
        species_data = self._load_species_data(species_name, version)
        if not species_data:
            return f"Species '{species_name}' not found in {version}"
        
        # Get publication info
        pub_info = self.ICTV_PUBLICATIONS.get(version, {})
        
        if format == 'standard':
            return self._format_standard_species_citation(
                species_name, species_data, version, pub_info
            )
        elif format == 'bibtex':
            return self._format_bibtex_species_citation(
                species_name, species_data, version, pub_info
            )
        elif format == 'ris':
            return self._format_ris_species_citation(
                species_name, species_data, version, pub_info
            )
        elif format == 'git':
            return self._format_git_species_citation(
                species_name, species_data, version
            )
        else:
            return f"Unknown format: {format}"
    
    def _load_species_data(self, species_name: str, version: str) -> Optional[Dict]:
        """Load species data from repository."""
        version_dir = self.repo_path / 'output' / version
        if not version_dir.exists():
            return None
        
        # Search for species file
        for yaml_file in version_dir.rglob('*.yaml'):
            try:
                with open(yaml_file, 'r') as f:
                    data = yaml.safe_load(f)
                    if data and data.get('scientific_name') == species_name:
                        data['file_path'] = str(yaml_file.relative_to(version_dir))
                        return data
            except:
                continue
        
        return None
    
    def _format_standard_species_citation(self, species_name: str, 
                                        species_data: Dict, version: str,
                                        pub_info: Dict) -> str:
        """Format standard academic citation."""
        classification = species_data.get('classification', {})
        
        # Build taxonomic string
        tax_parts = []
        for rank in ['family', 'genus']:
            if rank in classification and classification[rank]:
                tax_parts.append(f"{rank.title()}: {classification[rank]}")
        
        taxonomic_info = ", ".join(tax_parts) if tax_parts else "Unclassified"
        
        # Get year
        year = pub_info.get('year', version.replace('MSL', '20'))
        
        citation = f"{species_name}. {taxonomic_info}. "
        
        if pub_info:
            citation += (f"In: {pub_info['authors']} ({year}) "
                        f"{pub_info['title']}. {pub_info['journal']} "
                        f"{pub_info['volume']}:{pub_info['pages']}. "
                        f"doi:{pub_info['doi']}")
        else:
            citation += f"ICTV Master Species List {version} ({year}). "
            citation += "International Committee on Taxonomy of Viruses. "
            citation += "https://ictv.global"
        
        return citation
    
    def _format_bibtex_species_citation(self, species_name: str, 
                                       species_data: Dict, version: str,
                                       pub_info: Dict) -> str:
        """Format BibTeX citation."""
        # Create citation key
        safe_name = species_name.replace(' ', '_').replace('-', '_')
        year = pub_info.get('year', version.replace('MSL', '20'))
        key = f"{safe_name}_{version}_{year}"
        
        classification = species_data.get('classification', {})
        
        bibtex = f"@misc{{{key},\n"
        bibtex += f"  title = {{{species_name}}},\n"
        bibtex += f"  author = {{International Committee on Taxonomy of Viruses}},\n"
        bibtex += f"  year = {{{year}}},\n"
        bibtex += f"  note = {{ICTV Master Species List {version}. "
        
        if 'family' in classification:
            bibtex += f"Family: {classification['family']}. "
        if 'genus' in classification:
            bibtex += f"Genus: {classification['genus']}. "
        
        bibtex += "}},\n"
        
        if pub_info and 'doi' in pub_info:
            bibtex += f"  doi = {{{pub_info['doi']}}},\n"
        
        bibtex += f"  url = {{https://ictv.global}}\n"
        bibtex += "}"
        
        return bibtex
    
    def _format_ris_species_citation(self, species_name: str, 
                                    species_data: Dict, version: str,
                                    pub_info: Dict) -> str:
        """Format RIS citation."""
        year = pub_info.get('year', version.replace('MSL', '20'))
        classification = species_data.get('classification', {})
        
        ris = "TY  - DATA\n"
        ris += f"TI  - {species_name}\n"
        ris += "AU  - International Committee on Taxonomy of Viruses\n"
        ris += f"PY  - {year}\n"
        ris += f"N1  - ICTV Master Species List {version}\n"
        
        if 'family' in classification:
            ris += f"N1  - Family: {classification['family']}\n"
        if 'genus' in classification:
            ris += f"N1  - Genus: {classification['genus']}\n"
        
        if pub_info and 'doi' in pub_info:
            ris += f"DO  - {pub_info['doi']}\n"
        
        ris += "UR  - https://ictv.global\n"
        ris += "ER  -"
        
        return ris
    
    def _format_git_species_citation(self, species_name: str, 
                                   species_data: Dict, version: str) -> str:
        """Format git-specific citation with commit hash."""
        file_path = species_data.get('file_path', '')
        
        citation = f"{species_name}\n"
        citation += f"Version: {version}\n"
        citation += f"File: {file_path}\n"
        
        if self.repo:
            try:
                # Get latest commit for this file
                full_path = self.repo_path / 'output' / version / file_path
                commits = list(self.repo.iter_commits(paths=str(full_path), max_count=1))
                
                if commits:
                    commit = commits[0]
                    citation += f"Git commit: {commit.hexsha[:8]}\n"
                    citation += f"Date: {commit.committed_datetime.isoformat()}\n"
                    citation += f"Repository: {self.repo_path}\n"
            except:
                pass
        
        return citation
    
    def cite_taxonomic_group(self, rank: str, name: str, version: str,
                           format: str = 'standard') -> str:
        """Generate citation for a taxonomic group (family, genus, etc.)."""
        # Count species in group
        species_count = self._count_species_in_group(rank, name, version)
        
        pub_info = self.ICTV_PUBLICATIONS.get(version, {})
        year = pub_info.get('year', version.replace('MSL', '20'))
        
        if format == 'standard':
            citation = f"{rank.title()} {name}. "
            citation += f"{species_count} species. "
            
            if pub_info:
                citation += (f"In: {pub_info['authors']} ({year}) "
                           f"{pub_info['title']}. {pub_info['journal']} "
                           f"{pub_info['volume']}:{pub_info['pages']}. "
                           f"doi:{pub_info['doi']}")
            else:
                citation += f"ICTV Master Species List {version} ({year}). "
                citation += "International Committee on Taxonomy of Viruses."
            
            return citation
        
        # Add other formats as needed
        return f"Format '{format}' not yet implemented for taxonomic groups"
    
    def _count_species_in_group(self, rank: str, name: str, version: str) -> int:
        """Count species in a taxonomic group."""
        version_dir = self.repo_path / 'output' / version
        if not version_dir.exists():
            return 0
        
        count = 0
        for yaml_file in version_dir.rglob('*.yaml'):
            try:
                with open(yaml_file, 'r') as f:
                    data = yaml.safe_load(f)
                    if data:
                        classification = data.get('classification', {})
                        if classification.get(rank) == name:
                            count += 1
            except:
                continue
        
        return count
    
    def cite_version_comparison(self, version1: str, version2: str,
                              format: str = 'standard') -> str:
        """Generate citation for version comparison."""
        year1 = self.ICTV_PUBLICATIONS.get(version1, {}).get('year', 
                                                             version1.replace('MSL', '20'))
        year2 = self.ICTV_PUBLICATIONS.get(version2, {}).get('year', 
                                                             version2.replace('MSL', '20'))
        
        if format == 'standard':
            citation = (f"ICTV Taxonomy Comparison: {version1} ({year1}) to "
                       f"{version2} ({year2}). International Committee on "
                       f"Taxonomy of Viruses. Retrieved from ICTV Git-based "
                       f"Taxonomy System, {datetime.now().strftime('%Y-%m-%d')}.")
            return citation
        
        return f"Format '{format}' not yet implemented for version comparisons"
    
    def generate_data_citation(self, description: str, 
                             versions_used: List[str],
                             format: str = 'standard') -> str:
        """Generate citation for research using multiple versions."""
        if not versions_used:
            return "No versions specified"
        
        years = []
        for version in versions_used:
            pub_info = self.ICTV_PUBLICATIONS.get(version, {})
            year = pub_info.get('year', version.replace('MSL', '20'))
            years.append(str(year))
        
        year_range = f"{min(years)}-{max(years)}" if len(set(years)) > 1 else years[0]
        
        if format == 'standard':
            citation = (f"{description}. Data from ICTV Master Species Lists "
                       f"{', '.join(versions_used)} ({year_range}). "
                       f"International Committee on Taxonomy of Viruses. "
                       f"Accessed via ICTV Git-based Taxonomy System. "
                       f"https://github.com/shandley/ICTV-git")
            
            if self.repo:
                try:
                    commit = self.repo.head.commit
                    citation += f" (commit {commit.hexsha[:8]})"
                except:
                    pass
            
            return citation
        
        return f"Format '{format}' not yet implemented for data citations"
    
    def export_citations(self, citations: List[Dict], output_path: str,
                        format: str = 'standard'):
        """Export multiple citations to file."""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        if format == 'bibtex':
            ext = '.bib'
        elif format == 'ris':
            ext = '.ris'
        else:
            ext = '.txt'
        
        output_file = output_file.with_suffix(ext)
        
        with open(output_file, 'w') as f:
            for i, cit_info in enumerate(citations):
                if i > 0:
                    f.write("\n\n")
                
                if 'species' in cit_info:
                    citation = self.cite_species(
                        cit_info['species'],
                        cit_info['version'],
                        format
                    )
                elif 'group' in cit_info:
                    citation = self.cite_taxonomic_group(
                        cit_info['rank'],
                        cit_info['group'],
                        cit_info['version'],
                        format
                    )
                else:
                    citation = "Invalid citation info"
                
                f.write(citation)
        
        print(f"Citations exported to: {output_file}")


def main():
    """Test citation generator."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate ICTV taxonomy citations")
    parser.add_argument("git_repo", help="Path to git taxonomy repository")
    parser.add_argument("--species", help="Species name to cite")
    parser.add_argument("--version", default="MSL38", help="MSL version")
    parser.add_argument("--format", default="standard", 
                       choices=['standard', 'bibtex', 'ris', 'git'],
                       help="Citation format")
    parser.add_argument("--family", help="Cite all species in family")
    parser.add_argument("--output", help="Output file for citations")
    
    args = parser.parse_args()
    
    generator = CitationGenerator(args.git_repo)
    
    if args.species:
        citation = generator.cite_species(args.species, args.version, args.format)
        print(citation)
        
        if args.output:
            generator.export_citations(
                [{'species': args.species, 'version': args.version}],
                args.output,
                args.format
            )
    
    elif args.family:
        citation = generator.cite_taxonomic_group(
            'family', args.family, args.version, args.format
        )
        print(citation)
    
    else:
        # Example citations
        print("Example Citations:\n")
        
        # Species citation
        species_example = generator.cite_species(
            "Severe acute respiratory syndrome-related coronavirus",
            "MSL38",
            "standard"
        )
        print("Species Citation:")
        print(species_example)
        print()
        
        # Data citation
        data_example = generator.generate_data_citation(
            "Viral taxonomy evolution analysis",
            ["MSL36", "MSL37", "MSL38"],
            "standard"
        )
        print("Data Citation:")
        print(data_example)


if __name__ == "__main__":
    main()