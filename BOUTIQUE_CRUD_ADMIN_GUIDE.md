# Boutique Admin & Officer CRUD Management System

## Overview

The boutique now has a complete CRUD (Create, Read, Update, Delete) system with proper permission controls for admin staff and chapter officers.

## Key Features

### 1. Officer Status Management
- **New Field**: `is_officer` boolean field added to `MemberProfile` model
- Admins can mark members as officers in the Django admin panel
- Officers get the same boutique management permissions as staff

### 2. Permission Controls

All boutique admin functions require one of the following:
- `user.is_staff` (Django staff member)
- `user.memberprofile.is_officer` (Chapter officer)

Protected views:
- `import_products` - CSV bulk import of products
- `add_product` - Create new product
- `edit_product` - Modify existing product
- `delete_product` - Remove product from boutique

### 3. CRUD Operations

#### Create Product
- **URL**: `/pages/boutique/admin/add-product/`
- **View**: `add_product()`
- **Template**: `product_form.html`
- **Features**:
  - Product name, description, category, price, inventory
  - Size variants (comma-separated: S,M,L,XL)
  - Color variants (comma-separated: Black,White,Blue)
  - Product image upload

#### Read Product
- **URL**: `/pages/boutique/product/<id>/`
- **View**: `product_detail()`
- **Template**: `product_detail.html`
- **Features**:
  - View full product details
  - See inventory status
  - Admin buttons visible to staff/officers

#### Update Product
- **URL**: `/pages/boutique/admin/edit-product/<id>/`
- **View**: `edit_product()`
- **Template**: `product_form.html`
- **Features**:
  - Edit all product fields
  - Update image
  - Modify variants
  - Change pricing and inventory

#### Delete Product
- **URL**: `/pages/boutique/admin/delete-product/<id>/`
- **View**: `delete_product()`
- **Template**: `delete_product_confirm.html`
- **Features**:
  - Confirmation screen with product preview
  - One-click deletion after confirmation
  - Prevents accidental deletion

### 4. Bulk Operations

#### CSV Import
- **URL**: `/pages/boutique/admin/import-products/`
- **View**: `import_products()`
- **Template**: `import_products.html`
- **Features**:
  - Upload CSV files (max 5MB)
  - Validate data before import
  - Row-level error reporting
  - Prevent duplicate products
  - Create multiple products in bulk

**CSV Format**:
```
name,description,category,price,inventory,sizes,colors
Phi Beta Sigma T-Shirt,Comfortable cotton tee,apparel,19.99,100,S;M;L;XL,Black;White;Navy
Sigma Beta Club Hoodie,Warm hoodie with logo,apparel,49.99,50,S;M;L;XL;XXL,Black;White
Fraternity Hat,Baseball cap,accessories,14.99,75,,Black;White;Navy
```

## Admin Interface

### Dashboard Controls
Both shop page and individual product pages show admin controls for staff/officers:

1. **Shop Home** (`/pages/boutique/`)
   - "Add Product" button - Creates new product
   - "Import CSV" button - Bulk product upload
   - Edit/Delete buttons on each product card

2. **Product Detail** (`/pages/boutique/product/<id>/`)
   - Edit button - Modify product
   - Delete button - Remove product

### Django Admin
Access via `/admin/pages/memberprofile/`

**Member Profile Admin**:
- List view includes `is_officer` checkbox for quick toggling
- Filter members by officer status
- Edit individual member's officer status
- Bulk edit officer status in list view

**Product Admin**:
- List view with name, category, price, inventory
- Inline editing of price and inventory
- Date hierarchy for browsing by creation date
- Comprehensive search and filtering
- Fieldsets for organized editing

## Setup Instructions

### For Django Admin
1. Go to Django admin: `/admin/`
2. Navigate to Member Profiles
3. Find the member to promote to officer
4. Check the "Is officer" checkbox under "Admin Privileges"
5. Save

### For Users
Officers can:
1. Access the shop at `/pages/boutique/`
2. Click "Add Product" to create new items
3. Click "Import CSV" to bulk upload products
4. Click "Edit" on any product to modify it
5. Click "Delete" on any product to remove it

## Security Considerations

- All admin views require login (`@login_required`)
- All CRUD operations require staff or officer status (`@user_passes_test`)
- Delete operations require confirmation page
- CSV import validates all data before processing
- Images are stored in secure location

## Database Changes

### Migration: `0017_memberprofile_is_officer`
- Adds `is_officer` boolean field to `MemberProfile` model
- Default value: `False`
- Allows quick filtering in admin interface

## Code Changes Summary

### Models (`pages/models.py`)
- Added `is_officer` field to `MemberProfile`

### Views (`pages/views.py`)
- Updated `import_products` - Allow officers
- Added `add_product` - Create new product
- Added `edit_product` - Modify product
- Added `delete_product` - Remove product

### Admin (`pages/admin.py`)
- Updated `MemberProfileAdmin` - Added is_officer field and filtering
- Enhanced `ProductAdmin` - Better list view, inline editing, date hierarchy

### URLs (`pages/urls.py`)
- Added `/pages/boutique/admin/add-product/`
- Added `/pages/boutique/admin/edit-product/<id>/`
- Added `/pages/boutique/admin/delete-product/<id>/`

### Templates
- Created `product_form.html` - Form for add/edit product
- Created `delete_product_confirm.html` - Confirmation page
- Updated `shop.html` - Added admin controls and edit/delete buttons
- Updated `product_detail.html` - Added edit/delete buttons

## Testing Checklist

- [ ] Can staff members access admin functions
- [ ] Can officers access admin functions  
- [ ] Regular members cannot see admin buttons
- [ ] Can create a product with all fields
- [ ] Can edit product and save changes
- [ ] Can delete product with confirmation
- [ ] Can import products via CSV
- [ ] CSV validation catches errors
- [ ] Duplicate products are not created on import
- [ ] Product variants (sizes/colors) display correctly
- [ ] Admin controls visible on shop page for staff/officers
- [ ] Admin controls visible on product detail page
- [ ] Edit/delete buttons don't appear for regular members
- [ ] is_officer field toggles in Django admin
- [ ] Officer filtering works in admin interface

## Troubleshooting

### "You don't have permission to access this page"
- Check if user is staff or has is_officer checked
- Verify user.is_staff or user.memberprofile.is_officer

### Admin buttons not appearing
- Ensure user is logged in
- Check if user.is_staff or user.memberprofile.is_officer
- Clear browser cache and reload

### CSV import failing
- Verify CSV format with correct headers
- Check for special characters in product names
- Ensure price field is numeric
- Check file size under 5MB

### Product not deleting
- Check database permissions
- Verify user is staff or officer
- Try deleting from Django admin if web delete fails

