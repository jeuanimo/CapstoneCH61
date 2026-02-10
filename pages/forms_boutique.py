from django import forms
from django.core.exceptions import ValidationError
from .models import Product, Order, CartItem
import csv
import io
import os
import re
from django.core.files.storage import default_storage


class BoutiqueImportForm(forms.Form):
    """Form for importing merchandise products from CSV with image support"""
    csv_file = forms.FileField(
        label='CSV File',
        help_text='Upload a CSV file with columns: name, category, price, description, inventory, sizes, colors. Include image_path or image_url for images.',
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.csv'
        })
    )
    
    # Optional: Allow uploading a ZIP with images
    images_zip = forms.FileField(
        label='Images ZIP (Optional)',
        help_text='Optional: ZIP file containing product images. File names should match "image_path" column in CSV.',
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.zip'
        })
    )
    
    def clean(self):
        """Validate both CSV and optional ZIP file"""
        cleaned_data = super().clean()
        
        csv_file = cleaned_data.get('csv_file')
        images_zip = cleaned_data.get('images_zip')
        
        if not csv_file:
            raise ValidationError('CSV file is required')
        
        if not csv_file.name.endswith('.csv'):
            raise ValidationError('File must be a CSV file')
        
        if csv_file.size > 5 * 1024 * 1024:  # 5MB limit
            raise ValidationError('CSV file size must not exceed 5MB')
        
        if images_zip:
            if not images_zip.name.endswith('.zip'):
                raise ValidationError('Images file must be a ZIP file')
            if images_zip.size > 50 * 1024 * 1024:  # 50MB limit for images
                raise ValidationError('Images ZIP file size must not exceed 50MB')
        
        return cleaned_data
    
    def parse_csv(self):
        """Parse CSV file and return list of product data. Supports both standard format and Shopify exports."""
        csv_file = self.cleaned_data['csv_file']
        products_data = []
        
        try:
            # Reset file position to beginning
            csv_file.seek(0)
            
            # Handle both text and binary file modes
            if isinstance(csv_file, io.BytesIO) or hasattr(csv_file, 'read'):
                file_content = csv_file.read()
                if isinstance(file_content, bytes):
                    file_content = file_content.decode('utf-8')
            else:
                file_content = csv_file.read().decode('utf-8')
            
            # Remove BOM if present (Excel adds this)
            if file_content.startswith('\ufeff'):
                file_content = file_content[1:]
            
            # Parse CSV
            csv_reader = csv.DictReader(io.StringIO(file_content))
            
            if not csv_reader.fieldnames:
                raise ValidationError('CSV file is empty or has no header row')
            
            # Normalize column names to lowercase for case-insensitive matching
            fieldnames_lower = {f.lower().strip(): f for f in csv_reader.fieldnames}
            
            # Detect CSV format: Shopify or Standard
            is_shopify = 'title' in fieldnames_lower and 'variant price' in fieldnames_lower
            
            if is_shopify:
                # Shopify CSV format mapping
                return self._parse_shopify_csv(csv_reader)
            else:
                # Standard format - check required fields
                required_fields = ['name', 'category', 'price']
                missing_fields = [f for f in required_fields if f not in fieldnames_lower]
                
                if missing_fields:
                    actual_columns = list(csv_reader.fieldnames)
                    raise ValidationError(
                        f'CSV must contain these columns: {", ".join(missing_fields)}. '
                        f'Found columns: {", ".join(actual_columns)}'
                    )
                
                return self._parse_standard_csv(csv_reader)
        
        except csv.Error as e:
            raise ValidationError(f'CSV parsing error: {str(e)}')
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f'Error processing CSV file: {str(e)}')
    
    def _parse_shopify_csv(self, csv_reader):
        """Parse Shopify-format CSV export"""
        products_data = []
        seen_handles = set()  # Track unique products (Shopify has multiple rows per product for variants)
        
        valid_categories = ['apparel', 'accessories', 'drinkware', 'other']
        
        for row_num, row in enumerate(csv_reader, start=2):
            try:
                handle = row.get('Handle', '').strip()
                
                # Skip variant rows (same handle = same product, different variant)
                if handle in seen_handles:
                    continue
                seen_handles.add(handle)
                
                # Map Shopify columns to our fields
                name = row.get('Title', '').strip()
                if not name:
                    continue  # Skip rows without a title
                
                # Map Shopify "Type" to category, default to 'other'
                shopify_type = row.get('Type', '').strip().lower()
                category = 'other'
                if shopify_type:
                    # Try to match Shopify type to our categories
                    if any(word in shopify_type for word in ['shirt', 'apparel', 'clothing', 'jacket', 'hoodie', 'polo', 'tee']):
                        category = 'apparel'
                    elif any(word in shopify_type for word in ['accessory', 'accessories', 'hat', 'cap', 'bag', 'pin', 'lanyard']):
                        category = 'accessories'
                    elif any(word in shopify_type for word in ['drinkware', 'mug', 'cup', 'tumbler', 'bottle', 'glass']):
                        category = 'drinkware'
                
                # Get price from Variant Price
                try:
                    price = float(row.get('Variant Price', 0) or 0)
                    if price < 0:
                        price = 0
                except (ValueError, TypeError):
                    price = 0
                
                # Get inventory from Variant Inventory Qty
                try:
                    inventory = int(row.get('Variant Inventory Qty', 0) or 0)
                    if inventory < 0:
                        inventory = 0
                except (ValueError, TypeError):
                    inventory = 0
                
                # Get description from Body (HTML) - strip basic HTML tags
                description = row.get('Body (HTML)', '').strip()
                # Simple HTML tag removal
                description = re.sub(r'<[^>]+>', '', description)
                
                # Get image URL
                image_url = row.get('Image Src', '').strip()
                
                # Get sizes from Option1 if it's "Size"
                sizes = ''
                if row.get('Option1 Name', '').strip().lower() == 'size':
                    sizes = row.get('Option1 Value', '').strip()
                elif row.get('Option2 Name', '').strip().lower() == 'size':
                    sizes = row.get('Option2 Value', '').strip()
                elif row.get('Option3 Name', '').strip().lower() == 'size':
                    sizes = row.get('Option3 Value', '').strip()
                
                # Get colors from Options
                colors = ''
                if row.get('Option1 Name', '').strip().lower() == 'color':
                    colors = row.get('Option1 Value', '').strip()
                elif row.get('Option2 Name', '').strip().lower() == 'color':
                    colors = row.get('Option2 Value', '').strip()
                elif row.get('Option3 Name', '').strip().lower() == 'color':
                    colors = row.get('Option3 Value', '').strip()
                
                products_data.append({
                    'name': name,
                    'category': category,
                    'price': price,
                    'description': description[:1000] if description else '',  # Limit description length
                    'inventory': inventory,
                    'sizes': sizes,
                    'colors': colors,
                    'image_url': image_url,
                    'image_path': '',
                })
            
            except Exception as e:
                raise ValidationError(f'Row {row_num}: {str(e)}')
        
        if not products_data:
            raise ValidationError('CSV file contains no valid product data')
        
        return products_data
    
    def _parse_standard_csv(self, csv_reader):
        """Parse standard CSV format with forgiving error handling"""
        products_data = []
        valid_categories = ['apparel', 'accessories', 'drinkware', 'other']
        skipped_rows = []
        
        for row_num, row in enumerate(csv_reader, start=2):
            try:
                # Create lowercase key mapping for this row
                row_lower = {k.lower().strip(): v for k, v in row.items()}
                
                # Name is the only truly required field
                name = row_lower.get('name', '').strip()
                if not name:
                    skipped_rows.append(f'Row {row_num}: No product name')
                    continue  # Skip row instead of failing
                
                # Default category to 'other' if invalid or missing
                category = row_lower.get('category', 'other').strip().lower()
                if category not in valid_categories:
                    category = 'other'  # Default instead of error
                
                # Default price to 0 if invalid
                try:
                    price_str = row_lower.get('price', '0') or '0'
                    price = float(price_str.replace('$', '').replace(',', '').strip())
                    if price < 0:
                        price = 0
                except (ValueError, TypeError):
                    price = 0  # Default instead of error
                
                try:
                    inventory = int(row_lower.get('inventory', 0) or 0)
                    if inventory < 0:
                        inventory = 0
                except (ValueError, TypeError):
                    inventory = 0
                
                # Support both image_url (download from URL) and image_path (from ZIP)
                image_url = row_lower.get('image_url', '').strip()
                image_path = row_lower.get('image_path', '').strip()
                
                products_data.append({
                    'name': name,
                    'category': category,
                    'price': price,
                    'description': row_lower.get('description', '').strip(),
                    'inventory': inventory,
                    'sizes': row_lower.get('sizes', '').strip(),
                    'colors': row_lower.get('colors', '').strip(),
                    'image_url': image_url,
                    'image_path': image_path,
                })
            
            except Exception as e:
                # Skip problematic rows instead of failing entire import
                skipped_rows.append(f'Row {row_num}: {str(e)}')
                continue
        
        if not products_data:
            if skipped_rows:
                raise ValidationError(f'CSV file contains no valid product data. Issues: {"; ".join(skipped_rows[:5])}')
            raise ValidationError('CSV file contains no valid product data')
        
        return products_data


