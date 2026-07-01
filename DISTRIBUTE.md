# Distribution Guide for Non-Python Users

The `leiloaria-generator.exe` standalone executable allows your coworkers to run the pipeline **without installing Python**.

## For Developers (Building the EXE)

### Prerequisites
- Python 3.8+ installed
- Run once: `pip install pyinstaller`

### Build
```bash
cd Post/
python build_exe.py
```

Output: `dist/leiloaria-generator.exe` (378 MB - includes all templates bundled)

---

## For End Users (Running the EXE)

### Setup (One Time)

1. **Install LibreOffice** (required for PDF conversion)
   - Download: https://www.libreoffice.org/download/
   - Install with default settings
   - Verify: You should see `C:\Program Files\LibreOffice\program\soffice.exe`

2. **Install ImageMagick** (required for PNG export)
   - Download: https://imagemagick.org/script/download.php#windows
   - Choose: `ImageMagick-7.1.2-Q16-x64-static.exe` or newer
   - Install to default location: `C:\Program Files\ImageMagick-7.1.2-Q16\`

3. **Setup folder structure** (SIMPLE!)
   ```
   C:\leiloaria\                           (any location)
   ├── leiloaria-generator.exe             (copy from dist/ - that's it!)
   └── output/                             (created automatically)
   ```
   
   **Note:** Templates are bundled inside the EXE - no need to copy PPTX files!

### Usage

#### Option 1: Double-Click (Easiest)
Simply double-click `leiloaria-generator.exe` to process all properties.

#### Option 2: Command Line
Open Command Prompt in the folder with `leiloaria-generator.exe`:

```bash
# Process all properties
leiloaria-generator.exe

# Process first 10 properties
leiloaria-generator.exe --limit 10

# Skip first 50, process next 20
leiloaria-generator.exe --skip 50 --limit 20

# Show help
leiloaria-generator.exe --help
```

#### Option 3: Batch File (Windows Only)
Save as `run.bat` in the same folder:

```batch
@echo off
leiloaria-generator.exe %*
pause
```

Then just double-click `run.bat` or run: `run.bat --limit 10`

### Output

Generated files appear in the `output/` folder:
- `Property Name (City-State)_slide1.png` - First slide for Instagram
- `Property Name (City-State)_slide2.png` - Second slide for Instagram

**Note:** Two PNG files are generated per property (one per slide).

---

## Troubleshooting

### "LibreOffice not found" error
- Verify LibreOffice is installed: Check `C:\Program Files\LibreOffice\`
- Reinstall if needed: https://www.libreoffice.org/

### "ImageMagick not found" error
- Verify ImageMagick is installed: Check `C:\Program Files\ImageMagick-7.1.2-Q16\`
- Reinstall if needed: https://imagemagick.org/

### All-white PNG images
- Make sure ImageMagick is installed correctly
- Check internet connection (needs to download property images)

### Connection timeouts
- Check your internet connection
- Website may be temporarily down (try again later)

### Template files not found
- This shouldn't happen - templates are bundled in the EXE
- Verify you have the correct EXE file (should be ~378 MB)
- Try re-downloading the EXE from your colleague

---

## Files to Distribute

**Minimum required for users:**
- ✓ `leiloaria-generator.exe` (378 MB - **includes templates!**)

**Optional (helpful):**
- ? `DISTRIBUTE.md` (this file - setup instructions)
- ? `run.bat` (batch shortcut for Windows)

**NOT needed:**
- ✗ Any `.pptx` template files (bundled in EXE)
- ✗ Any `.py` files
- ✗ `requirements.txt`
- ✗ Python installation
- ✗ Virtual environment

**That's it!** Just one file to distribute.

---

## Creating a Portable Package

To create a ZIP file for distribution:

```powershell
# PowerShell
Compress-Archive -Path `
  "dist/leiloaria-generator.exe", `
  "Post/DISTRIBUTE.md" `
  -DestinationPath "leiloaria-portable.zip"
```

Share `leiloaria-portable.zip` - users just extract and run. That's all they need!

---

## Support

If a user encounters issues:

1. **First:** Verify LibreOffice and ImageMagick are installed
2. **Then:** Run from Command Prompt to see error messages
3. **Check:** Are all 4 PPTX templates in the same folder as the EXE?
4. **Finally:** Check internet connection (pipeline requires web access)

---

## What Changed from Python Version?

| Aspect | Python | EXE |
|--------|--------|-----|
| Python required? | ✓ Yes | ✗ No |
| Installation size | ~100 MB (env) | 378 MB (single file, includes templates) |
| Setup time | 10 min (env + deps) | 1 min (just copy exe) |
| Templates needed? | ✓ Yes (4 files) | ✗ No (bundled inside) |
| Runtime speed | ~15 sec/property | ~15 sec/property |
| Command line | Yes | Yes |
| GUI | No | No |

**Same functionality, no Python needed for end users.**
