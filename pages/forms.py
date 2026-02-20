"""
=============================================================================
DJANGO FORMS FOR PHI BETA SIGMA FRATERNITY CHAPTER WEBSITE
=============================================================================

This module contains all forms for user input and data validation:

FORM CATEGORIES:
1. Contact & Communication
   - ContactForm: Public contact form for website visitors

2. Member Management
   - MemberProfileForm: Create/edit member profiles with user account integration
   - ChapterLeadershipForm: Manage chapter leadership positions

3. Dues & Payments
   - DuesPaymentForm: Full dues record editing (admin)
   - CreateBillForm: Simplified bill creation interface (treasurer)

4. Payment Integration
   - StripeConfigurationForm: Configure Stripe payment processing (treasurer)

5. SMS Notifications
   - TwilioConfigurationForm: Configure Twilio SMS system (admin)
   - SMSPreferenceForm: Allow members to opt-in/out of SMS alerts

All forms use crispy_forms for Bootstrap styling and include:
- Input validation methods (clean_fieldname)
- Custom error messages for user guidance
- Appropriate widgets (TextInput, Select, DateInput, etc.)
- Security best practices (CSRF protection, secure field handling)

=============================================================================
"""

from django import forms
from .models import ChapterLeadership, MemberProfile, DuesPayment, StripeConfiguration, TwilioConfiguration, SMSPreference
from django.contrib.auth.models import User

class ContactForm(forms.Form):
    """Secure contact form with CSRF protection and validation"""
    
    name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your full name',
            'class': 'form-control'
        }),
        label='Name'
    )
    
    email = forms.EmailField(
        max_length=100,
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': 'your.email@example.com',
            'class': 'form-control'
        }),
        label='Email Address'
    )
    
    message = forms.CharField(
        max_length=2000,
        required=True,
        widget=forms.Textarea(attrs={
            'placeholder': 'Enter your message here...',
            'rows': 6,
            'class': 'form-control'
        }),
        label='Message'
    )
    
    def clean_name(self):
        """Validate and sanitize name field"""
        name = self.cleaned_data.get('name')
        if name:
            name = name.strip()
            if len(name) < 2:
                raise forms.ValidationError("Name must be at least 2 characters long.")
        return name
    
    def clean_email(self):
        """Validate email field"""
        email = self.cleaned_data.get('email')
        if email:
            email = email.lower().strip()
        return email
    
    def clean_message(self):
        """Validate and sanitize message field"""
        message = self.cleaned_data.get('message')
        if message:
            message = message.strip()
            if len(message) < 10:
                raise forms.ValidationError("Message must be at least 10 characters long.")
        return message

