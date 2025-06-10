#!/usr/bin/env python3
"""
Export MSL Excel files to CSV format for processing without pandas.

This script helps convert ICTV MSL Excel files to CSV format so they can be
processed using the simple_msl_parser.py which only requires built-in libraries.

NOTE: This script requires Excel or LibreOffice Calc to be installed on your system.
It will provide instructions for manual conversion if automated conversion fails.
"""

import subprocess
import sys
from pathlib import Path
import csv
import platform


def convert_with_libreoffice(excel_file: Path, csv_file: Path) -> bool:
    """Try to convert Excel to CSV using LibreOffice."""
    try:
        # Common LibreOffice paths
        libreoffice_paths = [
            '/Applications/LibreOffice.app/Contents/MacOS/soffice',  # macOS
            'soffice',  # Linux/Windows (if in PATH)
            '/usr/bin/soffice',  # Linux
            'C:\\Program Files\\LibreOffice\\program\\soffice.exe',  # Windows
        ]
        
        for soffice_path in libreoffice_paths:
            try:
                cmd = [
                    soffice_path,
                    '--headless',
                    '--convert-to',
                    'csv',
                    '--outdir',
                    str(csv_file.parent),
                    str(excel_file)
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"✅ Converted: {excel_file.name}")
                    return True
            except FileNotFoundError:
                continue
        
        return False
    except Exception as e:
        print(f"Error with LibreOffice conversion: {e}")
        return False


def convert_with_python_basic(excel_file: Path, csv_file: Path) -> bool:
    """
    Basic conversion attempt using csv module.
    Note: This won't work for Excel files, but provides the framework.
    """
    print(f"❌ Cannot convert {excel_file.name} without pandas or Excel/LibreOffice")
    return False


def provide_manual_instructions(excel_files: list) -> None:
    """Provide manual conversion instructions."""
    print("\n" + "="*60)
    print("MANUAL CONVERSION INSTRUCTIONS")
    print("="*60)
    print("\nTo convert MSL Excel files to CSV format manually:")
    print("\n1. Open each Excel file in Excel or LibreOffice Calc")
    print("2. Select the main data sheet (usually the first sheet)")
    print("3. File → Save As → CSV (Comma delimited)")
    print("4. Save with the same name but .csv extension")
    print("5. Place in the data/csv/ directory")
    
    print(f"\nFiles to convert ({len(excel_files)} total):")
    for i, excel_file in enumerate(excel_files[:5]):  # Show first 5
        print(f"   {i+1}. {excel_file.name}")
    if len(excel_files) > 5:
        print(f"   ... and {len(excel_files) - 5} more files")
    
    print("\nExample naming:")
    print("   MSL40_ICTV_Master_Species_List_2024_MSL40.v1.xlsx")
    print("   → MSL40_ICTV_Master_Species_List_2024_MSL40.v1.csv")


def main():
    """Main conversion function."""
    print("MSL Excel to CSV Converter")
    print("=" * 60)
    
    # Setup paths
    project_root = Path(__file__).parent.parent
    raw_dir = project_root / "data" / "raw"
    csv_dir = project_root / "data" / "csv"
    
    # Create CSV directory if needed
    csv_dir.mkdir(parents=True, exist_ok=True)
    
    # Find Excel files
    excel_files = list(raw_dir.glob("*.xlsx")) + list(raw_dir.glob("*.xls"))
    
    if not excel_files:
        print(f"❌ No Excel files found in {raw_dir}")
        return
    
    print(f"Found {len(excel_files)} Excel files in {raw_dir}")
    
    # Track conversion results
    converted = 0
    failed = []
    
    # Try to convert each file
    for excel_file in excel_files:
        csv_filename = excel_file.stem + ".csv"
        csv_file = csv_dir / csv_filename
        
        # Skip if already converted
        if csv_file.exists():
            print(f"⏭️  Skipping {excel_file.name} (CSV already exists)")
            converted += 1
            continue
        
        # Try LibreOffice conversion
        if convert_with_libreoffice(excel_file, csv_file):
            converted += 1
        else:
            failed.append(excel_file)
    
    # Summary
    print("\n" + "="*60)
    print("CONVERSION SUMMARY")
    print("="*60)
    print(f"✅ Successfully converted: {converted}")
    print(f"❌ Need manual conversion: {len(failed)}")
    
    if failed:
        provide_manual_instructions(failed)
    
    # Check if we have any CSV files to work with
    csv_files = list(csv_dir.glob("*.csv"))
    if csv_files:
        print(f"\n✅ {len(csv_files)} CSV files available in {csv_dir}")
        print("\nYou can now run analyses using:")
        print("   python src/simple_msl_parser.py")
    else:
        print(f"\n❌ No CSV files available yet in {csv_dir}")
        print("Please convert at least one MSL file to CSV format to proceed.")


if __name__ == "__main__":
    main()