"""
Image export utilities for Instagram posts
"""

import subprocess
import tempfile
from pathlib import Path
from PIL import Image
from typing import List
from config import LIBREOFFICE_PATH

class ImageExporter:
    """Export PPTX slides to PNG images for Instagram"""

    # Instagram dimensions for vertical posts (cropped from bottom to preserve logo)
    INSTAGRAM_WIDTH = 1080
    INSTAGRAM_HEIGHT = 1285  # Cropped to preserve top logo/band

    @staticmethod
    def pptx_to_png(pptx_path: Path, output_dir: Path) -> List[Path]:
        """Export PPTX slides to PNG images for Instagram using ImageMagick

        Args:
            pptx_path: Path to PPTX file
            output_dir: Directory to save PNG files

        Returns:
            List of paths to generated PNG files
        """
        try:
            png_files = []

            with tempfile.TemporaryDirectory() as temp_dir:
                temp_dir = Path(temp_dir)

                # Step 1: Convert PPTX to PDF using LibreOffice
                # Use simple filename without special characters for ImageMagick compatibility
                pdf_path = temp_dir / "output.pdf"
                try:
                    import time
                    time.sleep(0.5)  # Small delay to ensure file is ready

                    result = subprocess.run([
                        str(LIBREOFFICE_PATH),
                        "--headless",
                        "--convert-to", "pdf",
                        "--outdir", str(temp_dir),
                        str(pptx_path)
                    ], timeout=120, capture_output=True, text=True)

                    if result.returncode != 0:
                        print(f"[WARN] LibreOffice error - returncode: {result.returncode}")
                        if result.stderr:
                            print(f"[WARN] LibreOffice stderr: {result.stderr[:200]}")
                        if result.stdout:
                            print(f"[WARN] LibreOffice stdout: {result.stdout[:200]}")

                except subprocess.TimeoutExpired:
                    print(f"[ERROR] LibreOffice timeout")
                    return []

                # Verify PDF was created
                if not pdf_path.exists():
                    # Check what files were created (LibreOffice may use different filename)
                    pdf_files = list(temp_dir.glob("*.pdf"))
                    if pdf_files:
                        pdf_path = pdf_files[0]
                    else:
                        print(f"[ERROR] PDF conversion failed - no PDF generated")
                        return []

                # Step 2: Use ImageMagick to convert PDF to PNG (one file per page)
                # Create output pattern for multiple pages
                output_pattern = str(temp_dir / "slide_%d.png")

                # Try different ImageMagick command names and paths
                magick_commands = [
                    r"C:\Program Files\ImageMagick-7.1.2-Q16\magick.exe",
                    r"C:\Program Files\ImageMagick-7\magick.exe",
                    r"C:\Program Files (x86)\ImageMagick-7\magick.exe",
                    "magick",
                    "convert",
                ]

                magick_exe = None
                for cmd in magick_commands:
                    try:
                        result = subprocess.run([cmd, "--version"], capture_output=True, timeout=5)
                        if result.returncode == 0:
                            magick_exe = cmd
                            break
                    except:
                        continue

                if not magick_exe:
                    print(f"[ERROR] ImageMagick not found. Tried: {magick_commands}")
                    return []

                result = subprocess.run([
                    magick_exe,
                    "-density", "300",
                    "-quality", "95",
                    str(pdf_path),
                    output_pattern
                ], timeout=120, capture_output=True, text=True)

                if result.returncode != 0:
                    print(f"[WARN] ImageMagick error - returncode: {result.returncode}")
                    if result.stderr:
                        print(f"[WARN] ImageMagick stderr: {result.stderr[:300]}")
                    if result.stdout:
                        print(f"[WARN] ImageMagick stdout: {result.stdout[:300]}")

                # Find all generated PNG files
                generated_pngs = sorted(temp_dir.glob("slide_*.png"))

                if not generated_pngs:
                    print(f"[ERROR] ImageMagick conversion failed - no PNG files generated")
                    return []

                # Process each PNG: crop and move to output directory
                for idx, png_path in enumerate(generated_pngs, start=1):
                    try:
                        # Open and crop the image
                        img = Image.open(str(png_path))
                        img_cropped = ImageExporter._crop_for_instagram(img)

                        # Save to output directory with proper naming
                        png_filename = f"{pptx_path.stem}_slide{idx}.png"
                        output_path = output_dir / png_filename
                        img_cropped.save(str(output_path), 'PNG', optimize=False)
                        png_files.append(output_path)
                        print(f"    Exported slide {idx} to {png_filename} ({img_cropped.width}x{img_cropped.height})")

                    except Exception as e:
                        print(f"[WARN] Failed to process PNG slide {idx}: {e}")
                        continue

            return png_files

        except subprocess.TimeoutExpired:
            print(f"[ERROR] Conversion timeout")
            return []
        except FileNotFoundError as e:
            print(f"[ERROR] Required tool not found: {e}")
            return []
        except Exception as e:
            print(f"[ERROR] Error exporting PPTX to PNG: {e}")
            return []

    @staticmethod
    def _crop_for_instagram(img: Image.Image) -> Image.Image:
        """Crop image to Instagram dimensions, preserving top logo/band

        Args:
            img: PIL Image object

        Returns:
            Cropped PIL Image (1080x1285)
        """
        target_width = ImageExporter.INSTAGRAM_WIDTH
        target_height = ImageExporter.INSTAGRAM_HEIGHT

        # Resize to target width first, preserving aspect ratio
        scale = target_width / img.width
        new_height = int(img.height * scale)
        img_resized = img.resize((target_width, new_height), Image.Resampling.LANCZOS)

        # Crop from TOP (index 0) to preserve logo at the very top
        # Take exactly target_height pixels starting from top
        if img_resized.height >= target_height:
            img_cropped = img_resized.crop((0, 0, target_width, target_height))
        else:
            # Image is shorter than target - shouldn't happen but handle it
            img_cropped = img_resized

        return img_cropped
