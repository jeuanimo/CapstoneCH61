# Boutique Admin Quick Reference

## Permission Levels

```
ROLE              | is_staff | is_officer | Can Add/Edit/Delete Products | Can Import CSV
Admin             | ✅       | N/A        | ✅ Yes                       | ✅ Yes
Officer           | ❌       | ✅         | ✅ Yes                       | ✅ Yes
Regular Member    | ❌       | ❌         | ❌ No (can only buy)         | ❌ No
```

## Admin URLs

| Task | URL | Access |
|------|-----|--------|
| Shop Home | `/pages/boutique/` | Everyone |
| Add Product | `/pages/boutique/admin/add-product/` | Staff + Officers |
| Edit Product | `/pages/boutique/admin/edit-product/<id>/` | Staff + Officers |
| Delete Product | `/pages/boutique/admin/delete-product/<id>/` | Staff + Officers |
| Import CSV | `/pages/boutique/admin/import-products/` | Staff + Officers |
| Manage Members | `/admin/pages/memberprofile/` | Django Staff Only |
| Manage Products | `/admin/pages/product/` | Django Staff Only |

## Quick Setup: Make Someone an Officer

1. Go to `/admin/pages/memberprofile/`
2. Click on member name
3. Scroll to "Admin Privileges" section
4. Check "Is officer with admin privileges?"
5. Click Save

## Quick Setup: Add a Product

1. Go to `/pages/boutique/`
2. Click "Add Product" button (top of page)
3. Fill form:
   - Name: "Phi Beta Sigma T-Shirt"
   - Description: "Our fraternity t-shirt"
   - Category: "Apparel"
   - Price: "19.99"
   - Inventory: "100"
   - Sizes: "S,M,L,XL"
   - Colors: "Black,White,Navy"
   - Image: Upload image file
4. Click "Save Product"

## Quick Setup: Import Products via CSV

1. Create CSV file with headers:
   ```
   name,description,category,price,inventory,sizes,colors
   ```

2. Example row:
   ```
   Phi Beta Sigma Hoodie,Cotton hoodie with logo,Apparel,49.99,50,S;M;L;XL;XXL,Black;White
   ```

3. Go to `/pages/boutique/admin/import-products/`
4. Upload file (max 5MB)
5. Click "Import"

## Features at a Glance

- **Add Products**: Create new merchandise items
- **Edit Products**: Modify prices, inventory, details
- **Delete Products**: Remove products with confirmation
- **Bulk Import**: Upload 100+ products at once via CSV
- **Inventory Management**: Track stock levels
- **Variants**: Add sizes and colors to products
- **Images**: Upload product photos
- **Categories**: Organize merchandise by category

## Common Tasks

### Change Product Price
1. Click "Edit" on product
2. Change price field
3. Click "Save Product"

### Change Inventory
- **Via Web**: Click "Edit" → Change inventory → Save
- **Via Admin**: `/admin/pages/product/` → Inline edit

### View All Products
- Shop: `/pages/boutique/`
- Admin: `/admin/pages/product/`

### View Officer List
- `/admin/pages/memberprofile/?is_officer__exact=1`

### Remove Officer Status
1. Go to `/admin/pages/memberprofile/`
2. Find officer
3. Uncheck "Is officer"
4. Click Save

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Can't see admin buttons | Check if logged in as staff/officer |
| Import failing | Check CSV format, ensure headers match |
| Image not uploading | Check file format (JPG, PNG) and size |
| Product not deleting | Try from Django admin if web delete fails |
| Permission denied | Verify is_officer checked or is_staff=True |

## Code Permissions

All admin views check:
```python
@user_passes_test(lambda u: u.is_staff or (hasattr(u, 'memberprofile') and u.memberprofile.is_officer))
```

This allows both:
- Staff members (`user.is_staff == True`)
- Officers (`memberprofile.is_officer == True`)

