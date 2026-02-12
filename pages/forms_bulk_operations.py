"""
Forms for bulk member operations (edit and delete multiple members at once)
"""

from django import forms
from .models import MemberProfile, ChapterLeadership


class BulkMemberEditForm(forms.Form):
    """Form for bulk editing member fields"""
    
    # Fields that can be bulk edited
    status = forms.ChoiceField(
        required=False,
        choices=[('', '--- Keep Current Status ---')] + MemberProfile.STATUS_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Member Status',
        help_text='Leave blank to keep current status for each member'
    )
    
    dues_current = forms.ChoiceField(
        required=False,
        choices=[
            ('', '--- Keep Current ---'),
            ('yes', 'Mark as Dues Current'),
            ('no', 'Mark as Dues Not Current'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Dues Status',
        help_text='Leave blank to keep current dues status for each member'
    )
    
    leadership_position = forms.ChoiceField(
        required=False,
        choices=[('', '--- Remove Leadership Position ---')] + ChapterLeadership.POSITION_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Leadership Position',
        help_text='Leave blank to remove all leadership positions from selected members'
    )
    
    def clean(self):
        """Ensure at least one field to edit is selected"""
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        dues_current = cleaned_data.get('dues_current')
        leadership_position = cleaned_data.get('leadership_position')
        
        # If they selected a position but no checkbox for it
        if not any([status, dues_current, leadership_position]):
            raise forms.ValidationError(
                "Please select at least one field to edit."
            )
        
        return cleaned_data


class BulkMemberDeleteForm(forms.Form):
    """Form for confirming bulk deletion of members"""
    
    confirm_delete = forms.BooleanField(
        required=True,
        label='I understand this will permanently delete these members and their user accounts. This action cannot be undone.',
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )


class BulkMemberActionForm(forms.Form):
    """Form for selecting members and action to perform"""
    
    ACTION_CHOICES = [
        ('edit', 'Bulk Edit Selected Members'),
        ('delete', 'Delete Selected Members'),
    ]
    
    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        }),
        label='Action',
        help_text='Choose what you want to do with the selected members'
    )
    
    member_ids = forms.CharField(
        widget=forms.HiddenInput(),
        help_text='Comma-separated list of member IDs to operate on'
    )
    
    def clean_member_ids(self):
        """Validate member IDs"""
        member_ids = self.cleaned_data.get('member_ids', '').strip()
        
        if not member_ids:
            raise forms.ValidationError("No members selected.")
        
        # Parse the IDs
        try:
            ids = [int(id.strip()) for id in member_ids.split(',') if id.strip()]
        except (ValueError, AttributeError):
            raise forms.ValidationError("Invalid member IDs format.")
        
        if not ids:
            raise forms.ValidationError("No valid member IDs provided.")
        
        # Verify all IDs exist
        members = MemberProfile.objects.filter(pk__in=ids)
        if members.count() != len(ids):
            raise forms.ValidationError("Some selected members do not exist.")
        
        return ids
    
    def get_member_ids(self):
        """Get the list of member IDs as integers"""
        if self.is_valid():
            return self.cleaned_data.get('member_ids', [])
        return []