class ProductForm(forms.ModelForm):
    """Form for creating/editing products"""
    
    # Multi-select fields for standard sizes and colors
    sizes_multi = forms.MultipleChoiceField(
        choices=Product.SIZE_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
        label='Sizes',
        help_text='Select available sizes for this product'
    )
    
    colors_multi = forms.MultipleChoiceField(
        choices=Product.COLOR_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
        label='Colors',
        help_text='Select available colors for this product'
    )
    
    class Meta:
        model = Product
        fields = ['name', 'description', 'category', 'price', 'image', 'inventory', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Product name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Product description'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'inventory': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Pre-populate multi-select fields from existing comma-separated values
        if self.instance and self.instance.pk:
            self.fields['sizes_multi'].initial = self.instance.get_sizes_list()
            self.fields['colors_multi'].initial = self.instance.get_colors_list()
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        # Convert multi-select lists back to comma-separated strings
        sizes_list = self.cleaned_data.get('sizes_multi', [])
        colors_list = self.cleaned_data.get('colors_multi', [])
        instance.sizes = ','.join(sizes_list)
        instance.colors = ','.join(colors_list)
        if commit:
            instance.save()
        return instance


class CheckoutForm(forms.ModelForm):
    """Form for checkout (supports authenticated and guest users)"""
    class Meta:
        model = Order
        fields = ['full_name', 'email', 'phone', 'address', 'city', 'state', 'zip_code']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email address'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone number (optional)'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Street address'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State'}),
            'zip_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ZIP code'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.is_guest = kwargs.pop('is_guest', False)
        super().__init__(*args, **kwargs)
        if self.is_guest:
            self.fields['full_name'].required = True
            self.fields['email'].required = True
    
    def clean_zip_code(self):
        """Validate ZIP code format"""
        zip_code = self.cleaned_data.get('zip_code', '').strip()
        if zip_code and len(zip_code) < 5:
            raise ValidationError('ZIP code must be at least 5 characters')
        return zip_code
