# Image Handling Fixes - Summary

## Issues Fixed

### 1. Background Image Layering (Slide 1)
**Problem**: New background image was added but positioned behind existing template elements, making it invisible.

**Solution**: 
- Properly detect and remove placeholder shapes and groups from template
- Use EMU (English Metric Units) to calculate shape sizes accurately
- Only remove large shapes (> 5 inches) which are backgrounds/placeholders
- Move new image to correct z-index (position 2) using `_spTree.insert()`

### 2. Embedded Image Not Replacing (Small Middle Image)
**Problem**: The small image in the middle of the slide wasn't being replaced because it was embedded directly in the PPTX ZIP structure.

**Solution**:
- Created new `replace_embedded_images()` function
- Extracts PPTX as ZIP
- Finds all images in `ppt/media/` directory
- Replaces each with the property image (maintaining format: JPEG stays JPEG, PNG stays PNG)
- Re-zips the PPTX

### 3. Link Page (Slide 2) Issues
**Problems**: 
- Image was from different property
- Image was wrong size

**Solutions**:
- Explicitly pass the SAME image object to both slide 1 and slide 2
- Add debugging to show which shapes are being removed
- Ensure link page uses identical slide dimensions (11.25 x 14.06 inches)
- Process image identically: crop + RGB convert
- Remove all existing shapes before adding new ones

---

## Updated Function Calls

### Pipeline Execution Order (in `pipeline.py`)

```python
# Step 1: Modify text (already working fine)
PPTXHandler.modify_text(template, data, output)

# Step 2: Replace EMBEDDED images (NEW - handles small image)
PPTXHandler.replace_embedded_images(pptx_path, image)

# Step 3: Replace BACKGROUND images (updated - better layering)
PPTXHandler.replace_images(pptx_path, image)

# Step 4: Add LINK page (updated - consistent image)
PPTXHandler.add_link_page(pptx_path, image)
```

---

## Key Code Changes

### Image Processing Chain
```
Original Image (from website)
    ↓
Crop sidebars (20% from each side)
    ↓
Convert to RGB (JPEG compatibility)
    ↓
Step 1: Replace embedded images via ZIP
    ↓
Step 2: Replace/add background image via python-pptx
    ↓
Step 3: Add link page with same image
    ↓
Final PPTX with all images
```

### Shape Removal Logic
```python
# For large background/placeholder shapes (> 5 inches)
if width > 5 or height > 5:
    remove_shape()

# For embedded images (in media folder)
if file in "ppt/media/image*":
    replace_with_new_image()
```

### Z-Index Positioning
```python
# Move new image to back of slide (before text)
slide.shapes._spTree.remove(picture_element)
slide.shapes._spTree.insert(2, picture_element)  # Position 2 = right after metadata
```

---

## Testing the Fixes

Run this to test with a single property:
```bash
python test_pipeline.py
```

Or with the first property only:
```bash
python main.py --limit 1
```

Expected results in generated PPTX:
1. ✅ Large background image visible (behind text, not obscuring it)
2. ✅ Small middle image replaced with property image
3. ✅ Slide 2 (link page) has same background image as slide 1
4. ✅ "LINK" text visible in center of slide 2

---

## Files Modified

- **pptx_handler.py**
  - Added `replace_embedded_images()` function
  - Updated `replace_images()` with better shape detection and removal
  - Updated `add_link_page()` with improved cleanup

- **pipeline.py**
  - Added call to `replace_embedded_images()`
  - Improved image extraction logging
  - Better error reporting

---

## Technical Details

### EMU Conversion
PPTX uses EMU (English Metric Units) internally:
- 1 inch = 914,400 EMU
- Conversion: `inches = emu / 914400`

### PPTX Structure
```
document.pptx (ZIP file)
├── ppt/
│   ├── slides/
│   │   ├── slide1.xml (slide 1 content)
│   │   └── slide2.xml (slide 2 content)
│   └── media/
│       ├── image1.jpg (embedded images)
│       ├── image2.jpg
│       └── ...
├── [Content_Types].xml
├── _rels/
└── docProps/
```

When we replace images, we're modifying the files in `ppt/media/`.

---

## Troubleshooting

### Still seeing old image on slide 1?
- Check that `replace_images()` is removing the Group 2 element
- Verify image size (should be visible if > 5 inches)
- Look at console output for "Removing:" messages

### Small image still not replaced?
- Check that `replace_embedded_images()` finds image files
- Verify console shows "Replaced embedded: image1.jpg" etc.
- Template might have multiple images (we replace all of them)

### Link page image wrong?
- Verify same image object passed to both functions
- Check console shows same image being processed both times
- Ensure slide 2 exists in template (most have 2 slides)

---

## Next Steps

1. Test with `python test_pipeline.py`
2. Open generated PPTX and verify:
   - Slide 1: Background visible, small image replaced, text on top
   - Slide 2: Same background image, LINK text centered
3. Run with `python main.py --limit 5` for batch test
4. Check `output/` folder for results

---

If images still aren't showing, let me know the exact error messages from the console output!
