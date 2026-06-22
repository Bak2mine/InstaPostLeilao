# Leiloaria Property PDF Generator - Project Documentation

## Project Overview

Automated end-to-end pipeline for generating professional property presentation PDFs from leiloariasmart.com.br auction listings. The system scrapes property data, downloads images, fills PowerPoint templates dynamically, and exports to PDF with link pages.

## File Structure

### Core Pipeline
- **`main.py`** - Entry point with CLI argument parsing
- **`pipeline.py`** - Main orchestrator coordinating all modules
- **`config.py`** - Centralized configuration and constants

### Functional Modules
- **`scraper.py`** - Web scraping and property data extraction
- **`image_processor.py`** - Image download, crop, and format conversion
- **`pptx_handler.py`** - PowerPoint template text/image manipulation
- **`pdf_exporter.py`** - PDF generation and post-processing

### Testing & Documentation
- **`test_pipeline.py`** - Single property test to validate setup
- **`PIPELINE_README.md`** - Full user documentation
- **`CLAUDE.md`** - This file (project documentation)

### Templates
- **`1 e 2 praça.pptx`** - Template for 2 auctions + discount
- **`2praca.pptx`** - Template for 1 auction + discount
- **`1prac.pptx`** - Template for 2 auctions, no discount
- **`1pracD.pptx`** - Template for 1 auction, no discount

### Directories
- **`output/`** - Generated PPTX and PDF files
- **`.temp/`** - Temporary files during processing
- **`imoveis/`** - Legacy generated files (deprecated, replaced by output/)

## Architecture Decisions

### Modular Design
Each concern is separated into its own module to enable:
- Easy testing of individual components
- Clear responsibility boundaries
- Reusability and extensibility
- Simple dependency management

### Template Auto-Selection
Properties are categorized into 4 types based on:
1. Number of auctions (primeira/segunda praça)
2. Presence of discount percentage

This enables single command to process all properties with correct template.

### Image Processing Pipeline
Images go through standardized flow:
1. Download from URL
2. Crop 20% sidebars (removes blue/cyan borders from website)
3. Convert to RGB (JPEG compatibility)
4. Replace template sky image
5. Add as scaled background to slide

### Error Tolerance
Pipeline uses "skip on error" approach:
- Missing data → skip property, continue with next
- Failed image download → continue without image
- LibreOffice unavailable → skip PDF conversion
- Validation errors → detailed logging, resume ready

This ensures partial failures don't halt the entire run.

## Key Classes

### PropertyScraper
- `get_all_auctions()` - Fetch all listings from search page
- `get_property_data()` - Extract data from individual property page
- `extract_first_image_url()` - Parse image URL from HTML
- `get_property_page_html()` - Fetch raw HTML for parsing

### ImageProcessor
- `download_image()` - Download and return PIL Image
- `crop_sidebars()` - Remove 20% from left/right edges
- `to_rgb()` - Convert to RGB mode
- `process_for_pptx()` - Full processing pipeline

### PPTXHandler
- `modify_text()` - Replace placeholder text in slides
- `replace_images()` - Replace sky image and add background
- `add_link_page()` - Add second slide with image and "LINK"

### PDFExporter
- `pptx_to_pdf()` - Convert PPTX to PDF via LibreOffice
- `append_link_page()` - Merge template link page to PDF

### PropertyPDFPipeline
- `run()` - Main pipeline orchestrator
- `process_property()` - Process single property through full flow
- `validate_property_data()` - Verify required fields
- `sanitize_filename()` - Clean filenames for filesystem

## Data Flow

```
1. Scrape Search Page
   ↓
2. Get Auction URLs & Titles
   ↓
3. For Each Property:
   ├─ Fetch Property Page HTML
   ├─ Extract: title, location, prices, dates, discount
   ├─ Download First Image
   ├─ Determine Template Type (tipo1-4)
   ├─ Modify PPTX:
   │  ├─ Replace text placeholders
   │  ├─ Replace/add images
   │  └─ Add link page
   ├─ Export PPTX → PDF
   ├─ Append Link Page to PDF
   └─ Save to output/
```

## Configuration Guide

Edit `config.py` to customize:

