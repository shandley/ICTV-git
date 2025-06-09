"""
Historical API - 20-year taxonomy evolution access

Provides REST API access to historical changes, version comparisons,
and temporal analysis across the complete ICTV timeline (2005-2024).
"""

from typing import List, Dict, Optional, Tuple
from pathlib import Path
import subprocess
import json
import re
from datetime import datetime


class HistoricalAPI:
    """API for accessing 20-year taxonomic history via git"""
    
    def __init__(self, taxonomy_repo_path: str):
        """Initialize with path to complete 20-year taxonomy repository"""
        self.repo_path = Path(taxonomy_repo_path)
        self._validate_git_repo()
    
    def _validate_git_repo(self):
        """Ensure we have a valid git repository"""
        if not (self.repo_path / '.git').exists():
            raise ValueError(f"Not a git repository: {self.repo_path}")
    
    def _run_git_command(self, command: List[str]) -> str:
        """Execute git command and return output"""
        try:
            result = subprocess.run(
                ['git'] + command,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Git command failed: {e.stderr}")
    
    def get_msl_releases(self) -> List[Dict]:
        """
        Get all MSL releases with metadata
        
        Returns:
            List of MSL releases with chronological information
        """
        # Get all tags (MSL versions)
        tags_output = self._run_git_command(['tag', '--sort=version:refname'])
        tags = [tag for tag in tags_output.split('\n') if tag.startswith('MSL')]
        
        releases = []
        for tag in tags:
            # Get commit info for this tag
            commit_info = self._run_git_command(['show', '--format=%H|%ai|%s', '--no-patch', tag])
            commit_hash, commit_date, commit_message = commit_info.split('|', 2)
            
            # Extract MSL number
            msl_number = int(tag.replace('MSL', ''))
            
            # Try to get species count from commit message
            species_count = None
            count_match = re.search(r'Species:\s*([0-9,]+)', commit_message)
            if count_match:
                species_count = int(count_match.group(1).replace(',', ''))
            
            releases.append({
                'msl_version': tag,
                'msl_number': msl_number,
                'commit_hash': commit_hash,
                'commit_date': commit_date,
                'commit_message': commit_message,
                'species_count': species_count
            })
        
        return releases
    
    def get_release_details(self, msl_version: str) -> Optional[Dict]:
        """
        Get detailed information about a specific MSL release
        
        Args:
            msl_version: MSL version (e.g., 'MSL35', 'MSL40')
            
        Returns:
            Detailed release information
        """
        try:
            # Check if tag exists
            self._run_git_command(['rev-parse', '--verify', f'refs/tags/{msl_version}'])
            
            # Get commit details
            commit_info = self._run_git_command([
                'show', '--format=%H|%ai|%an|%ae|%s|%b', '--no-patch', msl_version
            ])
            
            lines = commit_info.split('\n')
            header = lines[0].split('|')
            commit_hash, commit_date, author_name, author_email, subject = header[:5]
            body = '\n'.join(lines[1:]) if len(lines) > 1 else ""
            
            # Get file changes
            files_changed = self._run_git_command(['diff-tree', '--no-commit-id', '--name-only', '-r', msl_version])
            file_list = [f for f in files_changed.split('\n') if f]
            
            # Get statistics
            stats_output = self._run_git_command(['diff-tree', '--stat', '--no-commit-id', '-r', msl_version])
            
            return {
                'msl_version': msl_version,
                'commit_hash': commit_hash,
                'commit_date': commit_date,
                'author': {
                    'name': author_name,
                    'email': author_email
                },
                'message': {
                    'subject': subject,
                    'body': body
                },
                'files_changed': file_list,
                'statistics': stats_output,
                'file_count': len(file_list)
            }
            
        except subprocess.CalledProcessError:
            return None
    
    def compare_releases(self, from_version: str, to_version: str) -> Dict:
        """
        Compare two MSL releases
        
        Args:
            from_version: Starting MSL version
            to_version: Ending MSL version
            
        Returns:
            Detailed comparison including changes and statistics
        """
        try:
            # Get diff statistics
            diff_stats = self._run_git_command(['diff', '--stat', f'{from_version}..{to_version}'])
            
            # Get changed files
            changed_files = self._run_git_command(['diff', '--name-only', f'{from_version}..{to_version}'])
            file_list = [f for f in changed_files.split('\n') if f]
            
            # Categorize changes
            added_files = []
            deleted_files = []
            modified_files = []
            
            for file_path in file_list:
                # Check file status
                try:
                    # File exists in to_version
                    self._run_git_command(['cat-file', '-e', f'{to_version}:{file_path}'])
                    try:
                        # File existed in from_version - modified
                        self._run_git_command(['cat-file', '-e', f'{from_version}:{file_path}'])
                        modified_files.append(file_path)
                    except subprocess.CalledProcessError:
                        # File didn't exist in from_version - added
                        added_files.append(file_path)
                except subprocess.CalledProcessError:
                    # File doesn't exist in to_version - deleted
                    deleted_files.append(file_path)
            
            # Get commit range
            commit_range = self._run_git_command(['rev-list', f'{from_version}..{to_version}'])
            commit_count = len([c for c in commit_range.split('\n') if c])
            
            return {
                'from_version': from_version,
                'to_version': to_version,
                'commit_count': commit_count,
                'statistics': diff_stats,
                'changes': {
                    'added_files': added_files,
                    'deleted_files': deleted_files,
                    'modified_files': modified_files,
                    'total_changes': len(file_list)
                },
                'file_breakdown': {
                    'added': len(added_files),
                    'deleted': len(deleted_files),
                    'modified': len(modified_files)
                }
            }
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to compare releases: {e}")
    
    def get_species_history(self, scientific_name: str) -> List[Dict]:
        """
        Get complete history of a species across all releases
        
        Args:
            scientific_name: Scientific name of the species
            
        Returns:
            List of historical states for this species
        """
        history = []
        releases = self.get_msl_releases()
        
        for release in releases:
            msl_version = release['msl_version']
            
            # Search for species in this release
            try:
                # Use git grep to find files containing this species name
                grep_result = self._run_git_command([
                    'grep', '-l', '--', f'scientific_name.*{scientific_name}', f'{msl_version}:'
                ])
                
                files = [f for f in grep_result.split('\n') if f and f.endswith('.yaml')]
                
                if files:
                    # Get the species file content
                    file_path = files[0]  # Take first match
                    content = self._run_git_command(['show', f'{msl_version}:{file_path}'])
                    
                    # Parse basic info from YAML
                    family_match = re.search(r'family:\s*"([^"]+)"', content)
                    genus_match = re.search(r'genus:\s*"([^"]+)"', content)
                    
                    history.append({
                        'msl_version': msl_version,
                        'commit_date': release['commit_date'],
                        'file_path': file_path,
                        'family': family_match.group(1) if family_match else None,
                        'genus': genus_match.group(1) if genus_match else None,
                        'exists': True
                    })
                else:
                    history.append({
                        'msl_version': msl_version,
                        'commit_date': release['commit_date'],
                        'exists': False
                    })
                    
            except subprocess.CalledProcessError:
                # Species not found in this release
                history.append({
                    'msl_version': msl_version,
                    'commit_date': release['commit_date'],
                    'exists': False
                })
        
        return history
    
    def get_family_evolution(self, family_name: str) -> Dict:
        """
        Track evolution of a viral family across releases
        
        Args:
            family_name: Name of the viral family
            
        Returns:
            Evolution data including species counts and major changes
        """
        releases = self.get_msl_releases()
        evolution = {
            'family_name': family_name,
            'timeline': [],
            'major_events': []
        }
        
        for release in releases:
            msl_version = release['msl_version']
            
            try:
                # Count species files in this family for this release
                family_pattern = f'{family_name.lower()}/genera/*/species/*.yaml'
                file_list = self._run_git_command([
                    'ls-tree', '-r', '--name-only', msl_version, '--', family_pattern
                ])
                
                species_files = [f for f in file_list.split('\n') if f.endswith('.yaml')]
                species_count = len(species_files)
                
                timeline_entry = {
                    'msl_version': msl_version,
                    'commit_date': release['commit_date'],
                    'species_count': species_count,
                    'exists': species_count > 0
                }
                
                evolution['timeline'].append(timeline_entry)
                
                # Detect major changes (>50% species count change)
                if len(evolution['timeline']) > 1:
                    prev_count = evolution['timeline'][-2]['species_count']
                    if prev_count > 0:
                        change_percent = abs(species_count - prev_count) / prev_count
                        if change_percent > 0.5:
                            evolution['major_events'].append({
                                'msl_version': msl_version,
                                'type': 'major_reorganization',
                                'description': f'Species count changed from {prev_count} to {species_count}',
                                'change_percent': change_percent
                            })
                
            except subprocess.CalledProcessError:
                # Family doesn't exist in this release
                evolution['timeline'].append({
                    'msl_version': msl_version,
                    'commit_date': release['commit_date'],
                    'species_count': 0,
                    'exists': False
                })
        
        return evolution
    
    def get_caudovirales_dissolution(self) -> Dict:
        """
        Get detailed information about the historic Caudovirales dissolution
        
        Returns:
            Comprehensive data about the MSL35 reorganization
        """
        # Compare MSL34 (before) to MSL35 (after dissolution)
        comparison = self.compare_releases('MSL34', 'MSL35')
        
        # Get specific details about the dissolution
        dissolution_data = {
            'event_name': 'Caudovirales Dissolution',
            'msl_version': 'MSL35',
            'year': 2019,
            'description': 'Historic reorganization eliminating order Caudovirales',
            'comparison': comparison,
            'significance': 'Most significant reorganization in ICTV history'
        }
        
        # Try to get more specific information about affected families
        try:
            # Look for siphoviridae changes
            msl34_sipho = self._run_git_command([
                'ls-tree', '-r', '--name-only', 'MSL34', '--', 'families/siphoviridae/'
            ])
            
            msl35_sipho = self._run_git_command([
                'ls-tree', '-r', '--name-only', 'MSL35', '--', 'families/siphoviridae/'
            ])
            
            dissolution_data['siphoviridae_impact'] = {
                'files_before': len([f for f in msl34_sipho.split('\n') if f]),
                'files_after': len([f for f in msl35_sipho.split('\n') if f])
            }
            
        except subprocess.CalledProcessError:
            pass
        
        return dissolution_data
    
    def get_timeline_summary(self) -> Dict:
        """
        Get high-level summary of the 20-year timeline
        
        Returns:
            Summary statistics and major milestones
        """
        releases = self.get_msl_releases()
        
        if not releases:
            return {'error': 'No releases found'}
        
        first_release = releases[0]
        last_release = releases[-1]
        
        # Calculate growth
        first_count = first_release.get('species_count', 0)
        last_count = last_release.get('species_count', 0)
        growth_rate = ((last_count - first_count) / first_count * 100) if first_count > 0 else 0
        
        # Identify major milestones
        milestones = []
        for release in releases:
            if release['msl_version'] == 'MSL35':
                milestones.append({
                    'msl_version': 'MSL35',
                    'year': 2019,
                    'event': 'Caudovirales Dissolution',
                    'significance': 'Historic reorganization'
                })
            elif release['msl_version'] == 'MSL36':
                milestones.append({
                    'msl_version': 'MSL36', 
                    'year': 2020,
                    'event': 'COVID-19 Pandemic Response',
                    'significance': 'Emergency taxonomy protocols'
                })
        
        return {
            'timeline_span': f"{first_release['msl_version']} to {last_release['msl_version']}",
            'total_releases': len(releases),
            'years_covered': 20,
            'species_growth': {
                'initial_count': first_count,
                'final_count': last_count,
                'growth_rate_percent': round(growth_rate, 1),
                'total_increase': last_count - first_count
            },
            'major_milestones': milestones,
            'repository_path': str(self.repo_path),
            'git_tags': len(releases),
            'complete_history': True
        }