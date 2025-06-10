"""
Base analyzer class for all research analyses.

Provides common functionality for loading MSL data, tracking changes over time,
and generating standardized outputs.
"""

from abc import ABC, abstractmethod
from pathlib import Path
import pandas as pd
import json
from typing import Dict, List, Any
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

class BaseAnalyzer(ABC):
    """Base class for all ICTV research analyzers."""
    
    def __init__(self, data_dir: Path = None):
        """Initialize analyzer with data directory."""
        if data_dir is None:
            data_dir = Path(__file__).parent.parent / "data" / "msl_files"
        self.data_dir = data_dir
        self.results = {}
        self.msl_versions = self._get_msl_versions()
        
    def _get_msl_versions(self) -> List[str]:
        """Get list of available MSL versions."""
        versions = []
        # Standard MSL version mapping
        version_map = {
            "MSL23": 2005, "MSL24": 2008, "MSL25": 2009, "MSL26": 2010,
            "MSL27": 2011, "MSL28": 2012, "MSL29": 2013, "MSL30": 2014,
            "MSL31": 2015, "MSL32": 2016, "MSL33": 2017, "MSL34": 2018,
            "MSL35": 2019, "MSL36": 2020, "MSL37": 2021, "MSL38": 2022,
            "MSL39": 2023, "MSL40": 2024
        }
        return version_map
    
    @abstractmethod
    def analyze(self) -> Dict[str, Any]:
        """Run the analysis. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def visualize(self) -> None:
        """Generate visualizations. Must be implemented by subclasses."""
        pass
    
    def save_results(self, output_dir: Path = None) -> None:
        """Save analysis results to JSON."""
        if output_dir is None:
            output_dir = Path(__file__).parent / self.__class__.__name__.lower() / "results"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / f"{self.__class__.__name__}_results.json"
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        print(f"Results saved to: {output_file}")
    
    def get_git_data(self, entity_type: str = "family") -> Dict[str, List[Dict]]:
        """Load data from git repository structure."""
        git_data = {}
        git_dir = Path(__file__).parent.parent / "ictv-git"
        
        # Navigate through git structure to find entities
        # This is a placeholder - actual implementation would parse git structure
        return git_data