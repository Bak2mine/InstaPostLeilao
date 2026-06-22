"""
Test script to validate the pipeline with a single property
"""

from pathlib import Path
from pipeline import PropertyPDFPipeline
from config import OUTPUT_DIR

def test_single_property():
    """Test pipeline with first property only"""
    print("=" * 70)
    print("PIPELINE TEST - SINGLE PROPERTY")
    print("=" * 70)

    pipeline = PropertyPDFPipeline()

    # Test with just 1 property
    success_count = pipeline.run(limit=1)

    # Check output
    output_files = list(OUTPUT_DIR.glob("*"))
    print(f"\nGenerated files: {len(output_files)}")
    for f in sorted(output_files):
        size = f.stat().st_size / (1024*1024)  # Convert to MB
        print(f"  - {f.name} ({size:.2f} MB)")

    if success_count > 0:
        print("\n✓ Test PASSED - Pipeline working correctly")
        return True
    else:
        print("\n✗ Test FAILED - Check errors above")
        return False

if __name__ == "__main__":
    success = test_single_property()
    exit(0 if success else 1)
