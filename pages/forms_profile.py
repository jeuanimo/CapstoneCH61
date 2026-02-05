from django import forms
from .models import MemberProfile, Announcement, Photo, PhotoAlbum, Event, Document
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


class InvitationSignupForm(forms.Form):
    """Custom signup form that allows existing usernames when using invitation codes"""
    
    invitation_code = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your invitation code'
        }),
        label='Invitation Code'
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your.email@example.com'
        }),
        label='Email Address'
    )
    
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your username'
        }),
        label='Username',
        help_text='Use the EXACT username provided by your admin (case-sensitive)'
    )
    
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password'
        }),
        label='Password',
        help_text='Your password must contain at least 8 characters.'
    )
    
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password'
        }),
        label='Password confirmation',
        help_text='Enter the same password as before, for verification.'
    )
    
    def clean_username(self):
        """Validate username - warn if case doesn't match existing user"""
        username = self.cleaned_data.get('username')
        
        # Check for case-insensitive match with existing users
        existing_users = User.objects.filter(username__iexact=username)
        if existing_users.exists():
            existing_user = existing_users.first()
            if existing_user.username != username:
                # Case mismatch - this is a warning, not an error
                # The view will handle matching to the correct user
                raise ValidationError(
                    f'Username case mismatch. The existing username is "{existing_user.username}". '
                    f'Please use the exact capitalization or your account may not work properly.'
                )
        
        return username
    
    def clean_password2(self):
        """Validate that the two passwords match"""
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise ValidationError("The two password fields didn't match.")
        
        # Validate password strength
        if password1:
            validate_password(password1)
        
        return password2


class EditProfileForm(forms.ModelForm):
    """Form for members to edit their own profile"""
    
    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First name'
        })
    )
    
    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last name'
        })
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'email@example.com'
        })
    )
    
    class Meta:
        model = MemberProfile
        fields = [
            'profile_image', 'phone', 'line_name', 'line_number',
            'address', 'bio', 'emergency_contact_name', 'emergency_contact_phone'
        ]
        widgets = {
            'profile_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(555) 555-5555'
            }),
            'line_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your line name'
            }),
            'line_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Line number'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Your address'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Tell us about yourself...'
            }),
            'emergency_contact_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Emergency contact name'
            }),
            'emergency_contact_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Emergency contact phone'
            }),
        }
        labels = {
            'profile_image': 'Profile Picture',
            'phone': 'Phone Number',
            'line_name': 'Line Name',
            'line_number': 'Line Number',
            'address': 'Address',
            'bio': 'Biography',
            'emergency_contact_name': 'Emergency Contact Name',
            'emergency_contact_phone': 'Emergency Contact Phone',
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Pre-fill user fields
        if self.user:
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial = self.user.last_name
            self.fields['email'].initial = self.user.email


class CreatePostForm(forms.ModelForm):
    """Form for members to create posts/announcements"""
    
    class Meta:
        model = Announcement
        fields = ['title', 'content', 'priority']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter post title...'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 8,
                'placeholder': 'Write your post content...'
            }),
            'priority': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
        labels = {
            'title': 'Post Title',
            'content': 'Post Content',
            'priority': 'Priority Level',
        }


class EditPhotoForm(forms.ModelForm):
    """Form for editing photo details"""
    
    class Meta:
        model = Photo
        fields = ['caption', 'tags', 'album', 'event']
        widgets = {
            'caption': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Add a caption for this photo...'
            }),
            'tags': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tags (comma-separated): event, party, brothers'
            }),
            'album': forms.Select(attrs={
                'class': 'form-control'
            }),
            'event': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
        labels = {
            'caption': 'Caption',
            'tags': 'Tags',
            'album': 'Album',
            'event': 'Event',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter albums to show only public ones
        self.fields['album'].queryset = PhotoAlbum.objects.filter(is_public=True)
        self.fields['album'].required = False
        self.fields['event'].required = False


class CreateAlbumForm(forms.ModelForm):
    """Form for creating photo albums"""
    
    class Meta:
        model = PhotoAlbum
        fields = ['title', 'description', 'is_public']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Album title...'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe what this album is about...'
            }),
            'is_public': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'title': 'Album Title',
            'description': 'Description',
            'is_public': 'Make this album visible to all members',
        }


class CreateEventForm(forms.ModelForm):
    """Form for creating events"""
    
    class Meta:
        model = Event
        fields = ['title', 'event_type', 'description', 'start_date', 'end_date', 'location', 'image']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Event name...'
            }),
            'event_type': forms.Select(attrs={
                'class': 'form-control',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Event details...'
            }),
            'start_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'end_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Event location...'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control'
            }),
        }
        labels = {
            'title': 'Event Name',
            'event_type': 'Event Type',
            'description': 'Description',
            'start_date': 'Start Date & Time',
            'end_date': 'End Date & Time',
            'location': 'Location',
            'image': 'Event Image',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['end_date'].required = False
        self.fields['image'].required = False


class DocumentForm(forms.ModelForm):
    """Form for creating and editing documents"""
    
    class Meta:
        model = Document
        fields = ['title', 'description', 'category', 'file', 'is_public', 'requires_officer']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Document title...'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Brief description of this document...'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'file': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'is_public': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'requires_officer': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'title': 'Document Title',
            'description': 'Description',
            'category': 'Category',
            'file': 'Document File',
            'is_public': 'Visible to all members',
            'requires_officer': 'Restricted to officers only',
        }
