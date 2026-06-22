"""
Main entry point for the Leiloaria Property PDF Generator pipeline
"""

import sys
import argparse
from pipeline import PropertyPDFPipeline

def main():
    parser = argparse.ArgumentParser(
        description="Automated Leiloaria Property PDF Generator Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate PDFs for all properties
  python main.py

  # Generate PDFs for first 10 properties
  python main.py --limit 10

  # Resume from property 50 (skip first 50)
  python main.py --skip 50

  # Generate PDFs for 20 properties starting from property 50
  python main.py --limit 20 --skip 50
        """
    )

    parser.add_argument(
        '--limit', '-l',
        type=int,
        default=None,
        help='Maximum number of properties to process (default: all)'
    )

    parser.add_argument(
        '--skip', '-s',
        type=int,
        default=0,
        help='Number of properties to skip (for resuming) (default: 0)'
    )

    args = parser.parse_args()

    # Run pipeline
    pipeline = PropertyPDFPipeline()
    success_count = pipeline.run(limit=args.limit, skip_count=args.skip)

    # Exit with appropriate code
    sys.exit(0 if success_count > 0 else 1)

if __name__ == "__main__":
    main()
