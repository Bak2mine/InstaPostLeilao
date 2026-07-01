# Leiloaria Property PDF Generator - Complete Index

## 📦 The Executable

**[dist/leiloaria-generator.exe](dist/leiloaria-generator.exe)** (34 MB)
- Standalone executable for coworkers
- No Python required
- Ready to distribute
- Test with: `leiloaria-generator.exe --help`

---

## 📚 Documentation

### For End Users (Non-Technical)
1. **[USER_SETUP_CHECKLIST.md](USER_SETUP_CHECKLIST.md)** ⭐ START HERE
   - Step-by-step setup (10 min)
   - Checklist format
   - Troubleshooting included
   - Print and follow along

2. **[DISTRIBUTE.md](DISTRIBUTE.md)** - Detailed Guide
   - Complete setup instructions
   - Usage examples
   - Troubleshooting guide
   - FAQ section

3. **[QUICK_START.txt](QUICK_START.txt)** - Quick Reference
   - One-page cheat sheet
   - Copy to folder with EXE
   - Basic commands only

### For Developers (Technical)
1. **[BUILD_EXE.md](BUILD_EXE.md)** - Build Instructions
   - How to rebuild EXE
   - Troubleshooting build issues
   - Optimization tips

2. **[EXE_SUMMARY.md](EXE_SUMMARY.md)** - Technical Overview
   - What was built and why
   - File sizes
   - Build process

3. **[RELEASE_NOTES.md](RELEASE_NOTES.md)** - Release Details
   - Version information
   - What changed
   - Support info

### Original Documentation
- **[CLAUDE.md](CLAUDE.md)** - Project architecture & design
- **[PIPELINE_README.md](PIPELINE_README.md)** - Pipeline documentation
- **[README.md](README.md)** - Original readme

---

## 🛠️ Build Files

### Main Build Scripts
- **[build_exe.py](build_exe.py)** - Automated build script
  - Run: `python build_exe.py`
  - Creates `dist/leiloaria-generator.exe`

- **[leiloaria.spec](leiloaria.spec)** - PyInstaller configuration
  - Manual build: `pyinstaller leiloaria.spec`
  - Reusable for future builds

### Configuration
- **[config.py](config.py)** - Pipeline configuration
- **[requirements.txt](requirements.txt)** - Python dependencies

---

## 🚀 Core Pipeline (Python)

### Executable Entry Point
- **[main.py](main.py)** - CLI entry point

### Main Modules
- **[pipeline.py](pipeline.py)** - Orchestrator
- **[scraper.py](scraper.py)** - Web scraping
- **[pptx_handler.py](pptx_handler.py)** - PowerPoint handling
- **[image_processor.py](image_processor.py)** - Image processing
- **[pdf_exporter.py](pdf_exporter.py)** - Now: PNG exporter

### Testing
- **[test_pipeline.py](test_pipeline.py)** - Single property test
- **[check_extraction.py](check_extraction.py)** - Data validation
- **[diagnose_pptx.py](diagnose_pptx.py)** - Template diagnosis

---

## 📄 Templates

**Required for both Python and EXE versions:**
- **[1 e 2 praça.pptx](1%20e%202%20praça.pptx)** - 2 auctions + discount
- **[2praca.pptx](2praca.pptx)** - 1 auction + discount  
- **[1prac.pptx](1prac.pptx)** - 2 auctions, no discount
- **[tipo4.pptx](tipo4.pptx)** - 1 auction, no discount

**Note:** Always keep 4 templates in same folder as EXE or Python scripts.

---

## 📁 Directories

- **[dist/](dist/)** - Build output (contains EXE)
- **[build/](build/)** - PyInstaller build artifacts (temporary)
- **[output/](output/)** - Generated PNG files (created at runtime)
- **[.temp/](.)** - Temporary files during processing (hidden)
- **[imoveis/](imoveis/)** - Legacy (deprecated)

---

## 🎯 Quick Start Paths

### Path 1: I Want to Use It (No Python)
1. ⭐ Read: [USER_SETUP_CHECKLIST.md](USER_SETUP_CHECKLIST.md)
2. Download: [dist/leiloaria-generator.exe](dist/leiloaria-generator.exe)
3. Follow the checklist
4. Run: `leiloaria-generator.exe`

### Path 2: I Want to Share It With Others
1. Read: [DISTRIBUTE.md](DISTRIBUTE.md)
2. Collect: EXE + 4 templates + DISTRIBUTE.md
3. Create: ZIP or share via network
4. Send: To coworkers with instructions

### Path 3: I Want to Build It Myself
1. Read: [BUILD_EXE.md](BUILD_EXE.md)
2. Install: `pip install pyinstaller`
3. Run: `python build_exe.py`
4. Output: `dist/leiloaria-generator.exe`

