# Image Handling Fixes - Version 3 (Targeted Group Removal)

## Root Cause Identified

The PowerPoint templates have a complex group structure:

**Slide 1 (Property Details):**
- **Group 2** (12.18 x 14.43 in) = Gray background covering entire slide
- **Group 5** (9.01 x 6.20 in) = Content area with image + title
- **Group 7** (9.01 x 2.31 in) = Pricing area
- **Group 10** (5.35 x 1.18 in) = Header area
- Plus various Freeforms (borders) and TextBoxes

**Slide 2 (Link Page):**
- **Group 2** (12.18 x 14.43 in) = Gray background
- **Group 5** (5.35 x 1.18 in) = Header
- **Group 8** (9.00 x 10.74 in) = Main content area
- **Group 11** (9.01 x 2.31 in) = Secondary area
- **Group 14** (9.01 x 10.74 in) = Another content area
- **Group 17** (7.51 x 1.10 in) = Footer area
- Plus TextBoxes with actual text ("LINK", "COMENTE", etc.)

## Issues Fixed

### 1. **Picture Below Background**
**Problem**: All groups were being removed indiscriminately, causing new images to layer incorrectly.

**Solution**:
- Only remove **Group 2** (the gray background)
- Leave ALL other groups intact (they contain the layout/structure)
- New background image is added after Group 2 is gone, so it layers correctly

### 2. **Wrong Property on Slide 2**
**Problem**: The image object was being reused across multiple properties if the PPTX file wasn't completely refreshed.

**Solution**:
- Use the SAME image object passed to both `replace_images()` and `add_link_page()`
- This ensures slide 1 and slide 2 always have the same property image

### 3. **Blue Border on Slide 2**
**Problem**: Only removing Group 2 left other decorative groups intact.

**Solution**:
- On slide 2, remove Groups 2, 5, 8, 11, 14, and 17 (all non-text groups)
- Keep TextBoxes which contain the actual content text
- This removes all background/border elements while preserving text

---

## Updated Code Logic

### Slide 1 (replace_images)
```python
# ONLY remove Group 2
for shape in slide.shapes:
    if shape.name == "Group 2":
        remove_shape()

# Add new background
add_background_image()
```

### Slide 2 (add_link_page)
```python
# Remove all non-text groups
groups_to_remove = ["Group 2", "Group 5", "Group 8", "Group 11", "Group 14", "Group 17"]
for shape in slide.shapes:
    if shape.name in groups_to_remove:
        remove_shape()

# Add new background
add_background_image()

# TextBoxes with "LINK", etc. are preserved
```

---

## Data Flow for Image Processing

### For Each Property:

```
1. Download image from website

2. Process image:
   - Crop sidebars (20%)
   - Convert to RGB

3. Slide 1 Processing:
   ├─ Replace embedded image (small placeholder in middle)
   ├─ Remove ONLY Group 2
   ├─ Add background image
   └─ Keep all other groups/text

4. Slide 2 Processing:
   ├─ Remove Groups 2, 5, 8, 11, 14, 17
   ├─ Add same background image
   ├─ Keep TextBoxes with "LINK" text
   └─ Result: clean link page with image

5. Save PPTX with both slides complete
```

---

## How to Test

```bash
python test_pipeline.py
```

**Expected Results:**

**Slide 1:**
- ✅ Background image fills entire slide
- ✅ Background image is BEHIND all text and groups
- ✅ Small property image in middle is replaced
- ✅ All text visible on top (title, location, prices, dates, discount)

**Slide 2:**
- ✅ Background image fills entire slide
- ✅ Same image as Slide 1
- ✅ "LINK" text centered
- ✅ No blue borders visible
- ✅ No gray background visible
- ✅ Website URL visible

---

## Files Modified

- **pptx_handler.py**
  - `replace_images()`: Only removes Group 2
  - `add_link_page()`: Removes specific groups on slide 2

- **pipeline.py**
  - Passes same image object to both slide functions

---

## Diagnostic Information

If you want to inspect another template, run:

```bash
python diagnose_pptx.py
```

This will show you:
- All shape names
- All group names
- Exact sizes of each shape
- What's inside each group
- Text content of each textbox

This helps identify which groups to remove for any template.

---

## Key Learning

PowerPoint groups are CONTAINERS that hold multiple elements. When we remove a group, we remove everything inside it. We need to be surgical:

- **Remove**: Large groups that are purely decorative (backgrounds, borders)
- **Keep**: Groups that contain important layout or content
- **Preserve**: TextBoxes with actual text values

The solution is to:
1. Identify which groups to remove using the diagnostic tool
2. Only remove those specific groups
3. Add new elements that layer correctly on top

This is why knowing the exact group structure is crucial!

---

Try running the test now. The image should be:
1. Visible (not behind other stuff)
2. Correct property (same on both slides)
3. No borders/artifacts visible

Let me know the results!
