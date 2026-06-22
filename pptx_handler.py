"""
PowerPoint template handling - text and image replacement
"""

import zipfile
import shutil
import os
from pathlib import Path
from io import BytesIO
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from PIL import Image
from typing import Optional, Dict
from config import SLIDE_WIDTH_INCHES, SLIDE_HEIGHT_INCHES

class PPTXHandler:
    """Handle PPTX template modifications - text and image replacement"""

    @staticmethod
    def replace_embedded_images(pptx_path: Path, image_pil: Image.Image) -> bool:
        """NOT USED - Embedded images are left alone to avoid affecting logos/decorations.
        The middle image will come through the background via the actual slide image addition.

        Args:
            pptx_path: Path to PPTX file
            image_pil: PIL Image to use as replacement

        Returns:
            True (no-op, just skipped)
        """
        print(f"    Skipping embedded image replacement (using background image instead)")
        return True

    @staticmethod
    def modify_text(template_pptx: Path, property_data: Dict, output_pptx: Path) -> Path:
        """Modify text in PPTX while preserving formatting

        Args:
            template_pptx: Path to template PPTX file
            property_data: Property data dict with keys like 'titulo', 'cidade', etc
            output_pptx: Path to save modified PPTX

        Returns:
            Path to output PPTX
        """
        prs = Presentation(str(template_pptx))
        slide = prs.slides[0]

        # Calculate date shorthand (MM/DD from MM/DD/YYYY)
        praca1_data = property_data.get('praca1_data', '')
        praca2_data = property_data.get('praca2_data', '')
        praca1_date_short = praca1_data.split('/')[0] + '/' + praca1_data.split('/')[1] if praca1_data else '15/06'
        praca2_date_short = praca2_data.split('/')[0] + '/' + praca2_data.split('/')[1] if praca2_data else '30/06'

        desconto_pct = property_data.get('desconto_pct')
        desconto_text = f"{int(desconto_pct)}% DE DESCONTO!" if desconto_pct else "20% DE DESCONTO!"

        # Text replacement mapping for all template types
        new_title = property_data.get('titulo', '')
        location = f"{property_data.get('cidade', '')}/{property_data.get('estado', '')}"

        replacements = {
            # Title placeholders (different templates have different defaults)
            "Lote de Terreno 300m²": new_title,
            "Terrenos em Cond. até 566m²": new_title,
            "Casa 147m²": new_title,
            "Apartamento 102m²": new_title,
            # Location placeholders
            "NOVA ODESSA/SP": location,
            "TERESINA/PI": location,
            "UBERLÂNDIA/MG": location,
            # Price placeholders (both auctions)
            "R$ 255.056,73": property_data.get('praca1_valor', '') or 'R$ 0,00',
            "R$ 142.920,39": property_data.get('praca1_valor', '') or 'R$ 0,00',
            "R$ 245.848,12": property_data.get('praca2_valor', '') or 'R$ 0,00',
            # Date placeholders
            "15/06": praca1_date_short,
            "02/07": praca1_date_short,
            "30/06": praca2_date_short,
            # Discount
            "20% DE DESCONTO!": desconto_text,
        }

        # Replace text in all shapes on slide 1
        for shape in slide.shapes:
            if hasattr(shape, "text_frame"):
                original_text = shape.text.strip()

                if original_text in replacements:
                    new_text = replacements[original_text]
                    text_frame = shape.text_frame

                    # Disable word wrap to prevent text hanging
                    text_frame.word_wrap = False

                    for paragraph in text_frame.paragraphs:
                        if paragraph.runs:
                            first_run = paragraph.runs[0]
                            font_copy = first_run.font

                            # Clear existing runs
                            for run in paragraph.runs:
                                run.text = ""

                            # Add new text with preserved formatting
                            new_run = paragraph.add_run()
                            new_run.text = new_text

                            # Preserve formatting from original
                            new_run.font.name = font_copy.name
                            new_run.font.size = font_copy.size
                            new_run.font.bold = font_copy.bold
                            new_run.font.italic = font_copy.italic
                            if font_copy.color.rgb:
                                new_run.font.color.rgb = font_copy.color.rgb

        prs.save(str(output_pptx))
        return output_pptx

    @staticmethod
    def replace_images(pptx_path: Path, image_pil: Image.Image) -> bool:
        """Replace embedded images (image1.jpeg or image2.jpeg) in PPTX via ZIP.
        Delete Group 2 (gray background) so the replaced image shows through.
        Handle both slides separately to avoid image mixing.

        Args:
            pptx_path: Path to PPTX file to modify
            image_pil: PIL Image object with property image

        Returns:
            True if successful, False otherwise
        """
        try:
            import tempfile
            from image_processor import ImageProcessor

            # Process image (crop + RGB conversion)
            image_cropped = ImageProcessor.crop_sidebars(image_pil)
            image_rgb = ImageProcessor.to_rgb(image_cropped)

            print(f"    Image size after processing: {image_rgb.size}")

            # Step 1: Replace embedded image (image2.jpeg) via ZIP manipulation for slide 1 only
            # Note: We only replace image2.jpeg, not image1.png, to avoid conflicts with slide 2
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_dir = Path(temp_dir)

                # Extract PPTX
                with zipfile.ZipFile(pptx_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)

                # Replace ONLY image2.jpeg (the main placeholder for slide 1)
                # Do NOT replace image1.jpeg/image1.png as it's shared with slide 2
                media_dir = temp_dir / "ppt" / "media"
                replaced = False

                sky_image_path = media_dir / "image2.jpeg"
                if sky_image_path.exists():
                    image_rgb.save(str(sky_image_path), quality=95)
                    print(f"    Replaced embedded image: image2.jpeg")
                    replaced = True
                else:
                    print(f"    [WARN] image2.jpeg not found in template")

                # Re-zip the PPTX
                with zipfile.ZipFile(pptx_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for root, dirs, files in os.walk(temp_dir):
                        for file in files:
                            file_path = Path(root) / file
                            arcname = file_path.relative_to(temp_dir)
                            zipf.write(file_path, arcname)

            # Step 2: Open PPTX and delete Group 2 from slide 1
            # This reveals the replaced embedded image
            prs = Presentation(str(pptx_path))

            print(f"    Processing slide 1...")
            slide1 = prs.slides[0]

            # Delete Group 2 (the gray background) so the property image shows
            for shape in list(slide1.shapes):
                if shape.name == "Group 2":
                    try:
                        sp = shape.element
                        sp.getparent().remove(sp)
                        print(f"    Deleted Group 2 (gray background)")
                        break
                    except Exception as e:
                        print(f"    Failed to delete Group 2: {e}")

            # Step 3: Process Slide 2 (if it exists)
            if len(prs.slides) >= 2:
                print(f"    Processing slide 2...")
                slide2 = prs.slides[1]

                # Delete Freeform shapes from slide 2 (they create overlapping lines)
                # Keep Groups and TextBoxes (they contain frames and text)
                deleted_count = 0
                for shape in list(slide2.shapes):
                    # Only delete Freeforms (decorative lines that overlap)
                    if 'Freeform' in shape.name:
                        try:
                            sp = shape.element
                            sp.getparent().remove(sp)
                            deleted_count += 1
                        except Exception as e:
                            pass

                if deleted_count > 0:
                    print(f"    Deleted {deleted_count} freeform shapes from slide 2")

                # Add the property image as background to slide 2 (squished 85% width, 90% height)
                img_stream2 = BytesIO()
                image_rgb.save(img_stream2, format='JPEG', quality=95)
                img_stream2.seek(0)

                # Apply squishing to slide 2 background: 90% height for gray rectangle alignment
                bg_width = Inches(11.25 * 0.90)  # 90% width for gray rectangle
                bg_height = Inches(14.06 * 0.90)  # 90% height
                # Center the image
                bg_left = Inches((11.25 - (11.25 * 0.90)) / 2)
                bg_top = Inches((14.06 - (14.06 * 0.90)) / 2)

                picture_bg2 = slide2.shapes.add_picture(
                    img_stream2,
                    bg_left,
                    bg_top,
                    width=bg_width,
                    height=bg_height
                )

                # Move to position 2 (behind text boxes)
                slide2.shapes._spTree.remove(picture_bg2._element)
                slide2.shapes._spTree.insert(2, picture_bg2._element)
                print(f"    Added background image to slide 2 (squished 90%)")

            # Step 4: Save presentation ONCE after all modifications
            prs.save(str(pptx_path))
            print(f"    All slides complete, saved")

            return True

        except Exception as e:
            print(f"[ERROR] Error replacing images: {e}")
            import traceback
            traceback.print_exc()
            return False

    @staticmethod
    def add_link_page(pptx_path: Path, image_pil: Image.Image) -> bool:
        """NO-OP: Both slides are now handled in replace_images() in a single pass.

        Args:
            pptx_path: Path to PPTX file
            image_pil: PIL Image object

        Returns:
            True (skipped, already done)
        """
        print(f"    Skipping add_link_page (already handled in replace_images)")
        return True