class ChapterLeadershipForm(forms.ModelForm):
    """Form for adding/editing chapter leadership"""
    
    class Meta:
        model = ChapterLeadership
        fields = ['full_name', 'position', 'email', 'phone', 'bio', 'profile_image', 'display_order', 'is_active']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter full name'
            }),
            'position': forms.Select(attrs={
                'class': 'form-control'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@example.com'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(555) 555-5555'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Enter biography...'
            }),
            'profile_image': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'display_order': forms.NumberInput(attrs={
                'class': 'form-control',
                'value': 0
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


class MemberProfileForm(forms.ModelForm):
    """Form for creating/editing member profiles"""
    
    # User fields
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username'
        }),
        help_text='Username for login'
    )
    first_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First Name'
        })
    )
    last_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last Name'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'email@example.com'
        })
    )
    
    # Leadership position field
    leadership_position = forms.ChoiceField(
        required=False,
        choices=[('', '--- None (Regular Member) ---')] + ChapterLeadership.POSITION_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Leadership Position',
        help_text='Select if this member holds a leadership position'
    )
    
    # Admin action fields (not on model)
    mark_non_financial = forms.BooleanField(
        required=False,
        label='Mark Member as Non-Financial with 90-Day Countdown',
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        help_text='Check to start 90-day countdown for dues payment. Member will lose document access.'
    )
    
    class Meta:
        model = MemberProfile
        fields = [
            'member_number', 'status', 'initiation_date', 'line_name', 
            'line_number', 'phone', 'emergency_contact_name', 
            'emergency_contact_phone', 'address', 'profile_image', 
            'bio', 'dues_current'
        ]
        widgets = {
            'member_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Member ID/Number'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'initiation_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'line_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Line Name'
            }),
            'line_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Line Number'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(555) 555-5555'
            }),
            'emergency_contact_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Emergency Contact Name'
            }),
            'emergency_contact_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Emergency Contact Phone'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Street Address, City, State, ZIP'
            }),
            'profile_image': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Member biography...'
            }),
            'dues_current': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        # Extract user instance if editing
        self.user_instance = kwargs.pop('user_instance', None)
        super().__init__(*args, **kwargs)
        
        # Pre-fill user fields if editing
        if self.user_instance:
            self.fields['username'].initial = self.user_instance.username
            self.fields['first_name'].initial = self.user_instance.first_name
            self.fields['last_name'].initial = self.user_instance.last_name
            self.fields['email'].initial = self.user_instance.email
            # Allow editing username - don't set readonly
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        
        # If editing an existing user
        if self.user_instance:
            # If username hasn't changed (exact match), allow it without checking
            if username == self.user_instance.username:
                return username
            # If username changed, check both exact and case-insensitive matches
            if User.objects.filter(username=username).exists():
                raise forms.ValidationError("This username is already taken by another user.")
            # Check for case-insensitive conflicts
            if User.objects.filter(username__iexact=username).exclude(username=self.user_instance.username).exists():
                raise forms.ValidationError(
                    f"A username similar to '{username}' already exists with different capitalization. "
                    "Please choose a different username to avoid confusion."
                )
            return username
        
        # If creating a new user, check for both exact and case-insensitive matches
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        # Check for case-insensitive conflicts
        if User.objects.filter(username__iexact=username).exists():
            existing = User.objects.filter(username__iexact=username).first()
            raise forms.ValidationError(
                f"A username similar to '{username}' already exists as '{existing.username}'. "
                "Please use the exact same capitalization or choose a different username."
            )
        return username
    
    def clean_member_number(self):
        member_number = self.cleaned_data.get('member_number')
        # If editing, allow the same member number
        if self.instance and self.instance.pk:
            existing = MemberProfile.objects.filter(member_number=member_number).exclude(pk=self.instance.pk)
            if existing.exists():
                raise forms.ValidationError("This member number is already in use.")
        else:
            # If creating, check if member number exists
            if MemberProfile.objects.filter(member_number=member_number).exists():
                raise forms.ValidationError("This member number is already in use.")
        return member_number
    
    def save(self, commit=True):
        """Handle non-financial marking and send email notification"""
        from django.utils import timezone
        from pages.email_utils import send_dues_reminder_email
        
        member_profile = super().save(commit=False)
        mark_non_financial = self.cleaned_data.get('mark_non_financial', False)
        
        # If checkbox is checked, mark as non-financial with 90-day countdown
        if mark_non_financial:
            member_profile.status = 'non_financial'
            member_profile.dues_current = False
            member_profile.marked_for_removal_date = timezone.now()
            member_profile.removal_reason = "Manually marked as non-financial by officer. Member must pay dues within 90 days."
        
        # Update user account if needed
        if self.user_instance:
            self.user_instance.username = self.cleaned_data.get('username')
            self.user_instance.first_name = self.cleaned_data.get('first_name')
            self.user_instance.last_name = self.cleaned_data.get('last_name')
            self.user_instance.email = self.cleaned_data.get('email')
            if commit:
                self.user_instance.save()
        
        if commit:
            member_profile.save()
            # Send email notification if marked as non-financial
            if mark_non_financial:
                send_dues_reminder_email(member_profile)
        
        return member_profile


class DuesPaymentForm(forms.ModelForm):
    """Form for creating/editing dues and payments"""
    
    class Meta:
        model = DuesPayment
        fields = ['member', 'payment_type', 'amount', 'amount_paid', 'description', 
                  'due_date', 'payment_date', 'status', 'payment_method', 'transaction_id', 'notes']
        widgets = {
            'member': forms.Select(attrs={
                'class': 'form-control'
            }),
            'payment_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0'
            }),
            'amount_paid': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter description (optional)'
            }),
            'due_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'payment_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'payment_method': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Cash, Check, PayPal, Venmo'
            }),
            'transaction_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Transaction ID (optional)'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Internal notes (optional)'
            }),
        }


