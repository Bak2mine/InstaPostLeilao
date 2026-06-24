"""
Configuration and constants for the Leiloaria PDF/PPTX generation pipeline
"""

from pathlib import Path

# Base paths
POST_DIR = Path(r"C:\Users\andre\Desktop\Leiloaria\Post")
IMOVEIS_DIR = POST_DIR / "imoveis"
OUTPUT_DIR = POST_DIR / "output"
TEMP_DIR = POST_DIR / ".temp"

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
