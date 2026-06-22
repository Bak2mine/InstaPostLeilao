# Pipeline Architecture Documentation

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     LEILOARIA PROPERTY PDF PIPELINE                         │
└─────────────────────────────────────────────────────────────────────────────┘

                          ┌──────────────┐
                          │   main.py    │
                          │ (CLI Entry)  │
                          └──────┬───────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
            ┌───────▼────────┐        ┌──────▼──────┐
            │ Parse Arguments │        │ Import/Run │
            │ --limit N       │        │  Pipeline  │
            │ --skip N        │        │            │
            └───────┬────────┘        └──────┬──────┘
                    │                        │
                    └────────────┬───────────┘
                                 │
                         ┌───────▼─────────┐
                         │  pipeline.py    │
                         │ (Orchestrator)  │
                         └───────┬─────────┘
                                 │
                ┌────────────────┼────────────────┐
                │                │                │
        ┌───────▼────────┐ ┌─────▼──────┐ ┌─────▼────────┐
        │  1. SCRAPING   │ │ 2. PROCESS │ │  3. OUTPUT   │
        └───────┬────────┘ └─────┬──────┘ └─────┬────────┘
                │                │              │
      ┌─────────▼────────┐      │              │
      │ PropertyScraper  │      │              │
      │  ├─ Get auctions │      │              │
      │  ├─ Fetch HTML   │      │              │
      │  ├─ Parse data   │      │              │
      │  └─ Extract URLs │      │              │
      └─────────┬────────┘      │              │
                │                │              │
        ┌───────▼──────────────┐ │              │
        │ For Each Property:   │ │              │
        ├─ Get property data   │ │              │
        ├─ Download image      │ │              │
        └─────────┬────────────┘ │              │
                  │               │              │
        ┌─────────▼────────────┐  │              │
        │ ImageProcessor       │  │              │
        │ ├─ Download URL      │  │              │
        │ ├─ Crop sidebars     │  │              │
        │ └─ Convert to RGB    │  │              │
        └─────────┬────────────┘  │              │
                  │               │              │
                  ├───────────────┤              │
                  │               │              │
            ┌─────▼────────┐ ┌───▼──────────┐  │
            │ PPTXHandler  │ │ PDFExporter  │  │
            │              │ │              │  │
            │ ├─ Fill text │ │ ├─ PPTX→PDF  │  │
            │ ├─ Replace   │ │ └─ Append    │  │
            │ │  images    │ │   link page  │  │
            │ └─ Add link  │ └──────┬───────┘  │
            │   page      │        │          │
            └─────┬───────┘        │          │
                  │                 │          │
                  └─────────────────┤──────────┘
                                    │
                          ┌─────────▼────────┐
                          │  output/ folder  │
                          │                  │
                          │ Property.pptx    │
                          │ Property.pdf     │
                          └──────────────────┘
```

## Module Responsibilities

### 1. main.py
**Purpose**: CLI entry point
**Responsibilities**:
- Parse command-line arguments (--limit, --skip, --help)
- Initialize PropertyPDFPipeline
- Execute pipeline.run()
- Return appropriate exit code

**Key Functions**:
- `main()` - Argument parser and pipeline launcher
- `argparse` configuration for CLI

---

### 2. config.py
**Purpose**: Centralized configuration
**Responsibilities**:
- Define all paths (POST_DIR, OUTPUT_DIR, TEMP_DIR)
- Store website URLs and headers
- Specify template locations and types
- Configure image processing parameters
- Set tool paths (LibreOffice)
- Define text replacement mappings

**Key Constants**:
```python
POST_DIR                # Base project directory
TEMPLATES               # Dict of template paths by tipo
LIBREOFFICE_PATH        # PDF export tool location
IMAGE_CROP_PERCENT      # 0.20 = crop 20% from sides
SLIDE_WIDTH_INCHES      # 11.25
SLIDE_HEIGHT_INCHES     # 14.06
```

---

### 3. scraper.py
**Purpose**: Web scraping and data extraction
**Responsibilities**:
- Fetch property listings from search page
- Extract property URLs and titles
- Download individual property pages
- Parse HTML to extract:
  - Property title and description
  - Location (city/state)
  - First auction price and date
  - Second auction price and date (if exists)
  - Discount percentage (if exists)
  - Property image URL
- Determine template type (tipo1-4)

**Key Classes**:
```
PropertyScraper
├─ __init__(session setup)
├─ get_all_auctions(limit=None)
├─ get_property_data(url, title)
├─ extract_first_image_url(html)
└─ get_property_page_html(url)
```

**Data Output**:
```python
{
    'titulo': str,           # Property name
    'cidade': str,           # City
    'estado': str,           # State (2 letters)
    'praca1_valor': str,     # First auction value
    'praca2_valor': str,     # Second auction value
    'praca1_data': str,      # First auction date (DD/MM/YYYY)
    'praca2_data': str,      # Second auction date (DD/MM/YYYY)
    'desconto_pct': float,   # Discount percentage
    'segunda_praca': bool,   # Has second auction
    'tipo': str,             # tipo1/tipo2/tipo3/tipo4
    'auction_url': str,      # Full URL to property
}
```

---

### 4. image_processor.py
**Purpose**: Image download and processing
**Responsibilities**:
- Download images from URLs
- Crop sidebars (remove 20% from each side)
- Convert to RGB format
- Handle image format conversions
- Error handling for download failures

**Key Classes**:
```
ImageProcessor (static methods)
├─ download_image(url)          → PIL.Image
├─ crop_sidebars(image)         → PIL.Image
├─ to_rgb(image)                → PIL.Image
└─ process_for_pptx(image)      → PIL.Image
```

**Processing Pipeline**:
```
Original Image (various formats)
    ↓
