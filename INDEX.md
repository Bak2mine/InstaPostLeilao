# Leiloaria Pipeline - Complete File Index

A comprehensive index of all files in the automated pipeline system.

---

## 🚀 Getting Started

**First time here?**
1. Start with: **[README.md](README.md)** - Overview and quick reference
2. Then read: **[QUICKSTART.md](QUICKSTART.md)** - 5-minute setup guide
3. Run: `python test_pipeline.py` - Verify your setup works

---

## 📋 Complete File Listing

### Production Code (7 modules)

| File | Purpose | Lines | Details |
|------|---------|-------|---------|
| **main.py** | CLI entry point | 42 | Command-line interface with --limit and --skip arguments |
| **pipeline.py** | Main orchestrator | 165 | Coordinates all modules, controls workflow |
| **config.py** | Configuration hub | 61 | All settings, paths, constants in one place |
| **scraper.py** | Web scraping | 157 | Fetch listings, extract property data, determine template type |
| **image_processor.py** | Image handling | 47 | Download, crop, convert images |
| **pptx_handler.py** | PPTX manipulation | 194 | Modify text, replace images, add slides |
| **pdf_exporter.py** | PDF export | 73 | Convert to PDF, append link page |

### Testing & Dependencies

| File | Purpose | Size |
|------|---------|------|
| **test_pipeline.py** | Test script | 1 KB |
| **requirements.txt** | Python dependencies | 0.1 KB |

### Documentation

| File | Audience | Purpose | Size |
|------|----------|---------|------|
| **README.md** | Everyone | Master overview & index | 9.6 KB |
| **QUICKSTART.md** | New users | 5-minute setup guide | 6.4 KB |
| **PIPELINE_README.md** | Users | Complete reference guide | 5.4 KB |
| **CLAUDE.md** | Developers | Developer documentation | 8.2 KB |
| **ARCHITECTURE.md** | Developers | System architecture & design | 20.3 KB |
| **MIGRATION_SUMMARY.md** | Migrating users | What changed from old scripts | 8.4 KB |
| **DELIVERABLES.txt** | Project managers | Complete deliverables checklist | 14.5 KB |
| **INDEX.md** | Everyone | This file - file index | ~5 KB |

---

## 🎯 Choosing Your Starting Point

### I'm new - where do I start?
→ **[README.md](README.md)** then **[QUICKSTART.md](QUICKSTART.md)**

### I want to run it immediately
→ **[QUICKSTART.md](QUICKSTART.md)** - 5 minute guide

### I need complete documentation
→ **[PIPELINE_README.md](PIPELINE_README.md)** - Full user guide

### I want to understand the architecture
→ **[CLAUDE.md](CLAUDE.md)** - Developer guide + **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design

### I'm migrating from old scripts
→ **[MIGRATION_SUMMARY.md](MIGRATION_SUMMARY.md)** - Migration guide

### I need to troubleshoot an issue
→ **[PIPELINE_README.md](PIPELINE_README.md)** - Troubleshooting section

### I'm managing this project
→ **[DELIVERABLES.txt](DELIVERABLES.txt)** - Complete checklist

---

## 📊 File Statistics

```
Total Files:              17 files
Total Size:              ~110 KB

Code:                     739 lines (7 modules)
Documentation:         1,066+ lines (6 guides)
Tests:                    29 lines (1 test)
Configuration:             6 lines (1 config)
─────────────────────────────────
Total:                  1,840 lines
```

---

## 🔄 File Dependencies

```
main.py
  └─ pipeline.py
      ├─ config.py
      ├─ scraper.py (uses config.py)
      ├─ image_processor.py (uses config.py)
      ├─ pptx_handler.py (uses config.py)
      └─ pdf_exporter.py (uses config.py)

test_pipeline.py
  └─ pipeline.py (and all above)

requirements.txt
  (no dependencies, just lists packages)
```

---

## 🎓 Documentation Hierarchy

```
Level 1: Overview
  └─ README.md - Start here, overview of everything

Level 2: Quick Start
  └─ QUICKSTART.md - Get running in 5 minutes

Level 3: User Documentation
  └─ PIPELINE_README.md - Complete reference for users

Level 4: Developer Documentation
  ├─ CLAUDE.md - Developer guide & best practices
  └─ ARCHITECTURE.md - System design & architecture

Level 5: Migration & Delivery
  ├─ MIGRATION_SUMMARY.md - For users migrating from old scripts
  └─ DELIVERABLES.txt - Project completion checklist
```

---

## 🚀 Usage Patterns

### Setup & Test
```bash
cd C:\Users\andre\Desktop\Leiloaria\Post
pip install -r requirements.txt
python test_pipeline.py
```

### Run Pipeline
```bash
# All properties
python main.py

# First 10
python main.py --limit 10

# Resume from property 50
python main.py --skip 50

# Help
python main.py --help
```

---

## ✨ What Each File Does

### Production Code

**main.py**
- Entry point for CLI
- Parses --limit and --skip arguments
- Initializes and runs PropertyPDFPipeline
- Returns appropriate exit codes

**pipeline.py**
- Main orchestrator class: PropertyPDFPipeline
- run() - Main pipeline execution
- process_property() - Process single property
- validate_property_data() - Data validation
- sanitize_filename() - Filename cleaning

