# CSV Image Import Validation Guide

## System Capabilities Verified ✅

Your boutique CSV import system supports:

### 1. **ZIP File Method** (Recommended for Teams)
- Upload CSV + ZIP file together
- ZIP contains images in any folder structure
- CSV references images via `image_path` column
- Maximum ZIP size: 50MB

### 2. **URL Method** (Recommended for Web Images)
- Upload CSV file only
- CSV contains `image_url` column with direct image links
- Images downloaded automatically during import
- No file upload size limits for images

### 3. **Hybrid Method**
- Single CSV with both `image_url` and `image_path` columns
- System uses whichever is available per product

---

## Quick Validation Test (5 minutes)

### Option A: Test with Public Image URLs ⚡ (Recommended - Fastest)

**1. Create test CSV file** (`test_products.csv`):
```csv
name,category,price,description,inventory,sizes,colors,image_url
"Phi Beta Sigma Classic Tee",apparel,24.99,"Premium quality t-shirt",100,"S, M, L, XL, 2XL","Black, White, Navy, Maroon",https://via.placeholder.com/300x300/000000/FFFFFF?text=PBS+Tee
"Sigma Beta Club Polo",apparel,34.99,"Professional polo shirt",75,"S, M, L, XL","Navy, White, Black",https://via.placeholder.com/300x300/001f3f/FFFFFF?text=PBS+Polo
"Chapter Embroidered Cap",accessories,19.99,"Adjustable baseball cap",50,"One Size","Black, Navy, White, Maroon",https://via.placeholder.com/300x300/1a1a2e/FFFFFF?text=PBS+Cap
"Stainless Steel Tumbler",drinkware,22.99,"Double-wall insulated tumbler",80,"16oz, 20oz, 24oz","Black, Silver, White",https://via.placeholder.com/300x300/708090/FFFFFF?text=PBS+Tumbler
```

**2. Go to import page:**
- URL: `http://localhost:8000/pages/boutique/admin/import-products/`
- Upload the CSV file
- Click "Import Products"

**3. Verify results:**
- Check for success message: "Successfully imported 4 new products!"
- Visit `http://localhost:8000/pages/boutique/` 
- All 4 products should appear with placeholder images

---

### Option B: Test with ZIP File Method (Full Test)

**1. Create CSV file** (`products.csv`):
```csv
name,category,price,description,inventory,sizes,colors,image_path
"Phi Beta Sigma Premium Tee",apparel,24.99,"High quality fraternity tee",100,"S, M, L, XL, 2XL","Black, White, Navy",images/tshirt.jpg
"Classic Cap",accessories,19.99,"Baseball cap with emblem",50,"One Size","Black, Navy, White",images/cap.jpg
"Insulated Tumbler",drinkware,18.99,"Double-wall insulated",75,"16oz, 20oz, 24oz","Black, Silver",images/tumbler.jpg
```

**2. Prepare images folder:**
```
Download or create test images:
- images/tshirt.jpg (any 300x300px image)
- images/cap.jpg
- images/tumbler.jpg
```

**3. Create ZIP structure:**
```
MyTestProducts/
├── products.csv
└── images/
    ├── tshirt.jpg
    ├── cap.jpg
    └── tumbler.jpg
```

**4. Create ZIP file:**
```bash
# On Mac/Linux:
cd MyTestProducts
zip -r products.zip products.csv images/

# On Windows:
# Right-click folder → Send to → Compressed (zipped) folder
```

**5. Upload to import page:**
- URL: `http://localhost:8000/pages/boutique/admin/import-products/`
- Upload `products.zip` as "Images ZIP File"
- Click "Import Products"

**6. Verify:**
- Success message should appear
- Check shop page for products with custom images

---

## Testing Both Methods Side-by-Side

**Test CSV** (`mixed_test.csv`):
```csv
name,category,price,description,inventory,sizes,colors,image_url,image_path
"Product with URL",apparel,19.99,"Uses external image",50,"S, M, L","Black, White",https://via.placeholder.com/300x300/FF0000/FFFFFF?text=URL+Image,
"Product with ZIP",apparel,29.99,"Uses ZIP image",40,"S, M, L",,Black, Navy",images/local.jpg
```

This tests both approaches in one import!

---

## Validation Checklist ✅

After importing, verify:

- [ ] Products appear on shop page (`/pages/boutique/`)
- [ ] Images display on product cards
- [ ] Images appear correctly (not broken or missing)
- [ ] Product details show correctly (price, description, sizes, colors)
- [ ] Edit/Delete buttons work (for officers)
- [ ] Shopping cart functionality works
- [ ] Images are responsive on mobile
- [ ] Dark mode displays images correctly
- [ ] No database errors in console

---

## Troubleshooting Import Issues

### "CSV file is required"
- Make sure you selected a CSV file
- File must have `.csv` extension

### "CSV must contain these columns: name, category, price"
- Check CSV has these 3 columns minimum
- Column names must match exactly (lowercase)
- No extra spaces in column names

### "Invalid category"
- Must be: `apparel`, `accessories`, `drinkware`, or `other`
- Check spelling and case

### "Price must be a valid number"
- Price column should have numeric values only
- Use format: `19.99` or `25`
- No currency symbols like `$19.99`

### Images Not Showing After ZIP Import
- Check file names match `image_path` column exactly (case-sensitive!)
- Example: If CSV says `images/MyTee.jpg`, ZIP must have exactly that path
- No spaces in file names

### Images Not Downloading from URLs
- Verify URLs work in browser first
- Check URL is publicly accessible (not blocked)
- Use HTTPS URLs when possible
- JPEG and PNG format recommended

### "Error extracting images"
- Make sure file is valid ZIP format
- Try creating ZIP from command line instead of GUI
- Test with smaller ZIP file first

---

## Performance Notes

**Recommended Import Sizes:**
- **Small**: 1-10 products (any method)
- **Medium**: 10-50 products (URL method preferred)
- **Large**: 50-100+ products (ZIP method recommended - faster)

**File Size Limits:**
- CSV: Max 5MB
- ZIP: Max 50MB

**Image Quality:**
- Size: 300x300px minimum recommended
- Format: JPG, PNG
- Quality: Compressed (200-500KB each recommended)

---

## Live Testing URLs

After successful import, test these URLs:

1. **Shop Page**: `http://localhost:8000/pages/boutique/`
2. **Product Detail**: `http://localhost:8000/pages/boutique/product/<id>/`
3. **Admin Import**: `http://localhost:8000/pages/boutique/admin/import-products/`
4. **Manage Products** (if officer): `http://localhost:8000/pages/boutique/admin/`

---

## What Gets Validated Automatically

✅ CSV format and structure
✅ Required columns present
✅ Data types (price is number, inventory is number)
✅ Category is valid
✅ No duplicate products (by name)
✅ Image ZIP extracts successfully
✅ Image files exist in ZIP before creating products
✅ Image URLs respond with valid images

---

## Next Steps After Validation

1. **If successful**: You're ready for production imports!
2. **If issues**: Check troubleshooting section above
3. **Need help**: Review [CSV_IMAGE_IMPORT_GUIDE.md](CSV_IMAGE_IMPORT_GUIDE.md) for advanced usage
