"""
PDF export and processing utilities
"""

import subprocess
from pathlib import Path
from pypdf import PdfReader, PdfWriter
from typing import Optional
from config import LIBREOFFICE_PATH, LINK_PDF

class PDFExporter:
    """Export PPTX to PDF and handle PDF operations"""

    @staticmethod
    def pptx_to_pdf(pptx_path: Path, output_dir: Path) -> Optional[Path]:
        """Export PPTX to PDF using LibreOffice

        Args:
            pptx_path: Path to PPTX file
            output_dir: Directory to save PDF

        Returns:
            Path to generated PDF or None if export fails
        """
        try:
            subprocess.run([
                str(LIBREOFFICE_PATH),
                "--headless",
                "--convert-to", "pdf",
                "--outdir", str(output_dir),
                str(pptx_path)
            ], timeout=60, check=True)

            # LibreOffice generates PDF with same name as PPTX
            generated_pdf = output_dir / f"{pptx_path.stem}.pdf"
            if generated_pdf.exists():
                return generated_pdf

            print(f"[WARN] PDF not found at expected location: {generated_pdf}")
            return None

        except subprocess.TimeoutExpired:
            print(f"[ERROR] LibreOffice timeout while converting {pptx_path}")
            return None
        except FileNotFoundError:
            print(f"[ERROR] LibreOffice not found at {LIBREOFFICE_PATH}")
            return None
        except Exception as e:
            print(f"[ERROR] Error converting to PDF: {e}")
            return None

    @staticmethod
    def append_link_page(pdf_path: Path) -> bool:
        """Append link page from template PDF to generated PDF

        Args:
            pdf_path: Path to PDF to modify

        Returns:
            True if successful, False otherwise
        """
        try:
            if not LINK_PDF.exists():
                print(f"[WARN] Link PDF template not found at {LINK_PDF}")
                return False

            reader = PdfReader(str(LINK_PDF))
            if not reader.pages:
                print(f"[WARN] Link PDF is empty")
                return False

            link_page = reader.pages[-1]

            pdf_reader = PdfReader(str(pdf_path))
            writer = PdfWriter()

            # Add original pages
            for page in pdf_reader.pages:
                writer.add_page(page)

            # Add link page
            writer.add_page(link_page)

            # Write back
            with open(pdf_path, 'wb') as f:
                writer.write(f)

            return True

        except Exception as e:
            print(f"[WARN] Could not add link page: {e}")
            return False
