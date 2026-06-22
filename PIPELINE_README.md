# Leiloaria Property PDF Generator Pipeline

Automated end-to-end pipeline for generating property presentation PDFs from leiloariasmart.com.br listings.

## Pipeline Flow

```
Scrape Listings → Extract Property Data → Fetch Images → Select Template → 
Fill PPTX → Replace Images → Export PDF → Append Link Page → Complete PDF
```

## Architecture

### Modular Structure

- **`config.py`** - Centralized configuration and constants
- **`scraper.py`** - Web scraping and data extraction from property pages
- **`image_processor.py`** - Image download and processing (crop, resize, format)
- **`pptx_handler.py`** - PowerPoint template manipulation (text & image replacement)
- **`pdf_exporter.py`** - PDF generation and post-processing
- **`pipeline.py`** - Main orchestrator that coordinates all modules
- **`main.py`** - Command-line entry point

### Templates

Four PowerPoint templates for different property types:

| Template | Filename | Use Case |
|----------|----------|----------|
| **tipo1** | `1 e 2 praça.pptx` | Two auctions + discount |
| **tipo2** | `2praca.pptx` | Single auction + discount |
| **tipo3** | `1prac.pptx` | Two auctions, no discount |
| **tipo4** | `1pracD.pptx` | Single auction, no discount |

Template selection is automatic based on property data.

## Usage

### Basic Usage

```bash
# Process all properties from the website
python main.py

# Process first 10 properties
python main.py --limit 10

# Process properties starting from index 50
python main.py --skip 50

# Process 20 properties starting from index 50
python main.py --limit 20 --skip 50
```

### Command-Line Options

```
--limit, -l     Maximum number of properties to process (default: all)
--skip, -s      Number of properties to skip, useful for resuming (default: 0)
--help, -h      Show help message
```

## Features

### Automatic Template Selection

Properties are categorized by auction type and discount availability:
- **tipo1**: Has both primeira and segunda praça + discount
- **tipo2**: Has only primeira praça + discount  
- **tipo3**: Has both praças + no discount
- **tipo4**: Has only primeira praça + no discount

### Image Processing

1. **Download** - Downloads first property image from listing page
2. **Crop** - Removes 20% sidebars (blue/cyan borders)
3. **Convert** - Converts to RGB JPEG for compatibility
4. **Replace** - Replaces template sky image with property photo
5. **Background** - Adds scaled background image to slide 1
6. **Link Page** - Adds second slide with image and "LINK" text

### Data Extraction

Automatically extracts from property pages:
- Property title and description
- Location (cidade/estado)
- First auction value and date
- Second auction value and date (if exists)
- Discount percentage (if exists)
- Property image URL

### Text Replacement

Dynamically replaces template placeholders:
- Title (e.g., "Lote de Terreno 300m²" → actual property name)
- Location (e.g., "NOVA ODESSA/SP" → actual location)
- Prices (both primeira and segunda praça)
- Dates (formatted as MM/DD)
- Discount percentage

### PDF Generation

1. Exports PPTX to PDF using LibreOffice
2. Appends link page from template PDF
3. Final output is multi-page PDF ready for distribution

## Output

Generated files are saved to `output/` directory with structure:
```
output/
├── Casa 147m².pptx
├── Casa 147m².pdf
├── Apartamento 102m².pptx
├── Apartamento 102m².pdf
└── ...
```

## Configuration

Edit `config.py` to customize:

```python
# Output directories
POST_DIR = Path(r"C:\Users\andre\Desktop\Leiloaria\Post")
OUTPUT_DIR = POST_DIR / "output"

# LibreOffice path (for PDF export)
LIBREOFFICE_PATH = r"C:\Program Files\LibreOffice\program\soffice.exe"

# Image processing
IMAGE_CROP_PERCENT = 0.20  # Crop 20% from each side
IMAGE_QUALITY = 95  # JPEG quality

# Slide dimensions
SLIDE_WIDTH_INCHES = 11.25
SLIDE_HEIGHT_INCHES = 14.06
```

## Error Handling

The pipeline handles common errors gracefully:

- **Missing template**: Logs error and skips property
- **Failed scraping**: Skips property or continues without image
- **LibreOffice unavailable**: Falls back or skips PDF export
- **Invalid data**: Validates required fields before processing
- **Network errors**: Retries with timeout protection

## Performance

- **Rate limiting**: 0.5s delay between properties to avoid rate limiting
- **Timeout protection**: 30s timeout on web requests, 60s on PDF export
- **Resumable**: Use `--skip` parameter to resume from any point
- **Memory efficient**: Streams images, doesn't hold large data in memory

## Troubleshooting

### LibreOffice errors
- Ensure LibreOffice is installed at: `C:\Program Files\LibreOffice\program\soffice.exe`
- Run in headless mode works on Windows, but may require specific versions

### Image not showing
- Check that first image on property page is accessible
- Verify image URL format matches regex in `scraper.py`

### Template placeholders not replaced
- Verify exact placeholder text in template matches `pptx_handler.py`
- Check `config.py` TEMPLATES dictionary points to correct files

### Data extraction issues
- Verify website HTML structure hasn't changed
- Update regex patterns in `scraper.py` if structure changed

## Future Improvements

- [ ] Add CLI progress bar
- [ ] Support for custom template selection
- [ ] Batch PDF merge option
- [ ] Email delivery integration
- [ ] Database logging for tracking
- [ ] Webhook notifications on completion
- [ ] Docker containerization for portability
