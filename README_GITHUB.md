# InstaPostLeilao - Property PDF Generator

Automated pipeline for generating professional property presentation PDFs from leiloariasmart.com.br auction listings, optimized for Instagram posts.

## Features

- **Web Scraping**: Automatically extracts property data (title, location, prices, auction dates, discounts)
- **Image Processing**: Downloads, crops, and converts property images to optimal format
- **Template Filling**: Dynamically replaces text and images in PowerPoint templates
- **PDF Export**: Generates professional PDFs via LibreOffice
- **Batch Processing**: Handle multiple properties automatically with error tolerance
- **Template Auto-Selection**: Chooses correct template based on property type

## Quick Start

### Requirements
- Python 3.8+
- LibreOffice (for PDF conversion)
- Internet connection

### Installation

```bash
pip install -r requirements.txt
```

### Usage

**Process single property (test):**
```bash
python test_pipeline.py
```

**Process all properties:**
```bash
python main.py
```

**Process with limit:**
```bash
python main.py --limit 10
```

**Resume from checkpoint:**
```bash
python main.py --skip 25
```

## Project Structure

```
├── main.py                 # CLI entry point
├── pipeline.py             # Main orchestrator
├── config.py               # Configuration and constants
├── scraper.py              # Web scraping
├── image_processor.py       # Image handling
├── pptx_handler.py          # PowerPoint manipulation
├── pdf_exporter.py          # PDF generation
├── test_pipeline.py         # Single property test
├── requirements.txt         # Python dependencies
├── 1pracD.pptx            # Templates (4 types)
├── 1prac.pptx
├── 2praca.pptx
└── 1 e 2 praça.pptx
```

## Architecture

### Modular Design
Each concern is separated into its own module:
- **Scraper**: Handles HTML parsing and data extraction
- **ImageProcessor**: Downloads and processes images
- **PPTXHandler**: Template text and image replacement
- **PDFExporter**: Format conversion
- **Pipeline**: Orchestrates the complete workflow

### Template System
Properties are categorized into 4 template types based on:
- Number of auctions (primeira/segunda praça)
- Presence of discount percentage

Auto-selection ensures correct template for each property.

### Image Processing
1. Download from website
2. Crop 20% sidebars (removes blue/cyan borders)
3. Convert to RGB (JPEG compatible)
4. Embed in template
5. Add as full-slide background

## Configuration

Edit `config.py` to customize:
- Output directory
- Website URLs
- Image quality and cropping
- LibreOffice path
- Slide dimensions

## Instagram Post Optimization

Generated PDFs can be directly exported to Instagram:
1. Each PDF has two pages: property details + link page
2. Image sizing optimized for 1080x1350 (Instagram portrait)
3. Text preserved for readability
4. For final crops/adjustments, use Instagram's built-in tools

## Error Handling

Pipeline uses graceful degradation:
- Missing data → Skip property, continue with next
- Failed image download → Continue without image
- LibreOffice unavailable → Skip PDF conversion
- Validation errors → Log and resume

## Known Limitations

- Single image per property (first image from listing)
- Template placeholders must match exactly
- Requires LibreOffice for PDF export
- Brazilian date/price formatting

## Troubleshooting

**PDF export fails:**
- Verify LibreOffice installation: `C:\Program Files\LibreOffice\program\soffice.exe`
- Check system temp directory has write permissions

**Images not showing:**
- Verify image URL is accessible
- Check JPEG quality setting in config

**Text not replacing:**
- Verify placeholder text matches template exactly
- Check property data extraction in scraper.py

## Future Enhancements

- [ ] Image gallery selection (multi-image support)
- [ ] Custom template mapping per property type
- [ ] Batch ZIP export
- [ ] Email delivery integration
- [ ] Web dashboard
- [ ] Docker containerization

## License

Created for leiloariasmart.com.br automation

## Support

For issues or questions, check:
1. Console output for error messages
2. `CLAUDE.md` for detailed documentation
3. `PIPELINE_README.md` for user guide
