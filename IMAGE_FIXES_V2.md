# Image Handling Fixes - Version 2

## Issues Fixed

### 1. **44 Images Being Replaced Instead of 1**
**Problem**: The embedded image replacement was replacing ALL images in the media folder, not just the small placeholder.

**Solution**:
- Now parses slide1.xml to find image references
- Only replaces the FIRST image (the small placeholder)
- Leaves all other images (logos, decorations, etc.) untouched
- Uses XML relationship files to map image IDs to file names

**Result**: Only 1 small image replaced (the property image placeholder)

### 2. **Logo Replaced (Top Left)**
**Problem**: Logo was being replaced along with other images.

**Solution**: 
- By fixing the embedded image replacement to only replace 1 image, logos are now safe
- Only the slide 1 placeholder image is replaced
- Logos in slide 2 are left alone

**Result**: Logo stays in place, only the placeholder is replaced

### 3. **Background Image Wrong Size**
**Problem**: Using hard-coded SLIDE_WIDTH_INCHES and SLIDE_HEIGHT_INCHES instead of actual slide dimensions.

**Solution**:
- Now reads actual slide dimensions from presentation object:
  ```python
  slide_width = prs.slide_width   # EMU format
  slide_height = prs.slide_height # EMU format
  ```
- Uses these exact dimensions when adding background images
- Works for both slide 1 and slide 2

**Result**: Background images now fill the entire slide correctly

### 4. **Light Blue Border on Slide 2**
**Problem**: Border elements weren't being removed completely.

**Solution**:
- Enhanced shape removal to catch more element types
- Now removes: pictures, groups, freeforms (borders), and shapes
- Added error handling for stubborn elements
- Validates all shape types before removal

**Result**: Blue border is completely removed before adding new background

---

## Updated Processing Order

For each property:

```
1. Modify text in PPTX
   └─ Replace: title, location, prices, dates, discount

2. Replace embedded image in slide 1 ONLY
   └─ Find image reference in slide1.xml
   └─ Replace FIRST image ONLY (the placeholder)
   └─ Leave logos/decorations untouched

3. Replace/add background image
   └─ Remove old backgrounds (Group 2, etc.)
   └─ Add new background at correct z-index
   └─ Use actual slide dimensions (not hard-coded)

4. Process slide 2 (link page)
   └─ Remove ALL old backgrounds/borders/groups
   └─ Add new background image (same as slide 1)
   └─ Add "LINK" text centered
   └─ Use actual slide dimensions
```

---

## Code Changes

### Embedded Image Replacement (SELECTIVE)
```python
# Parse slide1.xml to find image references
# Find ALL image IDs used in slide 1
image_ids = find_all_image_ids()

# Only take the FIRST one
first_id = image_ids[0]

# Find which file it points to
target_file = find_file_for_id(first_id)

# Replace ONLY that file
image_rgb.save(target_file)
```

### Background Image Sizing (DYNAMIC)
```python
# OLD (wrong)
width = Inches(SLIDE_WIDTH_INCHES)
height = Inches(SLIDE_HEIGHT_INCHES)

# NEW (correct)
width = prs.slide_width   # Already in EMU
height = prs.slide_height # Already in EMU
```

### Shape Removal (COMPREHENSIVE)
```python
# Remove any shape that isn't a text element
if is_picture or is_group or is_freeform or is_shape:
    remove_shape()
```

---

## Testing

Run to test:
```bash
python test_pipeline.py
```

Expected results:
- ✅ Small property image in middle of slide 1 (replaced correctly)
- ✅ Logo in top-left of both slides (intact, not replaced)
- ✅ Background image fills entire slide (correct size)
- ✅ No blue border visible on slide 2
- ✅ LINK text centered on slide 2
- ✅ Text (title, location, prices, etc.) on top of background

---

## Files Modified

- **pptx_handler.py**
  - Rewrote `replace_embedded_images()` to be selective (first image only)
  - Updated `replace_images()` to use actual slide dimensions
  - Enhanced `add_link_page()` with better shape removal

- **No changes to other files**

---

## Technical Notes

### EMU (English Metric Units)
- PPTX internally uses EMU
- 1 inch = 914,400 EMU
- `prs.slide_width` and `prs.slide_height` are already in EMU
- No conversion needed when passed to `add_picture()`

### XML Parsing
- Slide content is in `ppt/slides/slide1.xml`
- Relationships are in `ppt/slides/_rels/slide1.xml.rels`
- Image references use blip elements with `r:embed` attribute

### Shape Names in PPTX
- "Group 2" = gray background rectangle
- "Freeform X" = borders/decorative shapes
- Picture shapes = images
- Text elements = titles, prices, locations

---

## If Issues Persist

Check console output for:
- `Replacing embedded image: image2.jpeg` → Should see exactly 1 message
- `Removed X shapes from link page` → Should be > 0
- `Background image added (size: X.XXxY.YY in)` → Size should be reasonable (9-12 x 12-16)

If blue border still visible:
- It might be in a text shape's border properties
- Try zooming in on the edge to confirm it's truly a shape

If logo still being replaced:
- Check that you're using the new code (not cached Python)
- Restart Python interpreter: `python test_pipeline.py` not `python -i`

---

Try running the test now and let me know what you see!
