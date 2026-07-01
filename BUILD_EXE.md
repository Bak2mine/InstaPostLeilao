# Building Standalone Executable (EXE)

This guide explains how to create a standalone `leiloaria-generator.exe` that doesn't require Python.

## Prerequisites

These are one-time installations on the BUILD machine (not required on user machines):

1. **Python 3.8+** installed and in PATH
2. **PyInstaller**:
   ```bash
   pip install pyinstaller
   ```

## Build Steps

### Option 1: Automated Build (Recommended)

1. Open Command Prompt in the `Post` directory
2. Run:
   ```bash
   python build_exe.py
   ```
3. The EXE will be created at: `dist/leiloaria-generator.exe`

### Option 2: Manual Build with PyInstaller

```bash
pyinstaller leiloaria.spec
```

## Distribution to Users

### Files Required on User Machine

Users need:
- ✓ `leiloaria-generator.exe` (standalone, no Python needed)
- ✓ Template PPTX files:
  - `1 e 2 praça.pptx`
  - `2praca.pptx`
  - `1prac.pptx`
  - `tipo4.pptx`
- ✓ `output/` directory (will be created if missing)

**Files NOT needed on user machine:**
- ✗ Python installation
- ✗ Python source files (*.py)
- ✗ requirements.txt
- ✗ Virtual environment

### Setup for Users

1. Create a folder: `C:\leiloaria\` (or anywhere)
2. Copy `leiloaria-generator.exe` into it
3. Copy the 4 PPTX template files into the same folder
4. The `output/` folder will be created automatically

### Usage for Users

**Option 1: Double-click the EXE**
- Opens Command Prompt and runs the full pipeline

**Option 2: Command-line with options**
```bash
leiloaria-generator.exe --limit 10
leiloaria-generator.exe --skip 50 --limit 20
```

## External Dependencies (Still Required)

Users still need these installed (one-time):

### 1. LibreOffice
Required for PDF conversion from PPTX.

**Download:** https://www.libreoffice.org/download/
- Install: Accept all defaults
- Default path: `C:\Program Files\LibreOffice\program\soffice.exe`

### 2. ImageMagick
Required for PNG export (Instagram format).

**Download:** https://imagemagick.org/script/download.php#windows
- Choose: `ImageMagick-7.1.2-Q16-x64-static.exe` or newer
- Install to default location: `C:\Program Files\ImageMagick-7.1.2-Q16\`

### 3. Ghostscript (Optional but recommended)
Improves PDF quality. Download: https://www.ghostscript.com/download/gsdnld.html

## Troubleshooting Build

### "pyinstaller command not found"
Install PyInstaller:
```bash
pip install pyinstaller
```

### "File not found" errors during build
Ensure you're running from the `Post` directory where main.py exists.

### Large EXE file
Expected: 50-150 MB depending on dependencies. This is normal.

### "Python not found" error on build machine
Add Python to PATH:
1. Run installer again
2. Check "Add Python to PATH"

## Testing the EXE

After build, test the executable:

```bash
# Show help
leiloaria-generator.exe --help

# Process 1 property
leiloaria-generator.exe --limit 1
```

## Rollback to Python

If you need to go back to running Python directly:
```bash
python main.py --limit 10
```

## Size Optimization

If you need to reduce the EXE size:

1. Use UPX compression (included in spec):
   ```bash
   pip install upx
   pyinstaller leiloaria.spec --additional-hooks-dir=.
   ```

2. Or strip debug info:
   Edit `leiloaria.spec` and change `debug=True` to `debug=False`

## CI/CD Integration

To automate builds on every release:

See `BUILD_EXE.md` for GitHub Actions workflow template.

## Support

If users report issues:
1. Check LibreOffice and ImageMagick are installed
2. Verify templates are in same folder as EXE
3. Run in Command Prompt to see error messages
4. Check internet connection (scraping requires it)
