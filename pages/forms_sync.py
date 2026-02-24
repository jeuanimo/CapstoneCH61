from django import forms
from django.core.exceptions import ValidationError
import csv
import io


class MemberSyncForm(forms.Form):
    """Form for syncing members with international HQ member list"""
    
    csv_file = forms.FileField(
        label='International HQ Member List CSV',
        help_text='Upload CSV file from International HQ with current member numbers',
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.csv'
        })
    )
    
    confirm = forms.BooleanField(
        required=True,
        label='I understand members NOT on the HQ list will be marked as non-financial with a 90-day countdown to pay dues',
        help_text='Check this to confirm you understand the sync process',
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    def clean(self):
        """Validate CSV file"""
        cleaned_data = super().clean()
        csv_file = cleaned_data.get('csv_file')
        
        if not csv_file:
            raise ValidationError('CSV file is required')
        
        if not csv_file.name.endswith('.csv'):
            raise ValidationError('File must be a CSV file')
        
        if csv_file.size > 10 * 1024 * 1024:  # 10MB limit
            raise ValidationError('CSV file size must not exceed 10MB')
        
        return cleaned_data
    
    def _read_csv_content(self, csv_file):
        """Read and decode CSV file content."""
        if isinstance(csv_file, io.BytesIO) or hasattr(csv_file, 'read'):
            file_content = csv_file.read()
            if isinstance(file_content, bytes):
                file_content = file_content.decode('utf-8-sig')
        else:
            file_content = csv_file.read().decode('utf-8-sig')
        csv_file.seek(0)
        return file_content
    
    def _find_member_column(self, fieldnames):
        """Find the member number column from CSV headers."""
        valid_names = ['member#', 'member_number', 'member number', 'major_key']
        for col in fieldnames:
            if col.lower().strip() in valid_names:
                return col
        return None
    
    def _extract_member_numbers(self, csv_reader, member_column):
        """Extract member numbers from CSV rows."""
        member_numbers = set()
        errors = []
        for row_num, row in enumerate(csv_reader, start=2):
            member_num = row.get(member_column, '').strip()
            if member_num:
                member_numbers.add(member_num)
            else:
                errors.append(f'Row {row_num}: Missing member number')
        return member_numbers, errors
    
    def parse_member_numbers(self):
        """Extract member numbers from CSV file"""
        csv_file = self.cleaned_data['csv_file']
        
        try:
            file_content = self._read_csv_content(csv_file)
            csv_reader = csv.DictReader(io.StringIO(file_content))
            
            if not csv_reader.fieldnames:
                raise ValidationError('CSV file is empty')
            
            member_column = self._find_member_column(csv_reader.fieldnames)
            if not member_column:
                raise ValidationError(
                    f'CSV must contain a "Member#" or "Member Number" column. '
                    f'Found columns: {", ".join(csv_reader.fieldnames)}'
                )
            
            member_numbers, errors = self._extract_member_numbers(csv_reader, member_column)
            
            if not member_numbers:
                raise ValidationError('No valid member numbers found in CSV')
            
            return member_numbers, errors
        
        except csv.Error as e:
            raise ValidationError(f'CSV parsing error: {str(e)}')
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f'Error processing CSV file: {str(e)}')