class CreateBillForm(forms.ModelForm):
    """Simplified form for creating dues bills"""
    
    send_to_all_members = forms.BooleanField(
        required=False,
        label="Send to All Active Members",
        help_text="Check this to send this bill to all active chapter members",
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    custom_type = forms.CharField(
        required=False,
        label="Custom Bill Type",
        help_text="Specify a custom bill type for clarity and accounting purposes",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., Special Assessment, Fundraiser, Equipment Fee',
        })
    )
    
    class Meta:
        model = DuesPayment
        fields = ['member', 'payment_type', 'amount', 'description', 'due_date', 'custom_type']
        widgets = {
            'member': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'payment_type': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter amount due',
                'step': '0.01',
                'min': '0',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Bill description (e.g., Monthly dues, Special event, etc.)',
            }),
            'due_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': True
            }),
            'custom_type': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Special Assessment, Fundraiser, Equipment Fee',
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set defaults
        self.fields['payment_type'].initial = 'monthly_dues'
        # Make description optional
        self.fields['description'].required = False
        # Make member optional if sending to all
        self.fields['member'].required = False
        # Remove custom_type from default rendering - we'll add it manually in template
        self.fields.pop('custom_type', None)
    
    def clean(self):
        cleaned_data = super().clean()
        payment_type = cleaned_data.get('payment_type')
        # Get custom_type from POST data since we removed it from fields
        custom_type = self.data.get('custom_type', '')
        
        # If "other" is selected, custom_type is required
        if payment_type == 'other' and not custom_type:
            raise forms.ValidationError("Please specify a custom bill type when selecting 'Other'.")
        
        return cleaned_data


class StripeConfigurationForm(forms.ModelForm):
    """Form for treasurer to configure Stripe payment settings"""
    
    class Meta:
        model = StripeConfiguration
        fields = ['stripe_publishable_key', 'stripe_secret_key', 'stripe_account_id', 
                  'bank_account_name', 'bank_account_last_four', 'bank_routing_number', 
                  'is_active', 'is_test_mode']
        widgets = {
            'stripe_publishable_key': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'pk_test_... or pk_live_...',
                'help_text': 'Your Stripe Publishable Key'
            }),
            'stripe_secret_key': forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': 'sk_test_... or sk_live_...',
                'help_text': 'Your Stripe Secret Key (keep secure!)',
                'autocomplete': 'off'
            }),
            'stripe_account_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'acct_... (optional)',
                'help_text': 'Your Stripe Account ID (optional)'
            }),
            'bank_account_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Nu Gamma Sigma Chapter'
            }),
            'bank_account_last_four': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last 4 digits of account',
                'maxlength': '4'
            }),
            'bank_routing_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Bank routing number (9 digits)',
                'maxlength': '10'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_test_mode': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'help_text': 'Uncheck to use live mode (requires live keys)'
            }),
        }
    
    def clean_stripe_publishable_key(self):
        key = self.cleaned_data.get('stripe_publishable_key', '').strip()
        if key and not (key.startswith('pk_test_') or key.startswith('pk_live_')):
            raise forms.ValidationError('Invalid Stripe Publishable Key format.')
        return key
    
    def clean_stripe_secret_key(self):
        key = self.cleaned_data.get('stripe_secret_key', '').strip()
        if key and not (key.startswith('sk_test_') or key.startswith('sk_live_')):
            raise forms.ValidationError('Invalid Stripe Secret Key format.')
        return key
    
    def clean_bank_routing_number(self):
        routing = self.cleaned_data.get('bank_routing_number', '').strip()
        if routing and not routing.isdigit():
            raise forms.ValidationError('Routing number must contain only digits.')
        if routing and len(routing) != 9:
            raise forms.ValidationError('Routing number must be exactly 9 digits.')
        return routing
    
    def clean_bank_account_last_four(self):
        last_four = self.cleaned_data.get('bank_account_last_four', '').strip()
        if last_four and not last_four.isdigit():
            raise forms.ValidationError('Account number must contain only digits.')
        if last_four and len(last_four) != 4:
            raise forms.ValidationError('Please enter the last 4 digits of your account.')
        return last_four


