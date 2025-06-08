#!/usr/bin/env python3
"""
Download ICTV Master Species List (MSL) files.

This script downloads MSL Excel files from the ICTV website,
with fallback web scraping if direct URLs fail.
"""

import os
import sys
import requests
from pathlib import Path
from typing import Dict, List, Optional
import logging
from datetime import datetime
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MSLDownloader:
    """Downloads ICTV MSL files with caching and fallback mechanisms."""
    
    # Known direct URLs (as of January 2025)
    KNOWN_URLS = {
        'MSL40': 'https://ictv.global/sites/default/files/MSL/ICTV_Master_Species_List_2024_MSL40.v1.xlsx',
        'MSL39': 'https://ictv.global/sites/default/files/MSL/ICTV_Master_Species_List_2023_MSL39.v3.xlsx',
        'MSL38': 'https://ictv.global/sites/default/files/MSL/ICTV_Master_Species_List_2022_MSL38.v3.xlsx',
        'MSL37': 'https://ictv.global/sites/default/files/MSL/ICTV_Master_Species_List_2021_MSL37.v1.xlsx',
    }
    
    # ICTV MSL listing page
    MSL_LIST_URL = 'https://ictv.global/msl'
    
    def __init__(self, data_dir: Optional[str] = None):
        """Initialize downloader with data directory."""
        if data_dir:
            self.data_dir = Path(data_dir)
        else:
            self.data_dir = Path(__file__).parent.parent / 'data' / 'raw'
        
        # Create directory if it doesn't exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Data directory: {self.data_dir}")
    
    def download_file(self, url: str, filename: str) -> bool:
        """Download a file from URL to data directory."""
        filepath = self.data_dir / filename
        
        # Check if file already exists
        if filepath.exists():
            logger.info(f"File already exists: {filename}")
            return True
        
        logger.info(f"Downloading {filename} from {url}")
        
        try:
            # Download with streaming to handle large files
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            # Save file
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"Successfully downloaded: {filename}")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to download {filename}: {e}")
            return False
    
    def scrape_msl_urls(self) -> Dict[str, str]:
        """Scrape ICTV website for MSL file URLs."""
        logger.info(f"Scraping MSL URLs from {self.MSL_LIST_URL}")
        
        try:
            response = requests.get(self.MSL_LIST_URL, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Find all Excel file links
            excel_links = {}
            
            # Look for links containing 'Master_Species_List' and ending with .xlsx
            for link in soup.find_all('a', href=True):
                href = link['href']
                
                if 'Master_Species_List' in href and href.endswith('.xlsx'):
                    # Extract MSL version number
                    match = re.search(r'MSL(\d+)', href)
                    if match:
                        msl_version = f"MSL{match.group(1)}"
                        full_url = urljoin(self.MSL_LIST_URL, href)
                        excel_links[msl_version] = full_url
                        logger.info(f"Found {msl_version}: {full_url}")
            
            return excel_links
            
        except Exception as e:
            logger.error(f"Failed to scrape MSL URLs: {e}")
            return {}
    
    def download_known_msls(self) -> Dict[str, bool]:
        """Download MSL files using known URLs."""
        results = {}
        
        for msl_version, url in self.KNOWN_URLS.items():
            # Generate filename
            filename = f"{msl_version}_{Path(url).name}"
            success = self.download_file(url, filename)
            results[msl_version] = success
        
        return results
    
    def download_all_available(self) -> Dict[str, bool]:
        """Download all available MSL files with fallback to scraping."""
        results = {}
        
        # First try known URLs
        logger.info("Attempting to download from known URLs...")
        known_results = self.download_known_msls()
        results.update(known_results)
        
        # If any failed, try scraping for updated URLs
        failed = [v for v, success in known_results.items() if not success]
        if failed:
            logger.info(f"Some downloads failed: {failed}")
            logger.info("Attempting to scrape current URLs...")
            
            scraped_urls = self.scrape_msl_urls()
            
            for msl_version in failed:
                if msl_version in scraped_urls:
                    url = scraped_urls[msl_version]
                    filename = f"{msl_version}_{Path(url).name}"
                    success = self.download_file(url, filename)
                    results[msl_version] = success
        
        # Also try to find any newer MSL versions
        logger.info("Checking for newer MSL versions...")
        scraped_urls = self.scrape_msl_urls()
        
        for msl_version, url in scraped_urls.items():
            if msl_version not in results:
                filename = f"{msl_version}_{Path(url).name}"
                success = self.download_file(url, filename)
                results[msl_version] = success
        
        return results
    
    def list_downloaded_files(self) -> List[str]:
        """List all downloaded MSL files."""
        excel_files = list(self.data_dir.glob("*.xlsx"))
        return sorted([f.name for f in excel_files])


def main():
    """Main function to download MSL files."""
    downloader = MSLDownloader()
    
    print("ICTV MSL Downloader")
    print("=" * 50)
    
    # Download all available files
    results = downloader.download_all_available()
    
    # Summary
    print("\nDownload Summary:")
    print("-" * 50)
    
    successful = [v for v, success in results.items() if success]
    failed = [v for v, success in results.items() if not success]
    
    if successful:
        print(f"✓ Successfully downloaded: {', '.join(successful)}")
    
    if failed:
        print(f"✗ Failed to download: {', '.join(failed)}")
    
    # List all files
    print("\nAvailable MSL files:")
    print("-" * 50)
    
    files = downloader.list_downloaded_files()
    if files:
        for filename in files:
            filepath = downloader.data_dir / filename
            size_mb = filepath.stat().st_size / (1024 * 1024)
            print(f"  - {filename} ({size_mb:.1f} MB)")
    else:
        print("  No MSL files found")
    
    print(f"\nFiles saved to: {downloader.data_dir}")
    
    # Return exit code based on results
    if failed:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()