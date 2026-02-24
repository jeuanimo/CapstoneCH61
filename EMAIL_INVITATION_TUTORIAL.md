# Email Invitation & Account Activation System Tutorial

This tutorial walks you through how the member invitation and account activation system works in this Django application. The system uses **invitation codes** to control who can register, ensuring only authorized members can create accounts.

## Project File References

| Component | File Location |
|-----------|---------------|
| InvitationCode Model | `pages/models.py` (lines 644-686) |
| Signup Form | `pages/forms_profile.py` (lines 9-85) |
| Invitation Views | `pages/views.py` (lines 747-881, 979-1065) |
| URL Routes | `pages/urls.py` (lines 129-132) |
| Email Configuration | `config/settings.py` (lines 337-352) |
| Signup Template | `templates/pages/login.html` (lines 376-467) |
| Admin Template | `templates/pages/manage_invitations.html` |
| Create Invitation Template | `templates/pages/create_invitation.html` |

## Table of Contents

1. [System Overview](#system-overview)
2. [Database Model: InvitationCode](#database-model-invitationcode)
3. [Creating Invitation Codes](#creating-invitation-codes)
4. [User Registration Flow](#user-registration-flow)
5. [Form Validation](#form-validation)
6. [Email Configuration](#email-configuration)
7. [Admin Management Interface](#admin-management-interface)
8. [Complete Code Examples](#complete-code-examples)

---

## System Overview

The invitation system follows this workflow:

```
┌─────────────────────────────────────────────────────────────────┐
│                    INVITATION WORKFLOW                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. ADMIN creates invitation code with member email             │
│           ↓                                                     │
│  2. ADMIN shares code with prospective member                   │
│           ↓                                                     │
│  3. MEMBER goes to signup page                                  │
│           ↓                                                     │
│  4. MEMBER enters:                                              │
│     • Invitation code                                           │
│     • Email (must match invitation)                             │
│     • Username                                                  │
│     • Password                                                  │
│           ↓                                                     │
│  5. SYSTEM validates and creates account                        │
│           ↓                                                     │
│  6. Invitation marked as USED                                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Database Model: InvitationCode

The `InvitationCode` model stores all invitation data.

> **Source File:** [pages/models.py](pages/models.py) — Lines 644-686

### Model Definition

```python
# pages/models.py (lines 644-686)

class InvitationCode(models.Model):
    """Invitation codes for member signup"""
    
    # The unique invitation code (auto-generated)
    code = models.CharField(
        max_length=50, 
        unique=True, 
        help_text="Unique invitation code"
    )
    
    # Email address this code is assigned to
    email = models.EmailField(
        help_text="Email address this code is assigned to"
    )
    
    # Optional member details (pre-filled during signup)
    first_name = models.CharField(max_length=100, blank=True, default='')
    last_name = models.CharField(max_length=100, blank=True, default='')
    member_number = models.CharField(
        max_length=50, 
        blank=True, 
        default='', 
        help_text="National member number (if applicable)"
    )
    
    # Usage tracking
    is_used = models.BooleanField(default=False)
    used_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='invitation_used'
    )
    used_at = models.DateTimeField(null=True, blank=True)
    
    # Creation metadata
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='invitations_created'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(
        null=True, 
        blank=True, 
        help_text="Optional expiration date"
    )
    
    # Internal notes
    notes = models.TextField(
        blank=True, 
        default='', 
        help_text="Internal notes about this invitation"
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Invitation Code'
        verbose_name_plural = 'Invitation Codes'
    
    def __str__(self):
        return f"{self.code} - {self.email}"
    
    def is_valid(self):
        """Check if invitation code is still valid"""
        if self.is_used:
            return False
        if self.expires_at and timezone.now() > self.expires_at:
            return False
        return True
    
    def mark_as_used(self, user):
        """Mark invitation as used"""
        self.is_used = True
        self.used_by = user
        self.used_at = timezone.now()
        self.save()
```

### Key Fields Explained

| Field | Purpose |
|-------|---------|
| `code` | Unique alphanumeric code shared with the member |
| `email` | Must match the email entered during signup |
| `is_used` | Prevents code reuse after successful registration |
| `expires_at` | Optional expiration date for time-limited invitations |
| `member_number` | Links to national fraternity membership |

---

## Creating Invitation Codes

> **Source File:** [pages/views.py](pages/views.py) — Lines 997-1036

### View: Create Invitation

Admins create invitation codes through a dedicated view:

```python
# pages/views.py (lines 997-1036)

import secrets

@login_required
@user_passes_test(lambda u: u.is_staff)
def create_invitation(request):
    """Create new invitation code (admin only)"""
    
    if request.method == 'POST':
        # Get form data
        email = request.POST.get('email', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        member_number = request.POST.get('member_number', '').strip()
        notes = request.POST.get('notes', '').strip()
        
        # Validate email is provided
        if not email:
            messages.error(request, "Email address is required.")
            return redirect('create_invitation')
        
        # Check if email already has an active invitation
        existing = InvitationCode.objects.filter(
            email=email, 
            is_used=False
        ).first()
        
        if existing and existing.is_valid():
            messages.warning(
                request, 
                f"Active invitation already exists for {email}: {existing.code}"
            )
            return redirect('manage_invitations')
        
        # Generate unique code using Python's secrets module
        # This creates a cryptographically secure random string
        code = secrets.token_urlsafe(16)[:20].upper().replace('_', '').replace('-', '')
        
        # Create the invitation record
        InvitationCode.objects.create(
            code=code,
            email=email,
            first_name=first_name,
            last_name=last_name,
            member_number=member_number,
            notes=notes,
            created_by=request.user
        )
        
        logger.info(f"Invitation created: {code} for {email} by {request.user.username}")
        messages.success(request, f"Invitation code created: {code} for {email}")
        return redirect('manage_invitations')
    
    return render(request, 'pages/create_invitation.html')
```

### Code Generation Explained

The invitation code is generated using Python's `secrets` module:

```python
import secrets

# Generate cryptographically secure random string
code = secrets.token_urlsafe(16)  # Returns ~22 characters
code = code[:20]                   # Truncate to 20 characters
code = code.upper()                # Convert to uppercase
code = code.replace('_', '')       # Remove underscores
code = code.replace('-', '')       # Remove hyphens

# Result: "ABCD1234EFGH5678XYZ9" (example)
```

---

## User Registration Flow

> **Source File:** [pages/views.py](pages/views.py) — Lines 747-881

### Step 1: Validation Functions

The registration process uses several helper functions:

```python
# pages/views.py (lines 747-770)

def _validate_invitation_code(invitation_code):
    """
    Validate invitation code and return (invitation, error_message) tuple
    
    Returns:
        (InvitationCode, None) if valid
        (None, "error message") if invalid
    """
    if not invitation_code:
        return None, "Invitation code is required to sign up."
    
    try:
        invitation = InvitationCode.objects.get(code=invitation_code)
        
        if not invitation.is_valid():
            if invitation.is_used:
                return None, "This invitation code has already been used."
            else:
                return None, "This invitation code has expired."
        
        return invitation, None
        
    except InvitationCode.DoesNotExist:
        return None, "Invalid invitation code."


def _validate_invitation_email(invitation, email):
    """
    Check if email matches the invitation
    
    Args:
        invitation: InvitationCode instance
        email: Email entered by user
    
    Returns:
        Error message string or None if valid
    """
    if email.lower() != invitation.email.lower():
        return "Email address does not match the invitation code."
    return None
```

### Step 2: User Creation

```python
# pages/views.py (lines 771-801)

def _create_or_update_user(username, email, password, invitation, invitation_code):
    """
    Create or update user account from invitation
    
    This handles two scenarios:
    1. New user: Creates a fresh account
    2. Existing user: Updates password and activates account
    """
    try:
        # Check if username already exists (case-insensitive)
        user = User.objects.get(username__iexact=username)
        
        # Update existing user
        user.set_password(password)
        user.email = email
        
        # Apply name from invitation if provided
        if invitation.first_name:
            user.first_name = invitation.first_name
        if invitation.last_name:
            user.last_name = invitation.last_name
        
        user.is_active = True
        user.save()
        
        logger.info(
            f"Existing user activated with invitation: {user.username} "
            f"(code: {invitation_code})"
        )
        
    except User.DoesNotExist:
        # Create new user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        
        if invitation.first_name:
            user.first_name = invitation.first_name
        if invitation.last_name:
            user.last_name = invitation.last_name
        
        user.is_active = True
        user.save()
        
        logger.info(
            f"New user registered with invitation: {username} "
            f"(code: {invitation_code})"
        )
    
    return user
```

### Step 3: Member Profile Creation

```python
# pages/views.py (lines 803-829)

def _create_or_update_member_profile(user, invitation):
    """
    Create or update member profile for user
    
    Links the user account to a MemberProfile using the
    member_number from the invitation.
    """
    # Skip if no member number provided
    if not invitation.member_number:
        return
    
    try:
        # Try to find existing profile by member number
        member_profile = MemberProfile.objects.get(
            member_number=invitation.member_number
        )
        
        # Link to the new user if different
        if member_profile.user != user:
            member_profile.user = user
        
        # Set status to new_member (unless already a special status)
        if member_profile.status not in [
            'financial_life_member', 
            'non_financial_life_member', 
            'suspended'
        ]:
            member_profile.status = 'new_member'
        
        member_profile.save()
        logger.info(
            f"Updated existing MemberProfile {invitation.member_number} "
            f"for user {user.username}"
        )
        
    except MemberProfile.DoesNotExist:
        # Check if user already has a profile
        try:
            member_profile = MemberProfile.objects.get(user=user)
            member_profile.member_number = invitation.member_number
            
            if member_profile.status not in [
                'financial_life_member', 
                'non_financial_life_member', 
                'suspended'
            ]:
                member_profile.status = 'new_member'
            
            member_profile.save()
            logger.info(
                f"Added member_number {invitation.member_number} "
                f"to existing profile for {user.username}"
            )
            
        except MemberProfile.DoesNotExist:
            # Create new profile
            MemberProfile.objects.create(
                user=user,
                member_number=invitation.member_number,
                status='new_member'
            )
            logger.info(
                f"Created new MemberProfile {invitation.member_number} "
                f"for user {user.username}"
            )
```

### Step 4: Main Signup View

```python
# pages/views.py (lines 831-881)

SIGNUP_TEMPLATE = 'pages/signup.html'

def _create_user_from_invitation(form, invitation, email, invitation_code):
    """Create user from validated form and invitation"""
    username = form.cleaned_data.get('username')
    password = form.cleaned_data.get('password1')
    
    # Create or update user account and member profile
    user = _create_or_update_user(
        username, email, password, invitation, invitation_code
    )
    _create_or_update_member_profile(user, invitation)
    
    # Mark invitation as used only after all operations succeed
    invitation.mark_as_used(user)
    
    return username


def _handle_signup_post(request, form):
    """Handle POST request for signup view"""
    invitation_code = request.POST.get('invitation_code', '').strip()
    
    # Step 1: Validate invitation code
    invitation, error = _validate_invitation_code(invitation_code)
    if error:
        messages.error(request, error)
        return render(request, SIGNUP_TEMPLATE, {'form': form})
    
    # Step 2: Validate email matches invitation
    email = request.POST.get('email', '').strip()
    error = _validate_invitation_email(invitation, email)
    if error:
        messages.error(request, error)
        return render(request, SIGNUP_TEMPLATE, {'form': form})
    
    # Step 3: Process signup if form is valid
    if form.is_valid():
        username = _create_user_from_invitation(
            form, invitation, email, invitation_code
        )
        messages.success(
            request, 
            f"Account created successfully for {username}! Please log in."
        )
        return redirect('login')
    
    # Show form errors
    for field, errors in form.errors.items():
        for error in errors:
            messages.error(request, f"{field}: {error}")
    
    return render(request, SIGNUP_TEMPLATE, {'form': form})


def signup_view(request):
    """User registration view with invitation code validation"""
    # Redirect if already logged in
    if request.user.is_authenticated:
        return redirect('home')
    
    # Create form instance
    if request.method == 'POST':
        form = InvitationSignupForm(request.POST)
    else:
        form = InvitationSignupForm()
    
    if request.method == 'POST':
        return _handle_signup_post(request, form)
    
    return render(request, SIGNUP_TEMPLATE, {'form': form})
```

---

## Form Validation

> **Source File:** [pages/forms_profile.py](pages/forms_profile.py) — Lines 9-85

### InvitationSignupForm

The signup form includes custom validation:

```python
# pages/forms_profile.py (lines 9-85)

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


class InvitationSignupForm(forms.Form):
    """Custom signup form that validates invitation codes"""
    
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
                # Case mismatch - warn the user
                raise ValidationError(
                    f'Username case mismatch. The existing username is '
                    f'"{existing_user.username}". Please use the exact '
                    f'capitalization or your account may not work properly.'
                )
        
        return username
    
    def clean_password2(self):
        """Validate that the two passwords match"""
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise ValidationError("The two password fields didn't match.")
        
        # Validate password strength using Django's validators
        if password1:
            validate_password(password1)
        
        return password2
```

---

## Email Configuration

> **Source File:** [config/settings.py](config/settings.py) — Lines 337-352

### Django Settings

Configure email in `config/settings.py`:

```python
# config/settings.py (lines 337-352)

# ====================== EMAIL CONFIGURATION ======================

# Email backend - set via environment variable
# Development: Prints emails to console
# Production: Sends via SMTP
EMAIL_BACKEND = config(
    'EMAIL_BACKEND', 
    default='django.core.mail.backends.console.EmailBackend'
)

# SMTP server configuration
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')

# Sender email address
DEFAULT_FROM_EMAIL = config(
    'DEFAULT_FROM_EMAIL', 
    default='noreply@nugammasigma.org'
)
```

### Environment Variables (.env file)

```bash
# Development (prints to console)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Production (sends real emails via Gmail)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@yourdomain.org
```

### Email Utility Functions

> **Source File:** [pages/email_utils.py](pages/email_utils.py) — Lines 82-145

The project includes helper functions for sending emails:

```python
# pages/email_utils.py (lines 82-145)

from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def send_announcement_email(title, content, recipient_emails):
    """
    Send announcement email to members
    
    Args:
        title: Announcement title
        content: Announcement content
        recipient_emails: List of email addresses
    """
    if not recipient_emails:
        return False
    
    try:
        subject = f"Phi Beta Sigma - {title}"
        
        context = {
            'title': title,
            'content_html': content,
            'chapter_name': 'Nu Gamma Sigma',
        }
        
        # Try to use HTML template
        try:
            html_message = render_to_string(
                'pages/emails/announcement.html', 
                context
            )
            plain_message = strip_tags(html_message)
        except Exception:
            plain_message = f"{title}\n\n{content}"
            html_message = None
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_emails,
            html_message=html_message,
            fail_silently=False,
        )
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        return False
```

---

## Admin Management Interface

> **Source Files:** 
> - URLs: [pages/urls.py](pages/urls.py) — Lines 129-132
> - Views: [pages/views.py](pages/views.py) — Lines 979-993
> - Templates: [templates/pages/manage_invitations.html](templates/pages/manage_invitations.html), [templates/pages/create_invitation.html](templates/pages/create_invitation.html)

### URL Routes

```python
# pages/urls.py (lines 129-132)

urlpatterns = [
    # INVITATION CODE MANAGEMENT (Officer only)
    path('invitations/', views.manage_invitations, name='manage_invitations'),
    path('invitations/create/', views.create_invitation, name='create_invitation'),
    path('invitations/delete/<int:pk>/', views.delete_invitation, name='delete_invitation'),
    path('invitations/generate/<int:pk>/', views.generate_member_invitation, name='generate_member_invitation'),
]
```

### View: Manage Invitations

```python
# pages/views.py (lines 979-993)

@login_required
@user_passes_test(lambda u: u.is_staff)
def manage_invitations(request):
    """View and manage invitation codes (admin only)"""
    invitations = InvitationCode.objects.all().order_by('-created_at')
    
    # Separate active and used invitations
    active_invitations = [inv for inv in invitations if inv.is_valid()]
    used_invitations = invitations.filter(is_used=True)
    expired_invitations = [
        inv for inv in invitations 
        if not inv.is_valid() and not inv.is_used
    ]
    
    context = {
        'active_invitations': active_invitations,
        'used_invitations': used_invitations,
        'expired_invitations': expired_invitations,
    }
    return render(request, 'pages/manage_invitations.html', context)
```

### Template: manage_invitations.html

> **Source File:** [templates/pages/manage_invitations.html](templates/pages/manage_invitations.html)

```html
{% extends 'base.html' %}

{% block content %}
<div class="container my-5">
    <h2>Manage Invitation Codes</h2>
    
    <a href="{% url 'create_invitation' %}" class="btn btn-primary">
        <i class="fas fa-plus"></i> Create New Invitation
    </a>

    <!-- Active Invitations -->
    <div class="card mb-4">
        <div class="card-header bg-success text-white">
            <h4>Active Invitations ({{ active_invitations|length }})</h4>
        </div>
        <div class="card-body">
            {% if active_invitations %}
            <table class="table">
                <thead>
                    <tr>
                        <th>Code</th>
                        <th>Email</th>
                        <th>Name</th>
                        <th>Created</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {% for invitation in active_invitations %}
                    <tr>
                        <td><code>{{ invitation.code }}</code></td>
                        <td>{{ invitation.email }}</td>
                        <td>{{ invitation.first_name }} {{ invitation.last_name }}</td>
                        <td>{{ invitation.created_at|date:"M d, Y" }}</td>
                        <td>
                            <a href="{% url 'delete_invitation' invitation.pk %}" 
                               class="btn btn-sm btn-danger">
                                <i class="fas fa-trash"></i>
                            </a>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% else %}
            <p>No active invitations.</p>
            {% endif %}
        </div>
    </div>
    
    <!-- Used Invitations -->
    <div class="card mb-4">
        <div class="card-header bg-primary text-white">
            <h4>Used Invitations ({{ used_invitations.count }})</h4>
        </div>
        <div class="card-body">
            {% if used_invitations %}
            <table class="table">
                <thead>
                    <tr>
                        <th>Code</th>
                        <th>Email</th>
                        <th>Used By</th>
                        <th>Used At</th>
                    </tr>
                </thead>
                <tbody>
                    {% for invitation in used_invitations %}
                    <tr>
                        <td><code>{{ invitation.code }}</code></td>
                        <td>{{ invitation.email }}</td>
                        <td>{{ invitation.used_by.username }}</td>
                        <td>{{ invitation.used_at|date:"M d, Y g:i A" }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% endif %}
        </div>
    </div>
</div>
{% endblock %}
```

---

## Complete Code Examples

> **Note:** These are practical usage examples demonstrating how to use the invitation system. They can be run in the Django shell (`python manage.py shell`) or integrated into your own code.
>
> **Related Files:** [pages/models.py](pages/models.py), [pages/views.py](pages/views.py)

### Example 1: Creating an Invitation Programmatically

```python
from pages.models import InvitationCode
from django.contrib.auth.models import User
import secrets

def create_member_invitation(email, first_name, last_name, admin_user, member_number=None):
    """
    Create a new invitation code for a member
    
    Args:
        email: Member's email address
        first_name: Member's first name
        last_name: Member's last name
        admin_user: User creating the invitation
        member_number: Optional national member number
    
    Returns:
        InvitationCode instance
    """
    # Generate secure random code
    code = secrets.token_urlsafe(16)[:20].upper().replace('_', '').replace('-', '')
    
    invitation = InvitationCode.objects.create(
        code=code,
        email=email,
        first_name=first_name,
        last_name=last_name,
        member_number=member_number or '',
        created_by=admin_user,
        notes=f"Created for {first_name} {last_name}"
    )
    
    return invitation


# Usage:
admin = User.objects.get(username='admin')
invitation = create_member_invitation(
    email='newmember@example.com',
    first_name='John',
    last_name='Doe',
    admin_user=admin,
    member_number='PBS123456'
)
print(f"Invitation code: {invitation.code}")
```

### Example 2: Validating an Invitation Code

```python
def validate_and_get_invitation(code, email):
    """
    Validate an invitation code and email combination
    
    Returns:
        (True, InvitationCode) if valid
        (False, error_message) if invalid
    """
    try:
        invitation = InvitationCode.objects.get(code=code)
    except InvitationCode.DoesNotExist:
        return False, "Invalid invitation code"
    
    if invitation.is_used:
        return False, "This invitation code has already been used"
    
    if invitation.expires_at and timezone.now() > invitation.expires_at:
        return False, "This invitation code has expired"
    
    if email.lower() != invitation.email.lower():
        return False, "Email does not match the invitation"
    
    return True, invitation


# Usage:
is_valid, result = validate_and_get_invitation('ABC123', 'member@example.com')
if is_valid:
    invitation = result
    print(f"Valid invitation for {invitation.first_name} {invitation.last_name}")
else:
    error_message = result
    print(f"Error: {error_message}")
```

### Example 3: Complete Registration Test

```python
# Test in Django shell: python manage.py shell

from django.test import TestCase, Client
from django.contrib.auth.models import User
from pages.models import InvitationCode, MemberProfile
import secrets

class InvitationSignupTest(TestCase):
    def setUp(self):
        # Create admin user
        self.admin = User.objects.create_superuser(
            'admin', 'admin@test.com', 'adminpass123'
        )
        
        # Create invitation
        self.code = secrets.token_urlsafe(16)[:20].upper()
        self.invitation = InvitationCode.objects.create(
            code=self.code,
            email='newmember@test.com',
            first_name='Test',
            last_name='Member',
            member_number='TEST001',
            created_by=self.admin
        )
    
    def test_valid_signup(self):
        """Test successful registration with valid invitation"""
        client = Client()
        
        response = client.post('/signup/', {
            'invitation_code': self.code,
            'email': 'newmember@test.com',
            'username': 'newmember',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
        })
        
        # Should redirect to login on success
        self.assertEqual(response.status_code, 302)
        
        # User should be created
        user = User.objects.get(username='newmember')
        self.assertEqual(user.email, 'newmember@test.com')
        self.assertEqual(user.first_name, 'Test')
        
        # Invitation should be marked as used
        self.invitation.refresh_from_db()
        self.assertTrue(self.invitation.is_used)
        self.assertEqual(self.invitation.used_by, user)
        
        # Member profile should be created
        profile = MemberProfile.objects.get(user=user)
        self.assertEqual(profile.member_number, 'TEST001')
    
    def test_invalid_code(self):
        """Test signup with invalid invitation code"""
        client = Client()
        
        response = client.post('/signup/', {
            'invitation_code': 'INVALIDCODE',
            'email': 'newmember@test.com',
            'username': 'newmember',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
        })
        
        # Should stay on signup page with error
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid invitation code')
    
    def test_email_mismatch(self):
        """Test signup with mismatched email"""
        client = Client()
        
        response = client.post('/signup/', {
            'invitation_code': self.code,
            'email': 'wrong@test.com',  # Different email
            'username': 'newmember',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Email address does not match')
```

---

## Security Considerations

1. **Code Generation**: Uses `secrets.token_urlsafe()` for cryptographically secure codes
2. **Email Matching**: Email validation is case-insensitive but exact
3. **One-Time Use**: Codes are marked as used immediately after successful registration
4. **Expiration**: Optional expiration dates prevent old codes from being used
5. **Admin Only**: Only staff users can create and manage invitation codes
6. **Password Validation**: Django's built-in password validators are applied

---

## Summary

The email invitation system provides:

- ✅ Controlled registration via invitation codes
- ✅ Email verification (must match invitation)
- ✅ Automatic member profile linking
- ✅ Admin management interface
- ✅ Code expiration support
- ✅ Comprehensive audit trail (who created, who used, when)

This pattern is ideal for organizations that need to control membership access while providing a streamlined signup experience.
