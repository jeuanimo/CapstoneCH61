 #!/usr/bin/env python
"""
CSV Import Validation Script
Tests CSV import functionality without making database changes
"""

import os
import sys
import csv
import io
from pathlib import Path

# Add the project to the path
sys.path.insert(0, str(Path(__file__).parent))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from pages.forms_boutique import BoutiqueImportForm
from pages.models import Product
from django.core.files.uploadedfile import InMemoryUploadedFile

def test_csv_parsing():
    """Test CSV file parsing without importing"""
    print("\n" + "="*70)
    print("📋 CSV IMPORT VALIDATION TEST")
    print("="*70)
    
    csv_path = 'TEST_PRODUCTS.csv'
    
    if not os.path.exists(csv_path):
        print(f"❌ Test CSV file not found: {csv_path}")
        return False
    
    print(f"\n✅ Found test CSV file: {csv_path}")
    
    # Read and validate CSV
    with open(csv_path, 'rb') as f:
        csv_content = f.read()
    
    # Create uploaded file object
    csv_file = InMemoryUploadedFile(
        io.BytesIO(csv_content),
        field_name='csv_file',
        name='TEST_PRODUCTS.csv',
        content_type='text/csv',
        size=len(csv_content),
        charset='utf-8'
    )
    
    # Create form
    form = BoutiqueImportForm({'csv_file': csv_file}, {'csv_file': csv_file})
    
    print("\n📊 Validation Results:")
    print("-" * 70)
    
    # Check if form is valid
    if form.is_valid():
        print("✅ CSV format is valid")
        
        try:
            # Parse CSV
            products_data = form.parse_csv()
            print(f"✅ CSV parsed successfully - Found {len(products_data)} products\n")
            
            # Display product details
            print("📦 Products Found:")
            print("-" * 70)
            for i, product in enumerate(products_data, 1):
                print(f"\n{i}. {product['name']}")
                print(f"   Category: {product['category']}")
                print(f"   Price: ${product['price']:.2f}")
                print(f"   Inventory: {product['inventory']}")
                print(f"   Description: {product['description'][:50]}..." if len(product['description']) > 50 else f"   Description: {product['description']}")
                print(f"   Sizes: {product['sizes']}")
                print(f"   Colors: {product['colors']}")
                if product.get('image_url'):
                    print(f"   Image URL: {product['image_url']}")
                if product.get('image_path'):
                    print(f"   Image Path: {product['image_path']}")
            
            print("\n" + "="*70)
            print("✅ ALL VALIDATION TESTS PASSED!")
            print("="*70)
            print("\n📝 Next Steps:")
            print("1. Go to: http://localhost:8000/pages/boutique/admin/import-products/")
            print("2. Upload TEST_PRODUCTS.csv file")
            print("3. Click 'Import Products'")
            print("4. Verify products appear on shop page: /pages/boutique/")
            print("\n")
            
            return True
            
        except Exception as e:
            print(f"❌ Error parsing CSV: {str(e)}")
            return False
    else:
        print("❌ CSV validation failed:")
        for field, errors in form.errors.items():
            for error in errors:
                print(f"   - {field}: {error}")
        return False


def check_existing_products():
    """Check if test products already exist"""
    print("\n📊 Database Status:")
    print("-" * 70)
    total_products = Product.objects.count()
    print(f"Total products in database: {total_products}")
    
    test_product_names = [
        "Phi Beta Sigma Classic T-Shirt",
        "Sigma Beta Club Polo",
        "Chapter Embroidered Cap",
        "Stainless Steel Tumbler",
        "Fraternity Hoodie",
        "Logo Backpack"
    ]
    
    existing = []
    for name in test_product_names:
        if Product.objects.filter(name=name).exists():
            existing.append(name)
    
    if existing:
        print(f"\n⚠️  Found {len(existing)} existing products:")
        for name in existing:
            print(f"   - {name}")
        print("\n💡 Tip: To reimport, delete these products first or change their names in CSV")
    else:
        print("\n✅ Test products not found in database - ready for import!")


def test_image_urls():
    """Test if image URLs are accessible"""
    print("\n\n🖼️  IMAGE URL VALIDATION")
    print("="*70)
    
    try:
        import requests
    except ImportError:
        print("⚠️  requests library not installed - skipping URL validation")
        print("   Install with: pip install requests")
        return True
    
    # Read CSV and test URLs
    with open('TEST_PRODUCTS.csv', 'r') as f:
        reader = csv.DictReader(f)
        products = list(reader)
    
    print(f"\nTesting {len(products)} product image URLs...\n")
    
    all_valid = True
    for i, product in enumerate(products, 1):
        image_url = product.get('image_url', '').strip()
        if image_url:
            print(f"{i}. {product['name']}")
            print(f"   URL: {image_url}")
            try:
                response = requests.head(image_url, timeout=5)
                if response.status_code == 200:
                    print(f"   ✅ Accessible (Status: {response.status_code})")
                else:
                    print(f"   ⚠️  Returned status {response.status_code}")
                    all_valid = False
            except Exception as e:
                print(f"   ❌ Error accessing URL: {str(e)}")
                all_valid = False
            print()
    
    if all_valid:
        print("✅ All image URLs are accessible!")
    else:
        print("⚠️  Some URLs may not be accessible - check them manually in browser")
    
    return all_valid


if __name__ == '__main__':
    print("\n🚀 Starting CSV Import Validation...\n")
    
    # Run tests
    csv_valid = test_csv_parsing()
    check_existing_products()
    test_image_urls()
    
    print("\n💡 WHAT TO DO NEXT:")
    print("="*70)
    if csv_valid:
        print("""
1. Start the Django server:
   python manage.py runserver

2. Go to admin import page:
   http://localhost:8000/pages/boutique/admin/import-products/

3. Upload TEST_PRODUCTS.csv

4. Click 'Import Products'

5. Verify on shop page:
   http://localhost:8000/pages/boutique/

6. Check that:
   ✅ All 6 products appear
   ✅ Images load correctly
   ✅ Product details display properly
   ✅ Sizes and colors show
   ✅ Prices are correct
        """)
    else:
        print("Fix the CSV errors above before proceeding.")
    
    print("="*70 + "\n")