Download from URL (JPEG/PNG)
    ↓
Crop 20% from left/right (remove borders)
    ↓
Convert to RGB (ensure JPEG compatibility)
    ↓
Return PIL Image object
```

---

### 5. pptx_handler.py
**Purpose**: PowerPoint template manipulation
**Responsibilities**:
- Load PowerPoint templates
- Replace text placeholders with actual data
- Replace image (sky image, background)
- Add second slide with image and "LINK" text
- Preserve formatting when replacing text
- Handle PPTX ZIP structure manipulation

**Key Classes**:
```
PPTXHandler (static methods)
├─ modify_text(template, data, output)
├─ replace_images(pptx_path, image)
└─ add_link_page(pptx_path, image)
```

**Text Replacements**:
```python
{
    "Lote de Terreno 300m²" → property_data['titulo'],
    "NOVA ODESSA/SP" → f"{city}/{state}",
    "R$ 255.056,73" → property_data['praca1_valor'],
    "R$ 245.848,12" → property_data['praca2_valor'],
    "15/06" → praca1_date_short (MM/DD format),
    "30/06" → praca2_date_short (MM/DD format),
    "20% DE DESCONTO!" → f"{int(discount)}% DE DESCONTO!"
}
```

**Image Operations**:
1. Extract PPTX (ZIP file)
2. Replace `image1.jpeg` (sky placeholder)
3. Re-zip PPTX
4. Add scaled background image using python-pptx
5. Add second slide with background + "LINK" text

---

### 6. pdf_exporter.py
**Purpose**: PDF generation and post-processing
**Responsibilities**:
- Convert PPTX to PDF using LibreOffice
- Append link page from template PDF
- Handle PDF merging
- Error handling and validation

**Key Classes**:
```
PDFExporter (static methods)
├─ pptx_to_pdf(pptx_path, output_dir)
└─ append_link_page(pdf_path)
```

**PDF Generation Process**:
```
PPTX File
    ↓
LibreOffice --headless --convert-to pdf
    ↓
PDF File (single page/slide)
    ↓
Merge with Link Page Template
    ↓
Final PDF (multi-page)
```

---

### 7. pipeline.py
**Purpose**: Main orchestrator
**Responsibilities**:
- Coordinate all modules
- Control data flow
- Validate property data
- Handle errors gracefully
- Generate summary statistics
- Implement retry logic if needed

**Key Classes**:
```
PropertyPDFPipeline
├─ __init__(scraper, output_dir setup)
├─ run(limit=None, skip_count=0)
├─ process_property(auction, property_data)
├─ validate_property_data(data)
└─ sanitize_filename(title)
```

**Main Flow**:
```python
run():
  1. Get all auctions (with limit)
  2. Skip first N properties (with skip)
  3. For each property:
     a. Extract data
     b. Validate data
     c. Process property:
        i.   Modify PPTX (text)
        ii.  Get image
        iii. Replace images
        iv.  Export to PDF
        v.   Append link page
     d. Save to output/
  4. Print summary
