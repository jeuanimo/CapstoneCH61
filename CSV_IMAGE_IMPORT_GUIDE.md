# CSV Image Import Guide

## Overview
You can now add images to products when importing from CSV. There are two methods:

1. **Image URLs** - Direct links to images online
2. **ZIP File** - Upload images in a ZIP file alongside your CSV

---

## Method 1: Using Image URLs

### How It Works
- Add an `image_url` column to your CSV
- Enter direct links to product images
- Images are downloaded automatically during import

### CSV Format
```csv
name,category,price,description,inventory,sizes,colors,image_url
"Phi Beta Sigma T-Shirt",apparel,19.99,"Classic fraternity tee",100,"S, M, L, XL","Black, White, Navy",https://example.com/images/tshirt.jpg
"Chapter Hat",apparel,24.99,"Embroidered baseball cap",50,"One Size","Black, Navy",https://example.com/images/hat.jpg
"Tumbler",drinkware,14.99,"Insulated travel mug",75,"16oz, 20oz","Black, Burgundy",https://example.com/images/tumbler.jpg
```

### Requirements
- URLs must be publicly accessible
- Common formats: `.jpg`, `.png`, `.gif`, `.webp`
- URLs should be complete (https://example.com/image.jpg)

### Advantages
- ✅ No need to download images separately
- ✅ Automatic image download
- ✅ No ZIP file needed

### Disadvantages
- ❌ URLs must be permanently available
- ❌ Slower import (network-dependent)
- ❌ Image URLs can break over time

---

## Method 2: Using ZIP File with Image Paths

### How It Works
1. Create a folder with your product images
2. ZIP the folder
3. Add an `image_path` column to CSV with file paths
4. Upload both CSV and ZIP together

### Step-by-Step

#### Step 1: Organize Your Images
```
my-products/
├── tshirt.jpg
├── hat.jpg
├── tumbler.jpg
└── polo.jpg
```

Or organize in subfolders:
```
images/
├── apparel/
│   ├── tshirt.jpg
│   ├── hat.jpg
│   └── polo.jpg
├── drinkware/
│   └── tumbler.jpg
└── accessories/
    └── keychain.jpg
```

#### Step 2: Create CSV with image_path
```csv
name,category,price,description,inventory,sizes,colors,image_path
"Phi Beta Sigma T-Shirt",apparel,19.99,"Classic fraternity tee",100,"S, M, L, XL","Black, White, Navy",tshirt.jpg
"Chapter Hat",apparel,24.99,"Embroidered baseball cap",50,"One Size","Black, Navy",hat.jpg
"Tumbler",drinkware,14.99,"Insulated travel mug",75,"16oz, 20oz","Black, Burgundy",tumbler.jpg
"Polo Shirt",apparel,34.99,"Embroidered polo",60,"S, M, L, XL, 2XL","White, Black, Maroon",polo.jpg
```

Or with subdirectories:
```csv
name,category,price,description,inventory,image_path
"Phi Beta Sigma T-Shirt",apparel,19.99,"Classic fraternity tee",100,apparel/tshirt.jpg
"Tumbler",drinkware,14.99,"Insulated travel mug",75,drinkware/tumbler.jpg
```

#### Step 3: Create ZIP File
**Mac/Linux:**
```bash
zip -r products.zip images/
# or with specific folder
zip -r products.zip tshirt.jpg hat.jpg tumbler.jpg
```

**Windows:**
- Right-click folder → Send to → Compressed (zipped) folder
- Or use 7-Zip, WinRAR, etc.

#### Step 4: Upload
1. Go to Admin → Import Products page
2. Select your CSV file
3. Select your ZIP file (labeled "Images ZIP")
4. Click "Import Products"

### CSV Format with Subdirectories
```csv
name,category,price,description,inventory,sizes,colors,image_path
"Phi Beta Sigma T-Shirt",apparel,19.99,"Classic",100,"S, M, L, XL","Black, Navy",apparel/tshirt.jpg
"Tumbler",drinkware,14.99,"Travel mug",75,"16oz, 20oz","Black, Burgundy",drinkware/tumbler.jpg
"Polo Shirt",apparel,34.99,"Professional",60,"S, M, L, XL","White, Black",apparel/polo.jpg
```

### Advantages
- ✅ Faster import (images already local)
- ✅ Organize images in folders
- ✅ Works offline
- ✅ Images won't break from URL changes

### Disadvantages
- ❌ Extra step to create ZIP
- ❌ Need to manage file structure
- ❌ Larger file to upload

---

## Quick Comparison

| Feature | Image URL | ZIP File |
|---------|-----------|----------|
| **Speed** | Slower | Faster |
| **Setup** | Simple | Moderate |
| **Reliability** | Depends on URL | Very Reliable |
| **File Size** | Smaller CSV | Larger ZIP |
| **Best For** | Linking to existing images | Complete control |

---

## Common Image Formats Supported

- `.jpg` / `.jpeg` - Most common
- `.png` - Best for graphics
- `.gif` - Animated images
- `.webp` - Modern format
- `.bmp` - Basic format

---

## File Size Limits

- **CSV File**: Maximum 5MB
- **Images ZIP**: Maximum 50MB

---

## Troubleshooting

### Images Not Showing

**Issue:** Products imported but images missing

**Solutions:**
1. Check image file names match exactly (case-sensitive)
2. Verify file extensions are correct
3. Make sure images are inside ZIP file
4. Try re-uploading with correct paths

### ZIP File Not Reading

**Issue:** "Error extracting images" message

**Solutions:**
1. Make sure file is actually a ZIP (not RAR or 7z)
2. Try creating ZIP from command line:
   ```bash
   zip -r products.zip images/
   ```
3. Check ZIP file isn't corrupted
4. Try smaller ZIP first

### URL Images Failing

**Issue:** Images from URLs not downloading

**Solutions:**
1. Verify URLs are publicly accessible
2. Test URL in browser first
3. Check for HTTPS (preferred)
4. Make sure no special characters in URLs
5. Use shorter timeouts - try different image host

---

## Example: Complete Workflow

### Using ZIP Method (Recommended for Bulk Import)

**1. File Structure:**
```
MyProducts/
├── products.csv
└── images/
    ├── tshirt.jpg
    ├── hat.jpg
    └── tumbler.jpg
```

**2. CSV Content (products.csv):**
```csv
name,category,price,description,inventory,sizes,colors,image_path
"Premium PBS T-Shirt",apparel,24.99,"High quality tee",150,"S, M, L, XL, 2XL","Black, White, Navy, Maroon",images/tshirt.jpg
"Classic Cap",apparel,19.99,"Baseball cap",100,"One Size","Black, Navy, Maroon",images/hat.jpg
"Stainless Tumbler",drinkware,18.99,"Double-wall insulated",75,"16oz, 20oz, 24oz","Black, Silver, White",images/tumbler.jpg
```

**3. Create ZIP:**
```bash
cd MyProducts
zip -r products.zip .
```

**4. Upload:**
- Go to `/pages/boutique/admin/import-products/`
- Upload `products.csv`
- Upload `products.zip`
- Click "Import Products"

**5. Verify:**
- Check admin panel for new products
- Verify images appear on shop page

---

## API Integration

If using the import function programmatically:

```python
from pages.forms_boutique import BoutiqueImportForm

# Create form with files
form = BoutiqueImportForm(
    POST_data,
    FILES={'csv_file': csv_file, 'images_zip': zip_file}
)

if form.is_valid():
    # Parse CSV
    products = form.parse_csv()
    
    # Process images
    images_zip = form.cleaned_data.get('images_zip')
```

---

## Best Practices

✅ **DO:**
- Use descriptive file names
- Organize images in folders
- Test URLs before bulk import
- Keep CSV and images together
- Compress PNG images before uploading

❌ **DON'T:**
- Use spaces in image file names
- Mix image URL and image_path in same CSV
- Upload extremely high-resolution images
- Rely on temporary URLs

---

## Support

For issues with importing:
1. Check the error message on screen
2. Verify CSV format (required columns)
3. Confirm image files exist
4. Check file permissions
5. Try with smaller batch first

---

**Last Updated:** February 5, 2026
**System:** Django 4.2.28
