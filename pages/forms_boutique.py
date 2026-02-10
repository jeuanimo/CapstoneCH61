from django import forms
from django.core.exceptions import ValidationError
from .models import Product, Order, CartItem
import csv
import io
import os
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
        """Parse CSV file and return list of product data"""
        csv_file = self.cleaned_data['csv_file']
        products_data = []
        
        try:
            # Handle both text and binary file modes
            if isinstance(csv_file, io.BytesIO) or hasattr(csv_file, 'read'):
                file_content = csv_file.read()
                if isinstance(file_content, bytes):
                    file_content = file_content.decode('utf-8')
            else:
                file_content = csv_file.read().decode('utf-8')
            
            # Parse CSV
            csv_reader = csv.DictReader(io.StringIO(file_content))
            
            if not csv_reader.fieldnames:
                raise ValidationError('CSV file is empty')
            
            required_fields = ['name', 'category', 'price']
            missing_fields = [f for f in required_fields if f not in csv_reader.fieldnames]
            
            if missing_fields:
                raise ValidationError(f'CSV must contain these columns: {", ".join(missing_fields)}')
            
            for row_num, row in enumerate(csv_reader, start=2):
                try:
                    # Validate required fields
                    name = row.get('name', '').strip()
                    if not name:
                        raise ValidationError(f'Row {row_num}: Product name is required')
                    
                    category = row.get('category', 'other').strip().lower()
                    valid_categories = ['apparel', 'accessories', 'drinkware', 'other']
                    if category not in valid_categories:
                        raise ValidationError(
                            f'Row {row_num}: Invalid category "{category}". Must be one of: {", ".join(valid_categories)}'
                        )
                    
                    try:
                        price = float(row.get('price', 0))
                        if price < 0:
                            raise ValueError
                    except (ValueError, TypeError):
                        raise ValidationError(f'Row {row_num}: Price must be a valid number')
                    
                    inventory = int(row.get('inventory', 0))
                    if inventory < 0:
                        raise ValidationError(f'Row {row_num}: Inventory must be a positive number')
                    
                    # Support both image_url (download from URL) and image_path (from ZIP)
                    image_url = row.get('image_url', '').strip()
                    image_path = row.get('image_path', '').strip()
                    
                    products_data.append({
                        'name': name,
                        'category': category,
                        'price': price,
                        'description': row.get('description', '').strip(),
                        'inventory': inventory,
                        'sizes': row.get('sizes', '').strip(),
                        'colors': row.get('colors', '').strip(),
                        'image_url': image_url,
                        'image_path': image_path,
                    })
                
                except ValidationError as e:
                    raise e
                except Exception as e:
                    raise ValidationError(f'Row {row_num}: {str(e)}')
            
            if not products_data:
                raise ValidationError('CSV file contains no valid product data')
            
            return products_data
        
        except csv.Error as e:
            raise ValidationError(f'CSV parsing error: {str(e)}')
        except Exception as e:
            raise ValidationError(f'Error processing CSV file: {str(e)}')


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
    """Form for checkout"""
    class Meta:
        model = Order
        fields = ['email', 'address', 'city', 'state', 'zip_code']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email address'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Street address'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State'}),
            'zip_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ZIP code'}),
        }
    
    def clean_zip_code(self):
        """Validate ZIP code format"""
        zip_code = self.cleaned_data.get('zip_code', '').strip()
        if zip_code and len(zip_code) < 5:
            raise ValidationError('ZIP code must be at least 5 characters')
        return zip_code
