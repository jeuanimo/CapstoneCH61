# Phi Beta Sigma Chapter Boutique - Getting Started Guide

## Quick Access

**Shop URL**: `http://yourdomain.com/pages/boutique/`

**Admin Import**: `http://yourdomain.com/pages/boutique/admin/import-products/` (Staff only)

## Setting Up Your First Products

### Option 1: Import via CSV (Recommended)

1. **Prepare your CSV file** with the following columns:
   ```
   name,category,price,description,inventory,sizes,colors
   ```

2. **Visit Admin Import Page**:
   - Go to `/pages/boutique/admin/import-products/`
   - Log in if needed (must be staff user)
   - Upload your CSV file (max 5MB)

3. **Verify Import**:
   - Check `/admin/pages/product/` to see all products
   - Edit if needed in the Django admin

### Option 2: Manual Admin Entry

1. **Go to Django Admin**: `/admin/pages/product/`
2. **Click "Add Product"**
3. **Fill in the fields**:
   - Name
   - Description
   - Category (apparel, accessories, drinkware, other)
   - Price
   - Inventory quantity
   - Sizes (comma-separated, e.g., "S, M, L, XL")
   - Colors (comma-separated, e.g., "Black, White, Navy")
   - Upload product image
4. **Save**

## Sample CSV for Quick Setup

Create a file named `products.csv`:

```csv
name,category,price,description,inventory,sizes,colors
"Phi Beta Sigma Classic T-Shirt",apparel,19.99,"Classic crew neck t-shirt with embroidered logo",150,"XS, S, M, L, XL, 2XL, 3XL","Black, White, Navy, Maroon"
"Polo Shirt",apparel,39.99,"Premium embroidered polo shirt for chapter events",100,"S, M, L, XL, 2XL","Navy, White, Black"
"Baseball Cap",apparel,24.99,"Classic baseball cap with embroidered crest",200,"One Size","Navy, Black, White"
"Hoodie",apparel,49.99,"Comfortable fleece-lined hoodie perfect for cold weather",75,"S, M, L, XL, 2XL","Black, Navy, Maroon, Gray"
"Insulated Tumbler",drinkware,14.99,"20oz insulated stainless steel tumbler keeps drinks hot or cold",500,"20oz","Black, Navy, Silver"
"Coffee Mug",drinkware,12.99,"11oz ceramic mug perfect for morning coffee",300,"One Size","White, Black, Navy"
"Embroidered Cap",accessories,18.99,"Adjustable baseball cap with embroidered logo",150,"One Size","Navy, Black"
"Fraternity Backpack",accessories,59.99,"Durable backpack with multiple compartments",50,"One Size","Black, Navy, Maroon"
"Phone Stand",accessories,9.99,"Desk phone stand with custom design",500,"One Size","Black, Silver"
```

## User Features

### Shopping Cart
- Add products with selected size/color
- View cart with item details
- Update quantities or remove items
- Cart persists across sessions

### Checkout
- Enter shipping information
- See order summary
- Proceed to secure payment

### Payment
- Secure Stripe payment processing
- Card information handled by Stripe (PCI compliant)
- Order confirmation page
- Order history tracking

### Order History
- View all past orders
- Check order status
- See shipping details

## Admin Features

### Product Management
- Create, edit, delete products
- Manage inventory levels
- Add product descriptions and images
- Set sizes and color options

### CSV Bulk Import
- Upload multiple products at once
- Automatic validation
- Row-level error reporting
- Duplicate prevention (same product name)

### Order Management
- View all customer orders
- Track order status (pending, completed, shipped, delivered, cancelled)
- Update order status
- View customer shipping details
- Check payment intent ID

### Reporting
- Admin dashboard shows total products
- Track orders by status
- Monitor inventory levels

## Product Categories

The system supports four merchandise categories:

1. **Apparel** - Clothing items (shirts, hoodies, hats)
2. **Accessories** - Non-clothing items (bags, phone stands, etc.)
3. **Drinkware** - Cups, tumblers, mugs
4. **Other** - Miscellaneous items

## Size and Color Options

### Configuring Variants
- Enter sizes as comma-separated values: `XS, S, M, L, XL, 2XL`
- Enter colors as comma-separated values: `Black, Navy, White, Maroon`
- Display as customer dropdowns on product pages

### Example Configurations
```
Apparel:
  Sizes: XS, S, M, L, XL, 2XL, 3XL
  Colors: Black, Navy, White, Maroon, Gray, Burgundy

Drinkware:
  Sizes: 16oz, 20oz, 24oz
  Colors: Black, Navy, Silver, White

Accessories:
  Sizes: One Size
  Colors: Black, Navy, White, Maroon
```