```

---

## Data Flow Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                    WEBSITE (leiloariasmart.com.br)           │
└────┬──────────────────────────────────────────────────────┬──┘
     │                                                       │
  (HTTP)                                               (HTTP)
     │                                                       │
     ▼                                                       ▼
┌─────────────────────┐              ┌──────────────────────────────┐
│  Search Page HTML   │              │  Property Page HTML          │
│  (auction listings) │              │ ├─ Title + Location          │
│                     │              │ ├─ Prices & Dates            │
│  Selectors:         │              │ ├─ Discount                  │
│  div.caixa-imoveis  │              │ └─ Images                    │
│  div.info-imovel-2  │              │                              │
└──────────┬──────────┘              └──────────┬───────────────────┘
           │                                    │
           │ scraper.get_all_auctions()         │
           │                                    │ scraper.get_property_data()
           ▼                                    ▼
    ┌──────────────────────────────────────────────────┐
    │ Property List: [                                 │
    │  {title, url},                                   │
    │  ...                                             │
    │ ]                                                │
    └──────────┬───────────────────────────────────────┘
               │
               │ For each property
               ▼
    ┌──────────────────────────────────────────────────┐
    │ Extracted Data:                                  │
    │ {                                                │
    │   titulo, cidade, estado,                        │
    │   praca1_valor, praca2_valor,                    │
    │   praca1_data, praca2_data,                      │
    │   desconto_pct,                                  │
    │   segunda_praca,                                 │
    │   tipo (1-4)                                     │
    │ }                                                │
    └──────────┬───────────────────────────────────────┘
               │
               ├─────────────────────────────────┐
               │                                 │
        ┌──────▼─────────┐           ┌──────────▼────────┐
        │  TEMPLATE.pptx │           │  IMAGE (from URL) │
        │                │           │                   │
        │ ├─ Slide 1     │           │ Process:          │
        │ │  Text areas  │           │ ├─ Download       │
        │ │  Image area  │           │ ├─ Crop 20%       │
        │ │              │           │ └─ RGB convert    │
        │ └─ Slide 2     │           └──────────┬────────┘
        │    Link area   │                      │
        └──────┬─────────┘                      │
               │                                │
               └────────────┬───────────────────┘
                            │
                    ┌───────▼───────────┐
                    │  PPTXHandler      │
                    │  Modify:          │
                    │  ├─ Replace text  │
                    │  ├─ Replace image │
                    │  └─ Add slide 2   │
                    └───────┬───────────┘
                            │
                         ┌──▼─────────────────┐
                         │ MODIFIED.pptx      │
                         └──┬────────────────┘
                            │
                    ┌───────▼──────────┐
                    │ PDFExporter      │
                    │ ├─ PPTX → PDF    │
                    │ └─ Add link page │
                    └───────┬──────────┘
                            │
                    ┌───────▼──────────┐
                    │ output/          │
                    │ Property.pdf     │
                    └──────────────────┘
```

## Module Dependencies

```
main.py
   └─ pipeline.py
      ├─ config.py
      ├─ scraper.py
      │  └─ config.py
      ├─ image_processor.py
      │  └─ config.py
      ├─ pptx_handler.py
      │  └─ config.py
      └─ pdf_exporter.py
         └─ config.py

test_pipeline.py
   └─ pipeline.py
      ├─ config.py
      ├─ scraper.py
      ├─ image_processor.py
      ├─ pptx_handler.py
      └─ pdf_exporter.py
```

## Error Handling Strategy

```
┌────────────────────────────────────────────────┐
│           PIPELINE ERROR HANDLING               │
└────────────────────────────────────────────────┘

Property Processing Error:
    │
    ├─ Data extraction fails
    │  └─ Log warning → Skip property → Continue
    │
    ├─ Image download fails
    │  └─ Log warning → Continue without image
    │
    ├─ Template not found
    │  └─ Log error → Skip property → Continue
    │
    ├─ PPTX modification fails
    │  └─ Log error → Skip property → Continue
    │
    ├─ PDF export fails
    │  └─ Log warning → Keep PPTX → Continue
    │
    └─ Link page append fails
       └─ Log warning → Keep single-page PDF → Continue

Final Result:
    ✓ Partial success (some properties succeeded)
    ✓ Full success (all properties succeeded)
    ✗ Full failure (no properties succeeded)

Summary Statistics:
    - Total scraped
    - Successfully generated
    - Failed count
    - Success rate
```

## Performance Characteristics

```
╔════════════════════════════════════════════════════════════╗
║              PERFORMANCE PROFILE                           ║
╚════════════════════════════════════════════════════════════╝

Per-Property Timeline:
  1. Fetch property page:    ~1-2 seconds
  2. Parse data:            ~0.1 seconds
  3. Download image:        ~2-5 seconds
  4. Process image:         ~0.5 seconds
  5. Modify PPTX:           ~1-2 seconds
  6. Export to PDF:         ~5-10 seconds
  7. Append link page:      ~0.5 seconds
  ─────────────────────────────────────
  Total per property:       ~10-25 seconds

For 50 properties:
  Sequential time:         500-1250 seconds (~8-20 minutes)
  With rate limiting (0.5s): +25 seconds
  Total:                   ~8-21 minutes

Memory Usage:
  - Images: Streamed (PIL loads into memory one at a time)
  - PPTX: Loaded as needed
  - Data: Dict of ~30 bytes per property
  Peak memory: ~10-50 MB

Network Usage:
  - Per property: ~2-10 MB (image download)
  - 50 properties: ~100-500 MB total
```

---

## Extension Points

### Adding a New Module
1. Create new file following naming convention
2. Import in pipeline.py
3. Update config.py if new settings needed
4. Add error handling in pipeline.py

### Modifying Template Selection
File: `scraper.py` → `get_property_data()` → `tipo` assignment

### Adding New Text Replacements
File: `pptx_handler.py` → `modify_text()` → `replacements` dict

### Changing Image Processing
File: `image_processor.py` → Add new method → Call from pipeline.py

### Supporting Additional Formats
File: `pdf_exporter.py` → Add new export method

---

This modular architecture enables easy testing, debugging, maintenance, and future enhancements.
