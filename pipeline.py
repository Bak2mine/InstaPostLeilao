"""
Main automated pipeline - orchestrates the complete flow:
Scrape → Extract Data → Get Image → Fill Template → Export PDF
"""

import re
import time
from pathlib import Path
from typing import Optional, Dict, List

from config import TEMPLATES, OUTPUT_DIR
from scraper import PropertyScraper
from image_processor import ImageProcessor
from pptx_handler import PPTXHandler
from pdf_exporter import PDFExporter

class PropertyPDFPipeline:
    """Complete automated pipeline for property PDF generation"""

    def __init__(self):
        self.scraper = PropertyScraper()
        self.output_dir = OUTPUT_DIR
        self.output_dir.mkdir(exist_ok=True)

    def sanitize_filename(self, title: str) -> str:
        """Remove invalid filename characters

        Args:
            title: Original title

        Returns:
            Sanitized filename-safe title
        """
        # Remove state indicator if present (after em-dash or hyphen)
        title = re.sub(r'\s*[–-].*$', '', title).strip()
        # Remove invalid filename characters
        title = re.sub(r'[<>:"/\\|?*]', '', title)
        # Replace forward slashes with dashes
        title = title.replace('/', ' - ')
        return title.strip()

    def validate_property_data(self, property_data: Dict) -> bool:
        """Validate that required fields are present

        Args:
            property_data: Property data dict

        Returns:
            True if all required fields present, False otherwise
        """
        required_fields = ['titulo', 'cidade', 'estado', 'praca1_valor', 'praca1_data', 'tipo']
        missing = [f for f in required_fields if not property_data.get(f)]

        if missing:
            print(f"    [WARN] Missing fields: {', '.join(missing)}")
            return False

        return True

    def process_property(self, auction: Dict, property_data: Dict) -> Optional[Path]:
        """Process single property through entire pipeline

        Args:
            auction: Dict with 'title' and 'url'
            property_data: Extracted property data dict

        Returns:
            Path to generated PDF or None if failed
        """
        # Validate data
        if not self.validate_property_data(property_data):
            return None

        # Get template
        template_type = property_data.get('tipo')
        if template_type not in TEMPLATES:
            print(f"    [ERROR] Unknown template type: {template_type}")
            return None

        template_pptx = TEMPLATES[template_type]['pptx']
        if not template_pptx.exists():
            print(f"    [ERROR] Template not found: {template_pptx}")
            return None

        # Prepare output filenames
        safe_title = self.sanitize_filename(auction['title'])
        pptx_path = self.output_dir / f"{safe_title}.pptx"
        pdf_path = self.output_dir / f"{safe_title}.pdf"

        print(f"    [1/5] Modifying PPTX text...")
        try:
            PPTXHandler.modify_text(template_pptx, property_data, pptx_path)
        except Exception as e:
            print(f"    [ERROR] Failed to modify PPTX: {e}")
            return None

        # Get property page HTML to extract image
        print(f"    [2/5] Fetching property page...")
        html = self.scraper.get_property_page_html(property_data['auction_url'])
        if not html:
            print(f"    [WARN] Could not fetch property page")
            image = None
        else:
            print(f"    [3/5] Extracting and downloading image...")
            image_url = self.scraper.extract_first_image_url(html)
            if image_url:
                print(f"    Image URL: {image_url[:80]}...")
                image = ImageProcessor.download_image(image_url)
                if image:
                    print(f"    Downloaded: {image.size}")
                else:
                    print(f"    [WARN] Failed to download image")
                    image = None
            else:
                print(f"    [WARN] No image URL found in page source")
                image = None

        # Replace images in PPTX
        print(f"    [4/5] Replacing images in PPTX...")
        if image:
            # First replace embedded images (the small middle image)
            PPTXHandler.replace_embedded_images(pptx_path, image)

            # Then replace/add background image
            if not PPTXHandler.replace_images(pptx_path, image):
                print(f"    [WARN] Could not replace background images")

            # Add link page with image (use the SAME image object to ensure consistency)
            if not PPTXHandler.add_link_page(pptx_path, image):
                print(f"    [WARN] Could not add link page")
        else:
            print(f"    [WARN] Skipped image replacement (no image available)")

        # Export to PDF
        print(f"    [5/5] Exporting to PDF...")
        pdf_file = PDFExporter.pptx_to_pdf(pptx_path, self.output_dir)
        if not pdf_file:
            print(f"    [ERROR] Failed to export PDF")
            return None

        # Append link page
        if not PDFExporter.append_link_page(pdf_file):
            print(f"    [WARN] Could not append link page to PDF")

        print(f"    [OK] Generated: {pdf_file.name}")
        return pdf_file

    def run(self, limit: Optional[int] = None, skip_count: int = 0) -> int:
        """Run complete pipeline

        Args:
            limit: Maximum properties to process (None = all)
            skip_count: Number of properties to skip (for resuming)

        Returns:
            Number of successfully generated PDFs
        """
        print("=" * 70)
        print("LEILOARIA PROPERTY PDF GENERATOR - AUTOMATED PIPELINE")
        print("=" * 70)

        # Get all auctions
        print(f"\n[STEP 1] Scraping property listings...")
        auctions = self.scraper.get_all_auctions(limit=limit)

        if not auctions:
            print("[ERROR] No properties found")
            return 0

        # Apply skip count
        if skip_count > 0:
            auctions = auctions[skip_count:]
            print(f"[INFO] Skipped {skip_count} properties, processing {len(auctions)} remaining")

        # Process each property
        print(f"\n[STEP 2] Processing properties...")
        success_count = 0
        failed_count = 0

        for i, auction in enumerate(auctions, start=skip_count + 1):
            print(f"\n[{i}/{len(auctions) + skip_count}] {auction['title']}")

            property_data = self.scraper.get_property_data(auction['url'], auction['title'])
            if not property_data:
                print(f"    [ERROR] Failed to extract property data")
                failed_count += 1
                time.sleep(0.5)
                continue

            pdf_result = self.process_property(auction, property_data)
            if pdf_result:
                success_count += 1
            else:
                failed_count += 1

            # Rate limiting
            time.sleep(0.5)

        # Summary
        print(f"\n" + "=" * 70)
        print(f"PIPELINE COMPLETE")
        print("=" * 70)
        print(f"Total properties scraped: {len(auctions) + skip_count}")
        print(f"Successfully generated: {success_count}")
        print(f"Failed: {failed_count}")
        print(f"Output directory: {self.output_dir}")
        print("=" * 70)

        return success_count