## Stripe Payment Integration

### Setup (Admin)
1. Add STRIPE_PUBLIC_KEY to Django settings
2. Add STRIPE_SECRET_KEY to Django settings
3. Payment processing is automatic

### Payment Flow
1. Customer adds items to cart
2. Proceeds to checkout
3. Enters shipping information
4. Enters payment details via Stripe
5. Order created with status "completed"
6. Confirmation page shown

### Payment Intent Storage
- Stripe payment intent ID stored with order
- Can be used to track payment status
- Webhook support available for payment status updates

## URL Endpoints

### Customer Routes
```
/pages/boutique/                              - Shop home (list all products)
/pages/boutique/?category=apparel             - Filter by category
/pages/boutique/product/<id>/                 - View product details
/pages/boutique/add-to-cart/<id>/             - Add to cart (POST)
/pages/boutique/cart/                         - View shopping cart
/pages/boutique/cart/update/<item_id>/        - Update cart item (POST)
/pages/boutique/cart/remove/<item_id>/        - Remove from cart (POST)
/pages/boutique/checkout/                     - Checkout page (requires login)
/pages/boutique/payment/<order_id>/           - Stripe payment (requires login)
/pages/boutique/payment-success/<order_id>/   - Order confirmation
/pages/boutique/orders/                       - Order history (requires login)
```

### Admin Routes
```
/pages/boutique/admin/import-products/        - CSV import (staff only)
/admin/pages/product/                         - Product management
/admin/pages/order/                           - Order management
/admin/pages/cart/                            - Cart management
```

## Database Structure

### Models

**Product**
- name, description, category, price
- inventory (stock quantity)
- sizes, colors (variant options)
- image, created_at, updated_at

**Cart**
- user (OneToOne)
- created_at, updated_at
- Methods: get_total_price(), get_total_items()

**CartItem**
- cart, product, quantity
- size, color (variant selection)
- Unique constraint: (cart, product, size, color)

**Order**
- user, status (pending/completed/shipped/delivered/cancelled)
- total_price, stripe_payment_intent
- email, address, city, state, zip_code
- created_at, updated_at
- Methods: get_total_items(), get_total_price()

**OrderItem**
- order, product, quantity
- size, color, price (snapshot of purchase price)
- Methods: get_total_price()

## Troubleshooting

### "Page not found" for /boutique/
- **Solution**: URLs are under `/pages/` prefix
- **Use**: `/pages/boutique/` instead of `/boutique/`

### CSV Import showing errors
- **Check**: Required columns (name, category, price) present
- **Check**: Category names match allowed values exactly
- **Check**: Price is a valid number
- **Check**: File size under 5MB

### Cart not showing items
- **Check**: User must be logged in
- **Check**: Items must be in "pending" status
- **Check**: Quantities must be positive

### Stripe payment failing
- **Check**: STRIPE_PUBLIC_KEY and STRIPE_SECRET_KEY configured
- **Check**: Card details entered correctly
- **Check**: Sufficient funds available

## Customization

### Styling
- All templates use Bootstrap 5 + custom CSS
- Dark blue primary color: #1a1a2e
- Green accent: #28a745
- Easily customizable through inline styles

### Product Images
- Images stored in MEDIA_ROOT
- Supported formats: JPG, PNG, GIF, WebP
- Recommended size: 600x600px or larger

### Email Notifications
- Currently sends order confirmation to user email
- Customizable in views.py payment_success()
- Can integrate with email backend

## Performance Tips

1. **Optimize images** before uploading (reduce file size)
2. **Use CSV import** for bulk product updates
3. **Archive old orders** periodically
4. **Cache product list** for high-traffic sites
5. **Monitor inventory** levels regularly

## Security Features

✅ CSRF protection on all forms
✅ User authentication required for checkout
✅ Inventory validation (no overselling)
✅ Stripe handles sensitive payment data
✅ ZIP code validation
✅ Staff-only admin endpoints
✅ Open redirect prevention

## Future Enhancements

- [ ] Real-time shipping rate calculation
- [ ] Automatic tax calculation
- [ ] Email order notifications
- [ ] Low stock alerts
- [ ] Customer reviews and ratings
- [ ] Discount codes and coupons
- [ ] Wishlist functionality
- [ ] Product search and advanced filtering
- [ ] Admin sales dashboard
- [ ] Inventory analytics

## Support

For issues or questions:
1. Check logs: `tail -f /path/to/django.log`
2. Review admin interface: `/admin/`
3. Check database: Django admin shell
4. Review code: See BOUTIQUE_IMPLEMENTATION.md

---

**Version**: 1.0
**Last Updated**: February 5, 2026
**Maintained By**: Development Team
