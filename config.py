"""
Configuration and constants for the Leiloaria PDF/PPTX generation pipeline
"""

from pathlib import Path
import sys
import os

# When running as PyInstaller EXE, templates are in a temporary directory
# But we want output files to go to the current working directory (where user runs the EXE)
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    # Running as bundled EXE
    TEMPLATE_DIR = Path(sys._MEIPASS) / 'Post'  # Templates inside EXE
    USER_DIR = Path.cwd()  # Current working directory (where EXE was run from)
else:
    # Running as Python script
    TEMPLATE_DIR = Path(__file__).parent
    USER_DIR = Path(__file__).parent

POST_DIR = TEMPLATE_DIR  # For template lookup
IMOVEIS_DIR = USER_DIR / "imoveis"
OUTPUT_DIR = USER_DIR / "output"
TEMP_DIR = USER_DIR / ".temp"

# Create directories if they don't exist
for directory in [IMOVEIS_DIR, OUTPUT_DIR, TEMP_DIR]:
    directory.mkdir(exist_ok=True)

# Website configuration
BASE_URL = "https://leiloariasmart.com.br"
MAIN_URL = "https://leiloariasmart.com.br/busca"
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
TIMEOUT = 30

# Template configuration
TEMPLATES = {
    'tipo1': {  # Duas praças + desconto
        'pptx': POST_DIR / "1 e 2 praça.pptx",
        'description': 'Two auctions with discount'
    },
    'tipo2': {  # Uma praça + desconto
        'pptx': POST_DIR / "2praca.pptx",
        'description': 'Single auction with discount'
    },
    'tipo3': {  # Duas praças sem desconto
        'pptx': POST_DIR / "1prac.pptx",
        'description': 'Two auctions without discount'
    },
    'tipo4': {  # Uma praça sem desconto
        'pptx': POST_DIR / "tipo4.pptx",
        'description': 'Single auction without discount'
    }
}

# LibreOffice path for PDF conversion
LIBREOFFICE_PATH = r"C:\Program Files\LibreOffice\program\soffice.exe"

# Link PDF template
LINK_PDF = POST_DIR / "Posts IG.pdf"

# Image processing
IMAGE_CROP_PERCENT = 0.20  # Crop 20% from left and right
IMAGE_FORMAT = 'JPEG'
IMAGE_QUALITY = 95

# PPTX slide configuration
SLIDE_WIDTH_INCHES = 11.25
SLIDE_HEIGHT_INCHES = 14.06

# Text replacements mapping for templates
TEXT_REPLACEMENTS = {
    'tipo1': {
        'title_placeholders': ['Lote de Terreno 300m²', 'Terrenos em Cond. até 566m²'],
        'location_placeholders': ['NOVA ODESSA/SP', 'TERESINA/PI'],
        'price1_placeholders': ['R$ 255.056,73', 'R$ 142.920,39'],
        'price2_placeholders': ['R$ 245.848,12'],
        'date1_placeholders': ['15/06', '02/07'],
        'date2_placeholders': ['30/06'],
        'discount_placeholder': '20% DE DESCONTO!',
    }
}

# Logging configuration
LOG_LEVEL = 'INFO'