**config.py**
- All paths (POST_DIR, OUTPUT_DIR, TEMP_DIR)
- Website settings (BASE_URL, HEADERS, TIMEOUT)
- Template definitions (tipo1-4)
- LibreOffice path
- Image processing settings
- Text replacement mappings

**scraper.py**
- PropertyScraper class
- Web scraping with requests + BeautifulSoup
- Extract auction listings
- Extract property data (title, location, prices, dates)
- Extract image URLs
- Automatic template type determination (tipo1-4)

**image_processor.py**
- ImageProcessor class (static methods)
- Download images from URLs
- Crop sidebars (remove 20% borders)
- Convert to RGB for JPEG compatibility

**pptx_handler.py**
- PPTXHandler class (static methods)
- Modify PPTX text (replace placeholders)
- Replace images in PPTX (sky image)
- Add background images
- Add second slide with LINK text
- Handle ZIP manipulation for PPTX

**pdf_exporter.py**
- PDFExporter class (static methods)
- Convert PPTX to PDF via LibreOffice
- Append link page from template PDF
- Error handling for PDF operations

### Testing

**test_pipeline.py**
- Test script for single property
- Validates complete end-to-end pipeline
- Useful for initial setup verification

### Configuration

**requirements.txt**
- Python package dependencies
- Install with: `pip install -r requirements.txt`

### Documentation

**README.md**
- Master overview and index
- Quick links to guides
- Summary of features
- Usage examples
- Troubleshooting intro

**QUICKSTART.md**
- 5-minute setup guide
- Installation steps
- Basic usage
- File organization
- Common commands

**PIPELINE_README.md**
- Complete user documentation
- Features explained in detail
- Configuration guide
- Complete troubleshooting section
- Performance information

**CLAUDE.md**
- Developer documentation
- Project structure
- Architecture decisions
- Key classes explanation
- Data flow
- Configuration guide
- Maintenance notes
- Debugging tips

**ARCHITECTURE.md**
- Detailed system architecture
- Module responsibilities
- Data flow diagrams
- Module dependencies
- Error handling strategy
- Performance characteristics
- Extension points

**MIGRATION_SUMMARY.md**
- Comparison of old vs new
- Architecture improvements
- Benefits summary
- Migration checklist
- Common questions

**DELIVERABLES.txt**
- Complete deliverables checklist
- Project summary
- Statistics
- Features list
- Quality metrics

**INDEX.md**
- This file
- File index and navigation
- Getting started guide
- File statistics

---

## 🎯 Key Information at a Glance

### What This Does
Automatically scrapes properties from leiloariasmart.com.br, fills PowerPoint templates with property data, downloads images, and exports professional PDFs.

### How to Use
```bash
python main.py                    # All properties
python main.py --limit 10         # First 10
python main.py --skip 50          # Resume from 50
```

### Output Location
`Post/output/` - Contains all generated PPTX and PDF files

### System Requirements
- Python 3.7+
- LibreOffice
- Windows 10/11

### Templates
- 1 e 2 praça.pptx (2 auctions + discount)
- 2praca.pptx (1 auction + discount)
- 1prac.pptx (2 auctions, no discount)
- 1pracD.pptx (1 auction, no discount)

---

## 📈 Statistics

| Metric | Value |
|--------|-------|
| Total files | 17 |
| Python modules | 7 |
| Test files | 1 |
| Documentation files | 6 |
| Configuration files | 1 |
| Total lines | 1,840+ |
| Production code | 739 lines |
| Documentation | 1,066+ lines |
| Total size | ~110 KB |
| Setup time | ~5 minutes |
| Test run time | ~15-30 seconds |

---

## ✅ Quality Metrics

- **Code Quality**: Production-ready with comprehensive error handling
- **Documentation**: 1,000+ lines across 6 guides
- **Testing**: Test script included for validation
- **Modularity**: 7 focused, single-responsibility modules
- **Error Handling**: Skip-on-error for resilience
- **Configuration**: Centralized in single file
- **Automation**: Full end-to-end automation

---

## 🔗 Quick Links

**To Get Started**
- [README.md](README.md) - Overview
- [QUICKSTART.md](QUICKSTART.md) - 5-minute setup

**For Users**
- [PIPELINE_README.md](PIPELINE_README.md) - Complete guide
- [Troubleshooting](PIPELINE_README.md#troubleshooting) - FAQ & issues

**For Developers**
- [CLAUDE.md](CLAUDE.md) - Developer guide
- [ARCHITECTURE.md](ARCHITECTURE.md) - System design

**For Migration**
- [MIGRATION_SUMMARY.md](MIGRATION_SUMMARY.md) - From old scripts

**Project Info**
- [DELIVERABLES.txt](DELIVERABLES.txt) - Complete checklist
- [INDEX.md](INDEX.md) - This file

---

## 🎊 Ready to Get Started?

1. **First time?** → Read [QUICKSTART.md](QUICKSTART.md)
2. **Want details?** → Read [README.md](README.md)
3. **Test it?** → Run `python test_pipeline.py`
4. **Use it?** → Run `python main.py`

---

*Last Updated: 2026-06-22*  
*Status: Production Ready ✓*