```python
# Paths
POST_DIR = Path(r"C:\Users\andre\Desktop\Leiloaria\Post")
OUTPUT_DIR = POST_DIR / "output"
IMOVEIS_DIR = POST_DIR / "imoveis"  # Legacy

# Website
BASE_URL = "https://leiloariasmart.com.br"
MAIN_URL = "https://leiloariasmart.com.br/busca"
TIMEOUT = 30

# Image
IMAGE_CROP_PERCENT = 0.20  # Crop 20% from edges
IMAGE_QUALITY = 95  # JPEG quality 1-100

# Slide
SLIDE_WIDTH_INCHES = 11.25
SLIDE_HEIGHT_INCHES = 14.06

# Tools
LIBREOFFICE_PATH = r"C:\Program Files\LibreOffice\program\soffice.exe"
LINK_PDF = POST_DIR / "Posts IG.pdf"  # Template for link page
```

## Template System

### Naming Convention
Templates follow pattern: `{count_praca}{discount_suffix}.pptx`

### Auto-Selection Logic
```
2nd praça? + Discount? → Template
────────────────────────────────
Yes       + Yes        → tipo1
Yes       + No         → tipo3
No        + Yes        → tipo2
No        + No         → tipo4
```

### Text Replacement
Each template has placeholders replaced with actual data:
- "Lote de Terreno 300m²" → Actual property title
- "NOVA ODESSA/SP" → Actual city/state
- "R$ 255.056,73" → Actual primeira praça price
- "R$ 245.848,12" → Actual segunda praça price
- "15/06" → Actual auction date (MM/DD format)
- "20% DE DESCONTO!" → Actual discount % or preserved

## Usage Patterns

### Process All Properties
```bash
python main.py
```

### Test Single Property
```bash
python test_pipeline.py
```

### Batch Processing with Limit
```bash
python main.py --limit 50
```

### Resume from Checkpoint
```bash
# If previous run stopped at property 125
python main.py --skip 125
```

### Sample Limited Run
```bash
# Process 20 properties starting from index 50
python main.py --skip 50 --limit 20
```

## Maintenance Notes

### When Website Changes
If scraping fails, check:
1. HTML selectors in `scraper.py` (`class_='caixa-imoveis'`, etc.)
2. Regex patterns for price/date extraction
3. Image URL regex pattern

### When Templates Change
1. Verify placeholder text still exists
2. Check text_frame order matches expectations
3. Validate image paths (`image1.jpeg` for sky, etc.)

### When LibreOffice Fails
1. Verify installation: `C:\Program Files\LibreOffice\program\soffice.exe`
2. Try manual conversion: `soffice --headless --convert-to pdf file.pptx`
3. Check system temp directory has write permissions

## Known Limitations

1. **Single image only** - Uses first image from property page only
2. **Template-specific** - Placeholders must match exactly
3. **No batch email** - PDFs generated but not distributed
4. **LibreOffice required** - No alternative PDF generation methods
5. **Rate limiting** - 0.5s delay between properties (conservative)
6. **Brazilian formatting** - Dates/prices use Brazilian format only

## Future Enhancement Ideas

- [ ] CLI progress bar with tqdm
- [ ] Database logging (SQLite)
- [ ] Image gallery selection (not just first image)
- [ ] Custom template mapping per property type
- [ ] Batch ZIP export
- [ ] Email delivery integration
- [ ] Slack/Discord notifications
- [ ] Docker containerization
- [ ] Schedule via cron/Task Scheduler
- [ ] Web dashboard for monitoring

## Debugging Tips

### Enable Verbose Logging
Add to `pipeline.py`:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Test Scraping Only
```python
from scraper import PropertyScraper
scraper = PropertyScraper()
auctions = scraper.get_all_auctions(limit=1)
data = scraper.get_property_data(auctions[0]['url'], auctions[0]['title'])
print(data)
```

### Test Image Processing
```python
from image_processor import ImageProcessor
img = ImageProcessor.download_image("URL_HERE")
img_processed = ImageProcessor.process_for_pptx(img)
img_processed.show()
```

### Test PPTX Modification
```python
from pptx_handler import PPTXHandler
PPTXHandler.modify_text(
    Path("template.pptx"),
    {'titulo': 'Test', 'cidade': 'Test', ...},
    Path("output.pptx")
)
```

## Contact & Support

For issues or questions about the pipeline:
1. Check `PIPELINE_README.md` for user documentation
2. Review error messages in console output
3. Enable verbose logging for debugging
4. Check `config.py` settings match your environment
