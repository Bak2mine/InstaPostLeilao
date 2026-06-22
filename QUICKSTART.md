# Quick Start Guide

## What Changed

You now have a **fully automated, modular pipeline** that replaces the old mixed scripts. Instead of multiple fragmented `pptx_generator_final.py`, `gerar_imoveis_final.py`, etc., everything is now:

- **Unified**: Single entry point (`main.py`)
- **Automated**: Scrape → Extract → Fill → Export in one command
- **Reliable**: Error handling, validation, rate limiting
- **Modular**: Clean separation of concerns
- **Documented**: Comprehensive documentation included

## What You Need

### Prerequisites
1. **Python 3.7+** with these packages:
   ```bash
   pip install requests beautifulsoup4 pillow python-pptx pypdf lxml
   ```

2. **LibreOffice** installed at:
   ```
   C:\Program Files\LibreOffice\program\soffice.exe
   ```

3. **PowerPoint Templates** in Post folder:
   - `1 e 2 praça.pptx` ✓ (should already exist)
   - `2praca.pptx` ✓
   - `1prac.pptx` ✓
   - `1pracD.pptx` ✓

4. **Link PDF Template**:
   - `Posts IG.pdf` ✓ (should already exist)

## Quick Start (3 steps)

### Step 1: Install Dependencies
```bash
pip install requests beautifulsoup4 pillow python-pptx pypdf lxml
```

### Step 2: Test with One Property
```bash
cd C:\Users\andre\Desktop\Leiloaria\Post
python test_pipeline.py
```

Expected output:
- Creates `output/` directory
- Generates 1 PPTX and 1 PDF
- Shows success/failure message

### Step 3: Run Full Pipeline
```bash
# All properties
python main.py

# First 10 properties
python main.py --limit 10

# Resume from property 50
python main.py --skip 50
```

## File Organization

### New Pipeline Files
```
Post/
├── main.py                 ← Run this
├── pipeline.py             ← Orchestrator
├── config.py               ← Settings
├── scraper.py              ← Web scraping
├── image_processor.py       ← Image handling
├── pptx_handler.py         ← Template modification
├── pdf_exporter.py         ← PDF generation
├── test_pipeline.py        ← Test script
├── CLAUDE.md               ← Developer docs
├── PIPELINE_README.md      ← Full documentation
└── QUICKSTART.md           ← This file
```

### Generated Files
```
Post/
├── output/                 ← All generated PDFs & PPTXs
│   ├── Casa 147m².pptx
│   ├── Casa 147m².pdf
│   ├── Apartamento 102m².pptx
│   └── Apartamento 102m².pdf
├── .temp/                  ← Temporary working files (auto-cleanup)
└── imoveis/                ← Old generated files (kept for reference)
```

### Templates (Keep As-Is)
```
Post/
├── 1 e 2 praça.pptx        ← 2 auctions + discount
├── 2praca.pptx             ← 1 auction + discount
├── 1prac.pptx              ← 2 auctions, no discount
├── 1pracD.pptx             ← 1 auction, no discount
└── Posts IG.pdf            ← Link page template
```

## Common Commands

```bash
# Test setup (generates 1 PDF)
python test_pipeline.py

# Generate all properties
python main.py

# Generate first 10
python main.py -l 10

# Generate 20 properties starting from #50
python main.py -s 50 -l 20

# Resume from where you left off
python main.py -s 150
```

## What Happens Step-by-Step

For **each property**, the pipeline:

1. **Scrapes** property listing page
   - Gets: title, location, prices, dates, discount

2. **Determines template type** automatically
   - tipo1: 2 auctions + discount
   - tipo2: 1 auction + discount  
   - tipo3: 2 auctions, no discount
   - tipo4: 1 auction, no discount

3. **Downloads image**
   - Fetches first image from property page
   - Crops 20% from sides (removes borders)
   - Converts to RGB JPEG

4. **Fills PowerPoint template**
   - Replaces text: title → actual property name
   - Replaces location: city/state
   - Replaces prices: first and second auction values
   - Replaces dates: auction dates
   - Replaces image: sky image + background

5. **Exports to PDF**
   - Converts PPTX → PDF using LibreOffice
   - Appends link page from template

6. **Saves output**
   - PPTX: `output/Property Name.pptx`
   - PDF: `output/Property Name.pdf`

## Troubleshooting

### Script won't run: "ModuleNotFoundError"
```bash
pip install requests beautifulsoup4 pillow python-pptx pypdf lxml
```

### LibreOffice error
Check it's installed:
```bash
"C:\Program Files\LibreOffice\program\soffice.exe" --version
```

### No output files
- Check `output/` directory was created
- Check console for error messages
- Run `python test_pipeline.py` to test single property

### PDF is blank
- Verify PPTX was created (check `output/` for .pptx file)
- Verify template files exist in Post folder
- Check LibreOffice conversion errors in console

### Images not showing in PDF
- Website might have changed image URLs
- Check internet connection
- Run with `--limit 1` to test single property

## Configuration

All settings are in `config.py`. Most don't need changing, but you can:

```python
# Change output location
OUTPUT_DIR = Path(r"C:\Different\Location\output")

# Process fewer properties at once
TIMEOUT = 60  # seconds to wait for web requests

# Crop different amount from sides
IMAGE_CROP_PERCENT = 0.15  # 15% instead of 20%
```

## Next Steps

1. ✅ Run `python test_pipeline.py` to test
2. ✅ Run `python main.py --limit 10` to test with 10 properties
3. ✅ Run `python main.py` for all properties
4. ✅ Check `output/` folder for generated PDFs
5. ✅ Share PDFs or proceed to next step

## Need Help?

- **User documentation**: Read `PIPELINE_README.md`
- **Developer docs**: Read `CLAUDE.md`
- **Testing**: Run `python test_pipeline.py`
- **Debug**: Add `--limit 1` to test single property and see detailed errors

## What's Different From Before

| Old Approach | New Pipeline |
|---|---|
| Multiple scripts (gerar_imoveis_final.py, pptx_generator_final.py) | Single entry point (main.py) |
| PNG-based templates | PowerPoint templates with automatic selection |
| Manual template selection | Automatic tipo1-tipo4 selection |
| No error recovery | Graceful error handling with skip-on-error |
| Mixed code in one file | Modular design (7 focused modules) |
| Hard-coded paths | Centralized config.py |
| No CLI arguments | CLI with --limit and --skip options |
| Deprecated imoveis/ output | New output/ directory |

## Summary

**Before**: Multiple fragmented scripts, unclear flow, manual steps
**After**: Unified automated pipeline, clear modular code, single command to process everything

Just run: `python main.py`

Done! 🎉
