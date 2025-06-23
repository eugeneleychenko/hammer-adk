#!/usr/bin/env python3
"""
Test script to verify the FileStructureValidator works correctly.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api_server import FileStructureValidator

def test_file_structure_validator():
    """Test the FileStructureValidator with existing files."""
    
    # Initialize validator
    validator = FileStructureValidator()
    
    # Test with a known file that should have results
    test_filename = "6QVUHKR7EYju1DF6_e-1018-1-mp3-st"
    
    print(f"Testing FileStructureValidator with filename: {test_filename}")
    print("=" * 60)
    
    # Get expected files
    expected_files = validator.get_expected_files(test_filename)
    print(f"Expected {len(expected_files)} files:")
    for file_type, file_path in expected_files.items():
        print(f"  {file_type}: {file_path}")
    
    print("\n" + "=" * 60)
    
    # Run validation
    validation_result = validator.validate_file_structure(test_filename)
    
    print("Validation Results:")
    print(f"  Validation Passed: {validation_result['validation_passed']}")
    print(f"  Files Found: {validation_result['files_found']}/{validation_result['total_expected']}")
    print(f"  Completion: {validation_result['completion_percentage']:.1f}%")
    
    if validation_result['files_missing']:
        print(f"  Missing Files: {validation_result['files_missing']}")
    
    if validation_result['files_present']:
        print(f"  Present Files: {validation_result['files_present']}")
    
    print("\n" + "=" * 60)
    print("Detailed File Status:")
    
    for file_type, details in validation_result['validation_details'].items():
        status = "✅ FOUND" if details['is_valid'] else "❌ MISSING"
        size = f"({details['size_bytes']} bytes)" if details['exists'] else ""
        print(f"  {status} {file_type}: {details['path']} {size}")
    
    print("\n" + "=" * 60)
    
    # Test retry logic
    print("Testing retry logic...")
    retry_result = validator.validate_and_retry(test_filename, max_retries=1)
    print(f"Retry validation passed: {retry_result['validation_passed']}")
    
    return validation_result

if __name__ == "__main__":
    result = test_file_structure_validator()
    
    if result['validation_passed']:
        print("\n🎉 SUCCESS: All expected files are present!")
        sys.exit(0)
    else:
        print(f"\n⚠️  WARNING: {len(result['files_missing'])} files are missing")
        print("This is expected if the web app hasn't been used to analyze this file yet.")
        sys.exit(1)