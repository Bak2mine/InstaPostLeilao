# User Setup Checklist

Print this and follow along to get started!

## Pre-Setup (5 minutes)

- [ ] Close all running applications
- [ ] Ensure you have admin rights on your computer
- [ ] Check you have internet connection

## Step 1: Install LibreOffice (3 minutes)

- [ ] Go to: https://www.libreoffice.org/download/
- [ ] Click "Download version X.X"
- [ ] Run the installer
- [ ] Click "Next" → "Typical Install" → "Finish"
- [ ] Verify: Open `C:\Program Files\LibreOffice\program\`
  - You should see `soffice.exe` file

**Done!** LibreOffice is installed.

---

## Step 2: Install ImageMagick (3 minutes)

- [ ] Go to: https://imagemagick.org/script/download.php#windows
- [ ] Scroll down to "Binary Releases"
- [ ] Download: `ImageMagick-7.1.2-Q16-x64-static.exe` (or newer)
- [ ] Run the installer
- [ ] Keep default settings
- [ ] Click "Finish"
- [ ] Verify: Open `C:\Program Files\ImageMagick-7.1.2-Q16\`
  - You should see `magick.exe` file

**Done!** ImageMagick is installed.

---

## Step 3: Setup Folder (2 minutes)

- [ ] Create a new folder: `C:\leiloaria\`
- [ ] Get these files from your colleague:
  - [ ] `leiloaria-generator.exe`
  - [ ] `1 e 2 praça.pptx`
  - [ ] `2praca.pptx`
  - [ ] `1prac.pptx`
  - [ ] `tipo4.pptx`
- [ ] Copy all 5 files into `C:\leiloaria\`

**Your folder should now look like:**
```
C:\leiloaria\
├── leiloaria-generator.exe
├── 1 e 2 praça.pptx
├── 2praca.pptx
├── 1prac.pptx
└── tipo4.pptx
```

**Done!** Setup complete.

---

## Step 4: First Run (Variable)

- [ ] Open Command Prompt
  - Press `Win + R`, type `cmd`, press Enter
- [ ] Navigate to folder:
  ```
  cd C:\leiloaria
  ```
- [ ] Test with 1 property:
  ```
  leiloaria-generator.exe --limit 1
  ```
- [ ] Watch the output
- [ ] When done, check `output/` folder for PNG files

**Success!** You can now run the generator.

---

## How to Use (Anytime)

### Option 1: Run Everything (Easiest)
```bash
cd C:\leiloaria
leiloaria-generator.exe
```

### Option 2: Run Specific Count
```bash
# Process first 5
leiloaria-generator.exe --limit 5

# Process first 20
leiloaria-generator.exe --limit 20
```

### Option 3: Resume from Checkpoint
```bash
# Skip first 50, then process 20
leiloaria-generator.exe --skip 50 --limit 20
```

### Output
Check these folders:
- **`output/`** - Your generated PNG files (ready for Instagram!)
- Command Prompt shows progress and any errors

---

## Troubleshooting

### "Command not found" or "File not found"
- [ ] Verify you're in `C:\leiloaria\` folder
- [ ] Verify file exists: `dir leiloaria-generator.exe`
- [ ] Check spelling of command

### "LibreOffice not found"
- [ ] Verify installation: `C:\Program Files\LibreOffice\program\soffice.exe` exists
- [ ] Restart computer after install
- [ ] Reinstall LibreOffice if needed

### "ImageMagick not found"
- [ ] Verify installation: `C:\Program Files\ImageMagick-7.1.2-Q16\magick.exe` exists
- [ ] Restart computer after install
- [ ] Reinstall ImageMagick if needed

### "Templates not found" error
- [ ] Verify all 4 PPTX files are in `C:\leiloaria\`
- [ ] Check spelling (capitals matter!)
  - `1 e 2 praça.pptx` ← note the space and accent
  - `2praca.pptx`
  - `1prac.pptx`
  - `tipo4.pptx`

### All PNG images are white
- [ ] Check internet connection
- [ ] Check ImageMagick is installed
- [ ] Try again later (website may be down)

### Pipeline takes very long
- [ ] This is normal! ~15 seconds per property
- [ ] For 58 properties: ~15 minutes total
- [ ] Do NOT close Command Prompt while running

---

## Support

**Need help?** Ask your colleague who gave you this program.

**Know the answer?** Here are key contacts:
- [ ] Contact: ___________________
- [ ] Phone: _____________________
- [ ] Email: ______________________

---

## Verification Checklist

Before you start processing all properties:

- [ ] LibreOffice is installed
- [ ] ImageMagick is installed
- [ ] All 4 PPTX files are in `C:\leiloaria\`
- [ ] `leiloaria-generator.exe` runs `--limit 1` successfully
- [ ] PNG files appear in `output/` folder
- [ ] PNG files are NOT all-white (if white, check ImageMagick)

**All checked?** You're ready to go!

---

## Tips & Tricks

✓ **Keep Command Prompt open** - Don't close it while the generator runs

✓ **Internet required** - Must be online to download property images

✓ **Resume if interrupted** - If you have to stop, note the property number and resume:
```bash
leiloaria-generator.exe --skip 25 --limit 10
```

✓ **Batch processing** - Can run multiple times:
```bash
leiloaria-generator.exe --limit 50    # Day 1: First 50
leiloaria-generator.exe --skip 50     # Day 2: Rest
```

✓ **Check progress** - Count PNG files in `output/` to see how many processed

---

**Setup Date:** _______________

**Setup by:** _______________

**Questions? Contact:** _______________