class TwilioConfigurationForm(forms.ModelForm):
    """Form for admin to configure Twilio SMS settings"""
    
    class Meta:
        model = TwilioConfiguration
        fields = ['account_sid', 'auth_token', 'twilio_phone_number', 'is_active', 'is_test_mode']
        widgets = {
            'account_sid': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Twilio Account SID',
                'help_text': 'Found in your Twilio Console'
            }),
            'auth_token': forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Twilio Auth Token',
                'help_text': 'Keep this secure!',
                'autocomplete': 'off'
            }),
            'twilio_phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+1234567890',
                'help_text': 'Your Twilio phone number (include country code)'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'help_text': 'Enable SMS alerts system'
            }),
            'is_test_mode': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'help_text': 'Test mode logs SMS but does not send (for testing)'
            }),
        }
    
    def clean_account_sid(self):
        sid = self.cleaned_data.get('account_sid', '').strip()
        if sid and len(sid) < 20:
            raise forms.ValidationError('Invalid Twilio Account SID format.')
        return sid
    
    def clean_auth_token(self):
        token = self.cleaned_data.get('auth_token', '').strip()
        if token and len(token) < 20:
            raise forms.ValidationError('Invalid Twilio Auth Token format.')
        return token
    
    def clean_twilio_phone_number(self):
        phone = self.cleaned_data.get('twilio_phone_number', '').strip()
        if phone and not phone.startswith('+'):
            raise forms.ValidationError('Phone number must start with + and include country code (e.g., +1234567890).')
        if phone and len(phone) < 10:
            raise forms.ValidationError('Invalid phone number format.')
        return phone


class SMSPreferenceForm(forms.ModelForm):
    """Form for members to set SMS preferences"""
    
    class Meta:
        model = SMSPreference
        fields = ['phone_number', 'receive_announcements', 'receive_messages', 
                  'receive_dues_reminders', 'receive_event_alerts', 
                  'quiet_hours_enabled', 'quiet_hours_start', 'quiet_hours_end']
        widgets = {
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+1 (555) 123-4567',
                'help_text': 'Your mobile phone number (with country code)',
                'type': 'tel'
            }),
            'receive_announcements': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'help_text': 'Receive SMS alerts for chapter announcements'
            }),
            'receive_messages': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'help_text': 'Receive SMS when someone sends you a direct message'
            }),
            'receive_dues_reminders': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'help_text': 'Receive SMS reminders for upcoming dues payments'
            }),
            'receive_event_alerts': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'help_text': 'Receive SMS alerts for upcoming chapter events'
            }),
            'quiet_hours_enabled': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'help_text': 'Enable quiet hours - no SMS between these times'
            }),
            'quiet_hours_start': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time',
                'help_text': 'Quiet hours start time (e.g., 22:00)'
            }),
            'quiet_hours_end': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time',
                'help_text': 'Quiet hours end time (e.g., 08:00)'
            }),
        }
    
    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number', '').strip()
        if phone and not phone.startswith('+'):
            raise forms.ValidationError('Phone number must start with + and include country code (e.g., +12025551234).')
        if phone and len(phone) < 10:
            raise forms.ValidationError('Phone number appears to be invalid.')
        return phone
    
    def clean(self):
        cleaned_data = super().clean()
        quiet_enabled = cleaned_data.get('quiet_hours_enabled')
        start_time = cleaned_data.get('quiet_hours_start')
        end_time = cleaned_data.get('quiet_hours_end')
        
        if quiet_enabled and (not start_time or not end_time):
            raise forms.ValidationError('Please set both start and end times for quiet hours.')
        
        return cleaned_data

class BulkEmailForm(forms.Form):
    """Form for sending bulk emails to members"""
    
    RECIPIENT_CHOICES = [
        ('all', 'All Members'),
        ('financial', 'Financial Members Only'),
        ('non_financial', 'Non-Financial Members Only'),
        ('officers', 'Officers Only'),
    ]
    
    recipient_group = forms.ChoiceField(
        choices=RECIPIENT_CHOICES,
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        }),
        label='Send Email To',
        help_text='Choose which members to receive this email'
    )
    
    subject = forms.CharField(
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email subject line'
        }),
        help_text='Subject line for the email'
    )
    
    message = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 10,
            'placeholder': 'Write your announcement here...\n\nTips:\n- Keep it professional\n- Include any action items or deadlines\n- Sign with chapter name'
        }),
        help_text='Body of the email message'
    )
    
    include_unsubscribed = forms.BooleanField(
        required=False,
        label='Include members who opted out of emails',
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        help_text='Uncheck to respect SMS/email preferences'
    )
    
    send_immediately = forms.BooleanField(
        required=False,
        label='Send immediately',
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        help_text='If unchecked, you\'ll see a preview first'
    )


