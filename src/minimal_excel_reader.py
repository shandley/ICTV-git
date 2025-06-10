#!/usr/bin/env python3
"""
Minimal Excel reader using only built-in libraries.
Reads Excel 2007+ (.xlsx) files by parsing the XML directly.
"""

import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Dict, Any, Optional
import re


class MinimalExcelReader:
    """Basic Excel reader that extracts data from .xlsx files."""
    
    def __init__(self, file_path: str):
        """Initialize with Excel file path."""
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"Excel file not found: {file_path}")
        if self.file_path.suffix != '.xlsx':
            raise ValueError("Only .xlsx files are supported (not .xls)")
        
        self.shared_strings = []
        self.headers = []
        self.data = []
    
    def read(self) -> List[Dict[str, str]]:
        """Read the Excel file and return data as list of dictionaries."""
        try:
            with zipfile.ZipFile(self.file_path, 'r') as z:
                # Read shared strings (used for text values)
                self._read_shared_strings(z)
                
                # Read the first worksheet
                self._read_worksheet(z)
                
            return self.data
            
        except Exception as e:
            print(f"Error reading Excel file: {e}")
            return []
    
    def _read_shared_strings(self, z: zipfile.ZipFile) -> None:
        """Read shared strings from Excel file."""
        try:
            with z.open('xl/sharedStrings.xml') as f:
                tree = ET.parse(f)
                root = tree.getroot()
                
                # Extract all shared strings
                for si in root.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}si'):
                    text_elem = si.find('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t')
                    if text_elem is not None and text_elem.text:
                        self.shared_strings.append(text_elem.text)
                    else:
                        self.shared_strings.append('')
        except KeyError:
            # Some Excel files might not have shared strings
            pass
    
    def _read_worksheet(self, z: zipfile.ZipFile) -> None:
        """Read the first worksheet."""
        # Find the first worksheet
        worksheet_path = 'xl/worksheets/sheet1.xml'
        
        with z.open(worksheet_path) as f:
            tree = ET.parse(f)
            root = tree.getroot()
            
            # Find all rows
            rows = root.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row')
            
            if not rows:
                return
            
            # Process first row as headers
            header_row = rows[0]
            self.headers = self._process_row(header_row)
            
            # Process data rows
            for row in rows[1:]:
                row_data = self._process_row(row)
                if row_data and any(row_data):  # Skip empty rows
                    # Create dictionary with headers as keys
                    row_dict = {}
                    for i, header in enumerate(self.headers):
                        if i < len(row_data) and row_data[i]:
                            row_dict[header] = row_data[i]
                        else:
                            row_dict[header] = ''
                    self.data.append(row_dict)
    
    def _process_row(self, row_elem) -> List[str]:
        """Process a single row element."""
        cells = row_elem.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c')
        row_data = []
        
        for cell in cells:
            # Get cell reference (e.g., A1, B2)
            cell_ref = cell.get('r', '')
            col_index = self._get_column_index(cell_ref)
            
            # Pad row_data to ensure correct column position
            while len(row_data) < col_index:
                row_data.append('')
            
            # Get cell value
            value = self._get_cell_value(cell)
            row_data.append(value)
        
        return row_data
    
    def _get_column_index(self, cell_ref: str) -> int:
        """Convert cell reference to column index (A=0, B=1, etc.)."""
        match = re.match(r'([A-Z]+)\d+', cell_ref)
        if not match:
            return 0
        
        col_letters = match.group(1)
        index = 0
        for i, char in enumerate(reversed(col_letters)):
            index += (ord(char) - ord('A') + 1) * (26 ** i)
        return index - 1
    
    def _get_cell_value(self, cell_elem) -> str:
        """Extract value from a cell element."""
        cell_type = cell_elem.get('t', 'n')  # Default to number
        value_elem = cell_elem.find('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
        
        if value_elem is None or value_elem.text is None:
            return ''
        
        value = value_elem.text
        
        # Handle different cell types
        if cell_type == 's':  # Shared string
            try:
                index = int(value)
                if 0 <= index < len(self.shared_strings):
                    return self.shared_strings[index]
            except (ValueError, IndexError):
                pass
        elif cell_type == 'str':  # Inline string
            is_elem = cell_elem.find('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}is')
            if is_elem is not None:
                t_elem = is_elem.find('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t')
                if t_elem is not None and t_elem.text:
                    return t_elem.text
        
        # Return raw value for numbers and other types
        return value
    
    def get_statistics(self) -> Dict[str, Any]:
        """Calculate basic statistics from the data."""
        stats = {
            'total_rows': len(self.data),
            'columns': self.headers,
            'families': {},
            'orders': {},
            'species_count': 0
        }
        
        # Find relevant columns (case-insensitive matching)
        headers_lower = {h.lower(): h for h in self.headers}
        
        species_col = None
        family_col = None
        order_col = None
        
        # Common column name variations
        for species_name in ['species', 'virus name', 'current species name']:
            if species_name in headers_lower:
                species_col = headers_lower[species_name]
                break
        
        for family_name in ['family', 'current family']:
            if family_name in headers_lower:
                family_col = headers_lower[family_name]
                break
        
        for order_name in ['order', 'current order']:
            if order_name in headers_lower:
                order_col = headers_lower[order_name]
                break
        
        # Count statistics
        for row in self.data:
            if species_col and row.get(species_col):
                stats['species_count'] += 1
                
                if family_col and row.get(family_col):
                    family = row[family_col]
                    stats['families'][family] = stats['families'].get(family, 0) + 1
                
                if order_col and row.get(order_col):
                    order = row[order_col]
                    stats['orders'][order] = stats['orders'].get(order, 0) + 1
        
        stats['total_families'] = len(stats['families'])
        stats['total_orders'] = len(stats['orders'])
        
        return stats


def demo_minimal_reader():
    """Demonstrate the minimal Excel reader."""
    print("Minimal Excel Reader Demo")
    print("=" * 60)
    
    # Find Excel files
    data_dir = Path(__file__).parent.parent / "data" / "raw"
    excel_files = list(data_dir.glob("*.xlsx"))
    
    if not excel_files:
        print(f"No .xlsx files found in {data_dir}")
        return
    
    print(f"Found {len(excel_files)} Excel files")
    
    # Process each file
    for excel_file in sorted(excel_files)[:3]:  # Process first 3 files
        print(f"\n{'='*60}")
        print(f"Processing: {excel_file.name}")
        print('='*60)
        
        try:
            reader = MinimalExcelReader(str(excel_file))
            data = reader.read()
            
            if data:
                stats = reader.get_statistics()
                print(f"Total rows: {stats['total_rows']}")
                print(f"Species count: {stats['species_count']}")
                print(f"Total families: {stats['total_families']}")
                print(f"Total orders: {stats['total_orders']}")
                
                # Show top 3 families
                if stats['families']:
                    print("\nTop 3 families by species count:")
                    sorted_families = sorted(stats['families'].items(), 
                                           key=lambda x: x[1], reverse=True)
                    for family, count in sorted_families[:3]:
                        print(f"  {family}: {count} species")
                
                # Show sample data
                print("\nSample data (first 2 rows):")
                for i, row in enumerate(data[:2]):
                    print(f"\nRow {i+1}:")
                    # Show only first few columns
                    shown_cols = 0
                    for key, value in row.items():
                        if value and shown_cols < 5:
                            print(f"  {key}: {value}")
                            shown_cols += 1
            else:
                print("No data extracted")
                
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    demo_minimal_reader()