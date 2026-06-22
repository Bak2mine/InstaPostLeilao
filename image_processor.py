"""
Image processing utilities for downloading and processing property images
"""

import requests
from PIL import Image
from io import BytesIO
from typing import Optional
from config import TIMEOUT, IMAGE_CROP_PERCENT

class ImageProcessor:
    """Download and process images from property pages"""

    @staticmethod
    def download_image(image_url: str) -> Optional[Image.Image]:
        """Download image from URL and return PIL Image object

        Args:
            image_url: Full URL to image

        Returns:
            PIL Image object or None if download fails
        """
        try:
            response = requests.get(image_url, timeout=TIMEOUT)
            if response.status_code == 200:
                return Image.open(BytesIO(response.content))
        except Exception as e:
            print(f"[WARN] Error downloading image: {e}")
        return None

    @staticmethod
    def crop_sidebars(image: Image.Image, crop_percent: float = IMAGE_CROP_PERCENT) -> Image.Image:
        """Crop sidebars from image and bottom pixels for Instagram optimization

        Args:
            image: PIL Image object
            crop_percent: Percentage to crop from each side (0.20 = 20%)

        Returns:
            Cropped PIL Image object
        """
        width, height = image.size
        crop_left = int(width * crop_percent)
        crop_right = int(width * (1 - crop_percent))
        # Also crop 5 pixels from bottom for proper framing
        crop_bottom = height - 5

        # Crop and then resize to be narrower (squish from sides)
        # This makes the image fit better on the slide
        cropped = image.crop((crop_left, 0, crop_right, crop_bottom))

        # Resize to 85% width while maintaining height for "squish" effect
        new_width = int(cropped.width * 0.85)
        cropped = cropped.resize((new_width, cropped.height), Image.Resampling.LANCZOS)

        return cropped

    @staticmethod
    def to_rgb(image: Image.Image) -> Image.Image:
        """Convert image to RGB mode"""
        return image.convert('RGB')

    @staticmethod
    def process_for_pptx(image: Image.Image) -> Image.Image:
        """Process image for use in PPTX (crop + RGB conversion)"""
        cropped = ImageProcessor.crop_sidebars(image)
        return ImageProcessor.to_rgb(cropped)