class BulkMessageForm(forms.Form):
    """Form for sending bulk internal messages to members"""
    
    RECIPIENT_CHOICES = [
        ('all', 'All Members'),
        ('financial', 'Financial Members Only'),
        ('non_financial', 'Non-Financial Members Only'),
        ('officers', 'Officers Only'),
        ('selected', 'Select Individual Members'),
    ]
    
    PRIORITY_CHOICES = [
        ('NR', 'Normal'),
        ('HI', 'High'),
        ('UR', 'Urgent'),
    ]
    
    CATEGORY_CHOICES = [
        ('GN', 'General'),
        ('OF', 'Official Chapter Business'),
        ('EV', 'Event Related'),
        ('FI', 'Financial'),
        ('CM', 'Committee'),
    ]
    
    recipient_group = forms.ChoiceField(
        choices=RECIPIENT_CHOICES,
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        }),
        label='Send Message To',
        help_text='Choose which members to receive this message'
    )
    
    selected_members = forms.ModelMultipleChoiceField(
        queryset=None,  # Set in __init__
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'member-checkbox'
        }),
        label='Select Members',
        help_text='Choose specific members (only used when "Select Individual Members" is chosen)'
    )
    
    subject = forms.CharField(
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Message subject'
        }),
        help_text='Subject line for the message'
    )
    
    content = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 10,
            'placeholder': 'Write your message here...'
        }),
        help_text='Body of the message'
    )
    
    priority = forms.ChoiceField(
        choices=PRIORITY_CHOICES,
        initial='NR',
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Priority',
        help_text='Set message priority level'
    )
    
    category = forms.ChoiceField(
        choices=CATEGORY_CHOICES,
        initial='GN',
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Category',
        help_text='Categorize this message'
    )
    
    def __init__(self, *args, current_user=None, **kwargs):
        super().__init__(*args, **kwargs)
        from django.contrib.auth.models import User
        # Exclude current user from recipient list
        if current_user:
            self.fields['selected_members'].queryset = User.objects.exclude(
                id=current_user.id
            ).order_by('last_name', 'first_name')
        else:
            self.fields['selected_members'].queryset = User.objects.all().order_by('last_name', 'first_name')


class SiteConfigurationForm(forms.ModelForm):
    """Form for officers/admins to manage site branding and configuration"""
    
    class Meta:
        from .models import SiteConfiguration
        model = SiteConfiguration
        fields = [
            'organization_name', 'chapter_name',
            'chapter_logo', 'pbs_seal', 'favicon',
            'facebook_url', 'instagram_url', 'twitter_url', 'email_address',
            'footer_text'
        ]
        widgets = {
            'organization_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Phi Beta Sigma Fraternity, Inc'
            }),
            'chapter_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Nu Gamma Sigma Chapter'
            }),
            'chapter_logo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'pbs_seal': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'favicon': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/png,image/x-icon,image/svg+xml'
            }),
            'facebook_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://facebook.com/yourpage'
            }),
            'instagram_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://instagram.com/yourprofile'
            }),
            'twitter_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://twitter.com/yourhandle'
            }),
            'email_address': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'contact@example.com'
            }),
            'footer_text': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '© 2026 Your Organization Name'
            }),
        }
        labels = {
            'organization_name': 'Organization Name',
            'chapter_name': 'Chapter Name',
            'chapter_logo': 'Chapter Logo',
            'pbs_seal': 'Phi Beta Sigma Seal/Logo',
            'favicon': 'Site Favicon (Browser Icon)',
            'facebook_url': 'Facebook URL',
            'instagram_url': 'Instagram URL',
            'twitter_url': 'Twitter/X URL',
            'email_address': 'Contact Email',
            'footer_text': 'Footer Text',
        }
        help_texts = {
            'chapter_logo': 'Your chapter-specific logo (PNG or JPG recommended)',
            'pbs_seal': 'The Phi Beta Sigma seal shown in the header',
            'favicon': 'Small icon shown in browser tabs (PNG, ICO, or SVG)',
        }