### Path 4: I Want to Use Python Directly
1. Install: `pip install -r requirements.txt`
2. Run: `python main.py --limit 10`
3. Check: Output folder for PNG files

### Path 5: I'm a Developer and Want Context
1. Read: [CLAUDE.md](CLAUDE.md) - Architecture
2. Read: [PIPELINE_README.md](PIPELINE_README.md) - Usage
3. Review: [pipeline.py](pipeline.py) - Main code
4. Check: [BUILD_EXE.md](BUILD_EXE.md) for build process

---

## ✅ Checklist by Use Case

### End User (Non-Technical)
- [ ] Read [USER_SETUP_CHECKLIST.md](USER_SETUP_CHECKLIST.md)
- [ ] Install LibreOffice
- [ ] Install ImageMagick
- [ ] Copy EXE + templates to folder
- [ ] Run: `leiloaria-generator.exe`
- [ ] Check output/ for PNG files

### Project Manager (Distributing to Team)
- [ ] Verify [dist/leiloaria-generator.exe](dist/leiloaria-generator.exe) exists
- [ ] Gather files: EXE + 4 templates
- [ ] Include: [DISTRIBUTE.md](DISTRIBUTE.md) + [USER_SETUP_CHECKLIST.md](USER_SETUP_CHECKLIST.md)
- [ ] Create: ZIP or share via cloud
- [ ] Send: With setup instructions
- [ ] Support: Direct users to troubleshooting section

### Developer (Maintaining/Rebuilding)
- [ ] Python 3.8+ installed
- [ ] Run: `pip install -r requirements.txt`
- [ ] Build: `python build_exe.py`
- [ ] Test: `dist/leiloaria-generator.exe --limit 1`
- [ ] Verify: PNG files generated in output/
- [ ] Update: [RELEASE_NOTES.md](RELEASE_NOTES.md) with version
- [ ] Distribute: New EXE to users

---

## 🔗 Key Links

### External Resources
- LibreOffice: https://www.libreoffice.org/download/
- ImageMagick: https://imagemagick.org/script/download.php#windows
- PyInstaller: https://www.pyinstaller.org/

### Website (Data Source)
- Leiloaria: https://leiloariasmart.com.br/

---

## 📊 File Statistics

| File | Size | Purpose |
|------|------|---------|
| leiloaria-generator.exe | 34 MB | Main executable |
| build_exe.py | 2 KB | Build script |
| *.pptx templates | ~500 KB | PowerPoint templates |
| *.py source files | ~50 KB | Python source code |

---

## 🆘 Support Quick Links

- **Setup Issues?** → [USER_SETUP_CHECKLIST.md](USER_SETUP_CHECKLIST.md)
- **Running into Problems?** → [DISTRIBUTE.md](DISTRIBUTE.md) (Troubleshooting section)
- **Need to Rebuild?** → [BUILD_EXE.md](BUILD_EXE.md)
- **Technical Details?** → [EXE_SUMMARY.md](EXE_SUMMARY.md)

---

## 📝 Document Types

### Blue Shirts (End Users)
👕 Print and follow:
- [USER_SETUP_CHECKLIST.md](USER_SETUP_CHECKLIST.md)
- [QUICK_START.txt](QUICK_START.txt)

### Support Team
🆘 Reference for troubleshooting:
- [DISTRIBUTE.md](DISTRIBUTE.md) (complete guide)
- [RELEASE_NOTES.md](RELEASE_NOTES.md) (tech specs)

### Developers
👨‍💻 For building and maintaining:
- [BUILD_EXE.md](BUILD_EXE.md)
- [CLAUDE.md](CLAUDE.md)
- [EXE_SUMMARY.md](EXE_SUMMARY.md)

### Project Managers
📋 For distribution and planning:
- [RELEASE_NOTES.md](RELEASE_NOTES.md)
- [DISTRIBUTE.md](DISTRIBUTE.md)
- [EXE_SUMMARY.md](EXE_SUMMARY.md)

---

## 🎓 Learning Path

1. **Understand the goal:**
   - Read the project overview in [CLAUDE.md](CLAUDE.md)

2. **See how it works:**
   - Follow [USER_SETUP_CHECKLIST.md](USER_SETUP_CHECKLIST.md)
   - Run: `leiloaria-generator.exe --limit 1`

3. **Understand the build:**
   - Read [EXE_SUMMARY.md](EXE_SUMMARY.md)
   - Review [BUILD_EXE.md](BUILD_EXE.md)

4. **Deep dive into code:**
   - Study [pipeline.py](pipeline.py)
   - Review [scraper.py](scraper.py)
   - Check [pptx_handler.py](pptx_handler.py)

5. **Share with others:**
   - Follow [DISTRIBUTE.md](DISTRIBUTE.md)
   - Give checklist to users
   - Support via troubleshooting guide

---

**Last Updated:** 2026-06-30  
**Status:** ✓ Ready for distribution  
**Version:** 1.0
