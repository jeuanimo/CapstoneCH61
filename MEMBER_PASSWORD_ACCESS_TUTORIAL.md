# Member Password & Account Access System Tutorial

This tutorial explains how new members get access to the system through the invitation code workflow, including how member accounts are created with temporary passwords and how members set their own passwords.

## Project File References

| Component | File Location |
|-----------|---------------|
| MemberCreateView (CBV) | `pages/views.py` (lines 1176-1238) |
| MemberUpdateView (CBV) | `pages/views.py` (lines 1241-1340) |
| generate_invitation_for_member() | `pages/views.py` (lines 175-197) |
| generate_member_invitation view | `pages/views.py` (lines 1053-1075) |
| import_members view | `pages/views.py` (lines 2066-2114) |
| _create_member_from_row() | `pages/views.py` (lines 1963-1994) |
| edit_own_profile view | `pages/views.py` (lines 3419-3450) |
| InvitationCode Model | `pages/models.py` (lines 644-686) |
| EditProfileForm | `pages/forms_profile.py` (lines 93-200) |
| Password Validators | `config/settings.py` (lines 192-213) |
| Member Roster Template | `templates/pages/portal/roster.html` |
| Import Members Template | `templates/pages/portal/import_members.html` |
| **Password Reset URLs** | `config/urls.py` (lines 29-50) |
| **Password Reset Form** | `templates/registration/password_reset.html` |
| **Reset Email Sent Page** | `templates/registration/password_reset_done.html` |
| **Set New Password Form** | `templates/registration/password_reset_confirm.html` |
| **Reset Complete Page** | `templates/registration/password_reset_complete.html` |
| **Password Reset Email** | `templates/registration/password_reset_email.html` |
| **Login Page (Forgot Link)** | `templates/pages/login.html` (line 372) |
| **Email Auth Backend** | `pages/backends.py` |
| **Auth Backends Config** | `config/settings.py` (lines 146-150) |

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Member Account Creation Methods](#member-account-creation-methods)
3. [Invitation Code Generation](#invitation-code-generation)
4. [Password Setup Process](#password-setup-process)
5. [Regenerating Invitation Codes](#regenerating-invitation-codes)
6. [Special Case: Members Without Email](#special-case-members-created-without-email-address)
7. [Password Reset for CSV Users](#password-reset-for-csv-users)
8. [Email Login Support](#email-login-support)
9. [Security Implementation](#security-implementation)
10. [Complete Workflow Examples](#complete-workflow-examples)

---

## System Overview

The member access system follows a **two-phase approach** for security:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    MEMBER ACCESS WORKFLOW                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  PHASE 1: ADMIN CREATES MEMBER ACCOUNT                                      │
│  ────────────────────────────────────────                                   │
│  • Admin creates member via Roster or CSV Import                            │
│  • System generates RANDOM TEMPORARY PASSWORD                               │
│  • System auto-generates INVITATION CODE                                    │
│  • Member CANNOT login with random password                                 │
│                                                                             │
│  PHASE 2: MEMBER SETS OWN PASSWORD                                          │
│  ──────────────────────────────────────                                     │
│  • Admin sends invitation code to member                                    │
│  • Member goes to signup page                                               │
│  • Member enters invitation code + email + new password                     │
│  • System updates account with member's chosen password                     │
│  • Member can now login                                                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Why This Approach?

1. **Security**: Random passwords are never shared - members create their own
2. **Audit Trail**: Every account activation is logged
3. **Control**: Admins control who can register
4. **Flexibility**: Works for single members or bulk imports

---

## Member Account Creation Methods

### Method 1: Individual Member Creation (MemberCreateView)

> **Source File:** [pages/views.py](pages/views.py) — Lines 1176-1238

When an admin creates a single member through the roster interface:

```python
# pages/views.py (lines 1176-1238)

class MemberCreateView(OfficerRequiredMixin, CreateView):
    """
    Create a new member profile with user account.
    
    URL: /portal/roster/create/
    """
    model = MemberProfile
    form_class = MemberProfileForm
    template_name = 'pages/portal/member_form.html'
    success_url = reverse_lazy('member_roster')
    
    def form_valid(self, form):
        """Create user account and member profile"""
        # Get form data
        username = form.cleaned_data['username']
        email = form.cleaned_data['email']
        first_name = form.cleaned_data['first_name']
        last_name = form.cleaned_data['last_name']
        
        # Create user account with RANDOM PASSWORD
        # This password is never shared with the member
        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=User.objects.make_random_password()  # Secure random password
        )
        user.is_active = True
        user.save()
        
        # Save member profile with user reference
        member_profile = form.save(commit=False)
        member_profile.user = user
        member_profile.save()
        
        # AUTO-GENERATE invitation code for the member
        invitation = generate_invitation_for_member(
            user, 
            member_profile, 
            self.request.user
        )
        
        logger.info(f"Member created: {member_profile.member_number}")
        
        # Show success message WITH the invitation code
        messages.success(
            self.request,
            f"Successfully created member profile for {user.get_full_name()}! "
            f"Invitation Code: {invitation.code} "
            f"(Send this code to {user.email} so they can set their password)"
        )
        
        return super().form_valid(form)
```

### Key Points:
- `User.objects.make_random_password()` generates a cryptographically secure password
- The random password is **never displayed or shared** with anyone
- An invitation code is automatically generated
- Admin must send the invitation code to the member manually

---

### Method 2: Bulk CSV Import

> **Source File:** [pages/views.py](pages/views.py) — Lines 1963-1994, 2066-2114

When importing multiple members via CSV:

```python
# pages/views.py (lines 1963-1994)

def _create_member_from_row(row, username, email, member_number, initiation_date):
    """Create user and member profile from CSV row"""
    first_name, last_name = _extract_name_from_row_for_member(row)

    # Create user with RANDOM PASSWORD (never shared)
    user = User.objects.create_user(
        username=username,
        email=email or '',
        first_name=first_name,
        last_name=last_name,
        password=User.objects.make_random_password()  # Secure random password
    )

    # Determine member status
    status, dues_current = _determine_member_status(member_number)

    # Override status if provided in CSV
    if row.get('status', '').strip():
        status = row.get('status', '').strip()

    # Create the member profile
    MemberProfile.objects.create(
        user=user,
        member_number=member_number,
        status=status,
        initiation_date=initiation_date,
        line_name=row.get('line_name', '').strip(),
        line_number=row.get('line_number', '').strip(),
        phone=row.get('phone', '').strip(),
        emergency_contact_name=row.get('emergency_contact_name', '').strip(),
        emergency_contact_phone=row.get('emergency_contact_phone', '').strip(),
        address=row.get('address', '').strip(),
        bio=row.get('bio', '').strip(),
        dues_current=dues_current
    )

    return user
```

### Import Members View

```python
# pages/views.py (lines 2066-2114)

def import_members(request):
    """Import members from CSV file (admin only)"""
    if request.method != 'POST' or not request.FILES.get('csv_file'):
        return render(request, 'pages/portal/import_members.html')
    
    csv_file = request.FILES['csv_file']
    
    # Validate file extension
    if not csv_file.name.endswith('.csv'):
        messages.error(request, "Please upload a CSV file.")
        return redirect('import_members')
    
    try:
        # Read and decode CSV file
        decoded_file = csv_file.read().decode('utf-8-sig')
        lines = decoded_file.strip().split('\n')
        
        # Find header row (supports IHQ format)
        header_row_index = 0
        for i, line in enumerate(lines):
            if 'MAJOR_KEY' in line or ('FIRST_NAME' in line and 'LAST_NAME' in line):
                header_row_index = i
                break
        
        # Process CSV
        csv_data = '\n'.join(lines[header_row_index:])
        io_string = io.StringIO(csv_data)
        csv_reader = csv.DictReader(io_string)
        
        success_count, error_count, skipped_count, errors = _process_csv_file(
            csv_reader, 
            request.user.username
        )
        
        # Show results
        _show_import_results(request, success_count, error_count, skipped_count, errors)
        
    except Exception as e:
        logger.error(f"CSV import error: {str(e)}")
        messages.error(request, f"Error processing CSV file: {str(e)}")
    
    return render(request, 'pages/portal/import_members.html')
```

### Important Note for CSV Import:
- **Invitation codes are NOT auto-generated** during CSV import
- Admin must generate invitation codes individually using the roster interface
- This allows batch imports without creating thousands of invitation codes

---

## Invitation Code Generation

> **Source File:** [pages/views.py](pages/views.py) — Lines 175-197

The `generate_invitation_for_member()` function creates invitation codes:

```python
# pages/views.py (lines 175-197)

def generate_invitation_for_member(user, member_profile, created_by):
    """
    Generate an invitation code for a member.
    
    Args:
        user: User object
        member_profile: MemberProfile object  
        created_by: User who created the invitation (admin)
    
    Returns:
        InvitationCode object
    """
    invitation = InvitationCode.objects.create(
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        member_number=member_profile.member_number,
        created_by=created_by,
        notes=f"Auto-generated for {user.get_full_name()}"
    )
    
    logger.info(
        f"Invitation code generated: {invitation.code} "
        f"for member {member_profile.member_number}"
    )
    return invitation
```

### How Invitation Codes Work

The `InvitationCode` model (from [pages/models.py](pages/models.py) lines 644-686):

```python
# pages/models.py (lines 644-686)

class InvitationCode(models.Model):
    """Invitation codes for member signup"""
    
    # Auto-generated unique code
    code = models.CharField(max_length=50, unique=True)
    
    # Must match email entered during signup
    email = models.EmailField()
    
    # Pre-filled member info
    first_name = models.CharField(max_length=100, blank=True, default='')
    last_name = models.CharField(max_length=100, blank=True, default='')
    member_number = models.CharField(max_length=50, blank=True, default='')
    
    # Usage tracking
    is_used = models.BooleanField(default=False)
    used_by = models.ForeignKey(User, null=True, blank=True, ...)
    used_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_by = models.ForeignKey(User, null=True, blank=True, ...)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    def is_valid(self):
        """Check if invitation code is still valid"""
        if self.is_used:
            return False
        if self.expires_at and timezone.now() > self.expires_at:
            return False
        return True
    
    def mark_as_used(self, user):
        """Mark invitation as used after successful signup"""
        self.is_used = True
        self.used_by = user
        self.used_at = timezone.now()
        self.save()
```

---

## Password Setup Process

When a member receives their invitation code, they complete signup:

> **Source File:** [pages/views.py](pages/views.py) — Lines 771-801

```python
# pages/views.py (lines 771-801)

def _create_or_update_user(username, email, password, invitation, invitation_code):
    """
    Create or update user account from invitation.
    
    IMPORTANT: This function handles EXISTING users created by admin.
    It sets the member's CHOSEN password, replacing the random one.
    """
    try:
        # Find existing user (created by admin)
        user = User.objects.get(username__iexact=username)
        
        # SET THE MEMBER'S CHOSEN PASSWORD
        # This replaces the random password that was generated
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
        # Create new user if doesn't exist
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        # ... (rest of user creation)
    
    return user
```

### Password Security

> **Source File:** [config/settings.py](config/settings.py) — Lines 192-213

Django validates all passwords before they're set:

```python
# config/settings.py (lines 192-213)

AUTH_PASSWORD_VALIDATORS = [
    {
        # Prevents passwords similar to username, email, etc.
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        # Minimum 8 characters
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 8}
    },
    {
        # Blocks 20,000+ common passwords
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        # Prevents all-numeric passwords
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
```

---

## Regenerating Invitation Codes

If a member loses their invitation code or needs a new one:

> **Source File:** [pages/views.py](pages/views.py) — Lines 1053-1075

```python
# pages/views.py (lines 1053-1075)

@login_required
@user_passes_test(lambda u: u.is_staff)
def generate_member_invitation(request, pk):
    """Generate a new invitation code for an existing member (admin only)"""
    member_profile = get_object_or_404(MemberProfile, pk=pk)
    user = member_profile.user
    
    # Check if there's already an active invitation
    existing = InvitationCode.objects.filter(
        email=user.email, 
        is_used=False
    ).first()
    
    if existing and existing.is_valid():
        # Return existing code instead of creating duplicate
        messages.info(
            request, 
            f"Active invitation already exists: <strong>{existing.code}</strong>"
        )
    else:
        # Generate new invitation using helper function
        invitation = generate_invitation_for_member(
            user, 
            member_profile, 
            request.user
        )
        
        messages.success(
            request, 
            f"Invitation code generated: <strong>{invitation.code}</strong>"
        )
    
    return redirect('member_roster')
```

### Accessing from the Roster

> **Source File:** [templates/pages/portal/roster.html](templates/pages/portal/roster.html) — Line 107

```html
<!-- templates/pages/portal/roster.html (line 107) -->

<!-- Ticket icon button to generate invitation code -->
<a href="{% url 'generate_member_invitation' member.pk %}" 
   class="btn btn-info btn-sm" 
   title="Generate Invitation Code">
    <i class="fas fa-ticket-alt"></i>
</a>
```

---

## Special Case: Members Created WITHOUT Email Address

This is a common scenario, especially with CSV imports from HQ rosters where email addresses may not be available. The signup validation requires the email entered during signup to **match the email on the invitation code**. Here's how to handle members without emails:

### The Problem

When a member is created without an email:

```python
# CSV Import creates user with empty email
user = User.objects.create_user(
    username='member_12345',
    email='',  # Empty - no email in CSV
    first_name='John',
    last_name='Doe',
    password=User.objects.make_random_password()
)

# If invitation is generated now, it has empty email
invitation = generate_invitation_for_member(user, member_profile, admin)
# invitation.email = ''  # Empty!
```

When the member tries to sign up:

```python
# Member enters their email during signup
email = 'john.doe@example.com'

# Validation FAILS because emails don't match
def _validate_invitation_email(invitation, email):
    if email.lower() != invitation.email.lower():
        return "Email address does not match the invitation code."
    # '' != 'john.doe@example.com' → FAILS
```

### Solution: Admin Must Add Email BEFORE Generating Invitation

> **Source Files:** 
> - [pages/views.py](pages/views.py) — Lines 1241-1340 (MemberUpdateView)
> - [pages/forms_profile.py](pages/forms_profile.py) — MemberProfileForm

#### Step-by-Step Workflow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│            WORKFLOW: MEMBER WITHOUT EMAIL ADDRESS                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. ADMIN imports members via CSV (no email addresses)                      │
│     • User accounts created with empty email                                │
│     • MemberProfiles created                                                │
│     • NO invitation codes generated yet                                     │
│                                                                             │
│  2. ADMIN contacts member to get their email address                        │
│     • Via phone, in-person, or other means                                  │
│                                                                             │
│  3. ADMIN updates member's email in the system                              │
│     • Go to Member Roster → Edit Member                                     │
│     • Add member's email address                                            │
│     • Save changes                                                          │
│                                                                             │
│  4. ADMIN generates invitation code (now has valid email)                   │
│     • Click ticket icon (🎫) in roster                                      │
│     • Invitation code created WITH email                                    │
│                                                                             │
│  5. ADMIN sends invitation code to member                                   │
│     • Via email to their newly-added address                                │
│                                                                             │
│  6. MEMBER completes signup with invitation code                            │
│     • Email matches → Password set → Account activated                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Code Example: Admin Updates Member Email

```python
# Step 3: Admin edits member in roster to add email
# This is handled by MemberUpdateView

# pages/views.py (lines 1241-1340)
class MemberUpdateView(OfficerRequiredMixin, UpdateView):
    """Edit an existing member profile (officers only)"""
    model = MemberProfile
    form_class = MemberProfileForm
    template_name = 'pages/portal/member_form.html'
    success_url = reverse_lazy('member_roster')
    
    def form_valid(self, form):
        # Update user's email from form
        member_profile = form.instance
        user = member_profile.user
        
        # NEW EMAIL GETS SAVED TO USER
        user.email = form.cleaned_data['email']
        user.first_name = form.cleaned_data['first_name']
        user.last_name = form.cleaned_data['last_name']
        user.save()
        
        # ... rest of update logic
```

#### Code Example: Generate Invitation AFTER Email Added

```python
# Step 4: Generate invitation (now email is populated)

# pages/views.py (lines 175-197)
def generate_invitation_for_member(user, member_profile, created_by):
    invitation = InvitationCode.objects.create(
        email=user.email,  # NOW HAS VALUE: 'john.doe@example.com'
        first_name=user.first_name,
        last_name=user.last_name,
        member_number=member_profile.member_number,
        created_by=created_by,
        notes=f"Auto-generated for {user.get_full_name()}"
    )
    return invitation

# Now when member signs up:
# invitation.email = 'john.doe@example.com'
# entered email = 'john.doe@example.com'
# MATCHES → Success!
```

### Alternative: Member Updates Email After Login

If an admin has already generated an invitation code with an empty email, there's an alternative path using a temporary matching approach:

#### Option A: Admin Deletes Old Invitation and Creates New One

```python
# 1. Admin deletes the old invitation (with empty email)
# Via: /invitations/ → Delete button

# 2. Admin updates member's email
# Via: /portal/roster/edit/<id>/

# 3. Admin generates new invitation
# Via: Click ticket icon in roster

# New invitation now has correct email
```

#### Option B: Member Profile Update After First Login

If a member somehow gets access (e.g., admin manually sets password), they can update their own email:

> **Source File:** [pages/views.py](pages/views.py) — Lines 3419-3450

```python
# pages/views.py (lines 3419-3450)

@login_required
def edit_own_profile(request):
    """Allow members to edit their own profile - including EMAIL"""
    member_profile = MemberProfile.objects.get(user=request.user)
    
    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, ...)
        if form.is_valid():
            # Member can update their email
            request.user.email = form.cleaned_data['email']
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.save()
            
            form.save()
            messages.success(request, "Your profile has been updated!")
```

### Best Practice Recommendation

To avoid the "no email" problem entirely:

1. **CSV Import Best Practice**: Include email addresses in your CSV when possible
2. **IHQ Export Limitation**: International HQ exports often don't include emails - this is expected
3. **Collect emails first**: Have new members provide their email before import
4. **Or update immediately**: Right after CSV import, update member emails before generating invitations

### Complete Code Example: Full No-Email Workflow

```python
# SCENARIO: Admin imports 50 members from HQ CSV (no emails)
# One member: John Doe (member_12345) needs access

# Step 1: CSV Import already done - user exists with no email
user = User.objects.get(username='member_12345')
print(user.email)  # Output: ''

member = MemberProfile.objects.get(user=user)
print(member.member_number)  # Output: '12345'

# Step 2: Admin gets email from John (via phone call)
john_email = 'john.doe@example.com'

# Step 3: Admin updates email in system
# (Via roster edit form or directly)
user.email = john_email
user.save()

# Step 4: Admin generates invitation
invitation = generate_invitation_for_member(user, member, admin_user)
print(invitation.code)  # Output: 'XYZ789ABC123'
print(invitation.email)  # Output: 'john.doe@example.com' ✓

# Step 5: Admin sends code to john.doe@example.com

# Step 6: John signs up
# - Enters code: XYZ789ABC123
# - Enters email: john.doe@example.com
# - Creates password: MySecurePassword123!
# - SUCCESS! Emails match, account activated
```

---

## Password Reset for CSV Users

> **NEW FEATURE**: Password reset allows CSV-imported users to set their password using their email address, without needing an invitation code.

### Project File References

| Component | File Location |
|-----------|---------------|
| Password Reset URLs | `config/urls.py` (lines 29-50) |
| Password Reset Form | `templates/registration/password_reset.html` |
| Reset Email Sent | `templates/registration/password_reset_done.html` |
| Set New Password | `templates/registration/password_reset_confirm.html` |
| Reset Complete | `templates/registration/password_reset_complete.html` |
| Email Template | `templates/registration/password_reset_email.html` |
| Email Subject | `templates/registration/password_reset_subject.txt` |

### Overview

This feature provides an **alternative path** for CSV-imported members to gain access:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              PASSWORD RESET WORKFLOW FOR CSV USERS                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  PREREQUISITE: Member has username (member_XXXXX) and email in system       │
│                                                                             │
│  1. USER goes to login page → clicks "Forgot Password?"                     │
│                                                                             │
│  2. USER enters their email address                                         │
│                                                                             │
│  3. SYSTEM sends password reset link to that email                          │
│                                                                             │
│  4. USER clicks link in email                                               │
│                                                                             │
│  5. USER sets their new password                                            │
│                                                                             │
│  6. USER can now login with:                                                │
│     • Username: member_[member_number]                                      │
│     • Password: [their chosen password]                                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### URL Route Configuration

> **Source File:** [config/urls.py](config/urls.py) — Lines 29-50

```python
# config/urls.py

from django.contrib.auth import views as auth_views

urlpatterns = [
    # ... existing URLs ...
    
    # PASSWORD RESET (for CSV-imported users to set their password)
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='registration/password_reset.html',
             email_template_name='registration/password_reset_email.html',
             subject_template_name='registration/password_reset_subject.txt',
             success_url='/password-reset/done/'
         ), 
         name='password_reset'),
    
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='registration/password_reset_done.html'
         ), 
         name='password_reset_done'),
    
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='registration/password_reset_confirm.html',
             success_url='/password-reset-complete/'
         ), 
         name='password_reset_confirm'),
    
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='registration/password_reset_complete.html'
         ), 
         name='password_reset_complete'),
]
```

### How It Works

#### Step 1: Login Page with "Forgot Password?" Link

> **Source File:** [templates/pages/login.html](templates/pages/login.html)

```html
<!-- Login page now includes forgot password link -->
<button type="submit" class="btn-login">Sign In</button>

<div style="text-align: center; margin-top: 1rem;">
    <a href="{% url 'password_reset' %}">
        <i class="fas fa-key"></i> Forgot Password?
    </a>
</div>
```

#### Step 2: Password Reset Form

> **Source File:** [templates/registration/password_reset.html](templates/registration/password_reset.html)

The user enters their email address. Django's built-in `PasswordResetView` handles:

1. Looking up Users with that email
2. Generating a secure, one-time-use token
3. Sending the reset email

```python
# Django's PasswordResetView (built-in) handles:
from django.contrib.auth.views import PasswordResetView

class PasswordResetView(FormView):
    form_class = PasswordResetForm
    
    def form_valid(self, form):
        # Finds user by email
        email = form.cleaned_data['email']
        users = User.objects.filter(email__iexact=email, is_active=True)
        
        # For each matching user, send reset email
        for user in users:
            # Generate secure token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Send email with reset link
            # Link format: /password-reset-confirm/<uidb64>/<token>/
```

#### Step 3: Email Template

> **Source File:** [templates/registration/password_reset_email.html](templates/registration/password_reset_email.html)

```
Hello,

You're receiving this email because you requested a password reset 
for your account at {{ site_name }}.

Please click the link below to reset your password:

{{ protocol }}://{{ domain }}{% url 'password_reset_confirm' uidb64=uid token=token %}

Your username is: {{ user.username }}

If you didn't request this password reset, you can safely ignore 
this email. Your password will remain unchanged.

This link will expire after 24 hours.
```

#### Step 4: Set New Password Form

> **Source File:** [templates/registration/password_reset_confirm.html](templates/registration/password_reset_confirm.html)

When user clicks the link:

```python
# Django's PasswordResetConfirmView validates:
# 1. Token hasn't expired (default: 3 days)
# 2. Token hasn't been used
# 3. User account exists and is active

# Then presents form for new password
form_fields = ['new_password1', 'new_password2']
```

### Complete Workflow for CSV Users

```python
# SCENARIO: 50 members imported via CSV
# Member: John Doe, member_number=12345

# === INITIAL STATE (After CSV Import) ===
user = User.objects.get(username='member_12345')
print(user.username)    # 'member_12345'
print(user.email)       # 'john.doe@example.com' (from CSV)
print(user.password)    # pbkdf2_sha256$... (random, unknown to user)

# === JOHN WANTS TO ACCESS THE SYSTEM ===

# Step 1: John goes to /login/
# - Sees "Forgot Password?" link

# Step 2: John clicks "Forgot Password?"
# - Goes to /password-reset/

# Step 3: John enters john.doe@example.com
# - System finds user with that email
# - Generates reset token
# - Sends email

# Step 4: John gets email with link like:
# https://site.com/password-reset-confirm/MjM/abc123-def456/

# Step 5: John clicks link → Sets password: "MyNewSecurePass123!"

# Step 6: John can now login:
# Username: member_12345
# Password: MyNewSecurePass123!
```

### Comparison: Invitation vs Password Reset

| Feature | Invitation Code | Password Reset |
|---------|-----------------|----------------|
| **Requires** | Invitation code + email | Email only |
| **Best for** | New members without accounts | CSV-imported members with accounts |
| **Admin action** | Must generate invitation | None (self-service) |
| **Email must match** | Invitation.email | User.email |
| **Creates account** | Links to existing user | Updates existing user |
| **One-time use** | Yes (code invalidated) | Yes (token expires) |

### When to Use Which Method

#### Use **Invitation Code** when:
- Creating brand new members manually
- Want admin oversight of who registers
- Email might differ from invitation
- First-time account setup

#### Use **Password Reset** when:
- Member imported via CSV already has account
- Member forgot their password
- Faster self-service access needed
- Admin doesn't need to be involved

### Security Considerations

1. **Token Expiration**: Reset links expire after 24 hours
2. **One-Time Use**: Tokens are invalidated after use
3. **HTTPS Required**: Links should use HTTPS in production
4. **No User Enumeration**: Same message shown whether email exists or not
5. **Password Validation**: Django's validators enforce security rules

```python
# config/settings.py - Password validation applies to password reset too!
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
     'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]
```

---

## Email Login Support

> **NEW FEATURE**: Users can now login with either their username OR email address.

### Project File References

| Component | File Location |
|-----------|---------------|
| Email Auth Backend | `pages/backends.py` |
| Auth Backends Config | `config/settings.py` (lines 146-150) |
| Login Template | `templates/pages/login.html` (line 343) |

### Overview

Previously, users could only login with their username (`member_12345`). Now they can use either:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     LOGIN OPTIONS                                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  OPTION 1: Username + Password                                              │
│  ─────────────────────────────                                              │
│  • Username: member_12345                                                   │
│  • Password: MySecurePassword123                                            │
│                                                                             │
│  OPTION 2: Email + Password (NEW!)                                          │
│  ─────────────────────────────────                                          │
│  • Email: john.doe@example.com                                              │
│  • Password: MySecurePassword123                                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### How It Works

Django uses authentication backends in sequence. We added a custom `EmailBackend`:

> **Source File:** [config/settings.py](config/settings.py) — Lines 146-150

```python
# config/settings.py

AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',       # 1. Brute-force protection
    'pages.backends.EmailBackend',                # 2. NEW: Email login
    'django.contrib.auth.backends.ModelBackend', # 3. Default: Username login
]
```

### Custom Email Backend

> **Source File:** [pages/backends.py](pages/backends.py)

```python
# pages/backends.py

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

User = get_user_model()


class EmailBackend(ModelBackend):
    """
    Custom authentication backend that allows users to login with email.
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate user by email address.
        
        Args:
            username: Can be either username or email address
            password: The user's password
        """
        if username is None or password is None:
            return None
        
        # Check if the username looks like an email (contains @)
        if '@' not in username:
            # Not an email, let the default ModelBackend handle it
            return None
        
        try:
            # Try to find user by email (case-insensitive)
            user = User.objects.get(email__iexact=username)
        except User.DoesNotExist:
            # No user with this email - run hasher to prevent timing attacks
            User().set_password(password)
            return None
        except User.MultipleObjectsReturned:
            # Multiple users with same email - deny access (data integrity issue)
            return None
        
        # Check password and user is active
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        
        return None
```

### Login Form Update

> **Source File:** [templates/pages/login.html](templates/pages/login.html) — Line 343

The login form now shows a helpful label:

```html
<label for="id_username">Username or Email</label>
{{ form.username }}
<p class="help-text">Enter your username (member_XXXXX) or email address</p>
```

### Complete Workflow: CSV User with Email Login

```python
# SCENARIO: John Doe imported via CSV, wants to login with email

# === INITIAL STATE (After CSV Import) ===
user = User.objects.get(username='member_12345')
print(user.username)  # 'member_12345'
print(user.email)     # 'john.doe@example.com'

# === JOHN SETS PASSWORD VIA PASSWORD RESET ===
# 1. Goes to /password-reset/
# 2. Enters: john.doe@example.com
# 3. Receives email with reset link
# 4. Sets password: MySecurePassword123

# === JOHN CAN NOW LOGIN TWO WAYS ===

# Option 1: Username login (original)
authenticate(request, username='member_12345', password='MySecurePassword123')
# → Handled by ModelBackend → SUCCESS

# Option 2: Email login (NEW!)
authenticate(request, username='john.doe@example.com', password='MySecurePassword123')
# → Handled by EmailBackend → SUCCESS
```

### Security Features

1. **Case-Insensitive Email Lookup**: `John.Doe@Example.COM` matches `john.doe@example.com`
2. **Timing Attack Prevention**: Failed lookups still run password hasher
3. **Duplicate Email Protection**: If multiple users have same email, login fails
4. **Inactive User Rejection**: Users with `is_active=False` cannot login
5. **Works with django-axes**: Brute-force protection still active

### Why This Matters for CSV Users

CSV-imported users have auto-generated usernames (`member_12345`) that are hard to remember. Email login provides a more user-friendly experience:

| Login Method | Ease of Use | Security |
|--------------|-------------|----------|
| Username (`member_12345`) | Hard to remember | ✓ Secure |
| Email (`john@example.com`) | Easy to remember | ✓ Secure |

---

## Security Implementation

### Password Hashing

> **Source File:** [PASSWORD_SECURITY_AUDIT.md](PASSWORD_SECURITY_AUDIT.md)

All passwords are securely hashed using Django's PBKDF2-SHA256:

```python
# Django's password hashing (automatic)

# Method 1: set_password() - used when updating existing user
user.set_password(password)  # Automatically hashes

# Method 2: create_user() - used when creating new user
User.objects.create_user(
    username=username,
    password=password  # Automatically hashed
)

# Method 3: make_random_password() - generates secure random password
User.objects.make_random_password()  # Cryptographically secure
```

### Example of Hashed Password in Database

```
pbkdf2_sha256$600000$randomsalt$hashedpasswordvalue...
```

- **Algorithm**: PBKDF2 with SHA256
- **Iterations**: 600,000+ (Django 4.0+)
- **Salt**: Unique per password
- **NEVER** stored in plaintext

### Brute Force Protection

The system uses Django Axes for login protection:

```python
# Configured in config/settings.py

AXES_FAILURE_LIMIT = 5  # Lock after 5 failed attempts
AXES_COOLOFF_TIME = 1   # 1 hour lockout
AXES_LOCKOUT_PARAMETERS = ['username']
```

---

## Complete Workflow Examples

### Example 1: Creating a Single Member

```python
# Step 1: Admin creates member in roster
# This happens in MemberCreateView.form_valid()

# User account created with random password
user = User.objects.create_user(
    username='jdoe',
    email='john.doe@example.com',
    first_name='John',
    last_name='Doe',
    password=User.objects.make_random_password()  # e.g., "xK9#mP2$vL5@"
)

# Member profile created
member_profile = MemberProfile.objects.create(
    user=user,
    member_number='PBS123456',
    status='new_member'
)

# Invitation code auto-generated
invitation = generate_invitation_for_member(user, member_profile, admin_user)
# invitation.code = "ABC123XYZ789DEF456"

# Step 2: Admin sends invitation code to member
# "Your invitation code is: ABC123XYZ789DEF456"

# Step 3: Member goes to signup page and enters:
# - Invitation code: ABC123XYZ789DEF456
# - Email: john.doe@example.com
# - Username: jdoe
# - Password: MySecurePassword123!
# - Confirm Password: MySecurePassword123!

# Step 4: System processes signup
user = User.objects.get(username='jdoe')
user.set_password('MySecurePassword123!')  # Replaces random password
user.save()

invitation.mark_as_used(user)
# invitation.is_used = True
# invitation.used_by = user
# invitation.used_at = now()

# Step 5: Member can now login with their chosen password
```

### Example 2: Bulk Import + Individual Activation

```python
# Step 1: Admin imports CSV with 50 members
# Each member gets:
# - User account with random password
# - MemberProfile with their info
# - NO invitation code (for efficiency)

# Step 2: Admin generates invitation codes as needed
# Via roster UI: Click ticket icon (🎫) next to member

# For member John Doe (pk=42):
member = MemberProfile.objects.get(pk=42)
invitation = generate_invitation_for_member(
    member.user, 
    member, 
    admin_user
)
# Shows: "Invitation code generated: XYZ789ABC123"

# Step 3: Admin sends code to John Doe
# Step 4: John completes signup (same as Example 1)
```

### Example 3: Lost Invitation Code Recovery

```python
# Member lost their invitation code

# Admin goes to roster, finds member, clicks ticket icon
# System checks for existing valid invitation:

existing = InvitationCode.objects.filter(
    email='member@example.com',
    is_used=False
).first()

if existing and existing.is_valid():
    # Return existing code
    messages.info(request, f"Active code exists: {existing.code}")
else:
    # Generate new code
    new_invitation = generate_invitation_for_member(user, member, admin)
    messages.success(request, f"New code: {new_invitation.code}")
```

### Example 4: Member Created WITHOUT Email (CSV Import)

This is the most common scenario when using HQ CSV exports.

```python
# SCENARIO: Admin imports members from HQ CSV (no email addresses)
# Member: Jane Smith (member_98765) needs system access

# Step 1: After CSV Import - user exists with NO email
user = User.objects.get(username='member_98765')
member = MemberProfile.objects.get(user=user)

print(user.email)          # Output: ''  (empty)
print(member.member_number)  # Output: '98765'

# ❌ WRONG: Don't generate invitation yet!
# If you do, the invitation will have empty email and member can't sign up

# Step 2: Admin contacts Jane to get her email
# (Phone call, in-person meeting, etc.)
jane_email = 'jane.smith@example.com'

# Step 3: Admin updates email in system
# Via: /portal/roster/edit/<member_pk>/
# (Or directly in code:)
user.email = jane_email
user.save()

print(user.email)  # Output: 'jane.smith@example.com' ✓

# Step 4: NOW generate invitation code
invitation = generate_invitation_for_member(user, member, admin_user)

print(invitation.code)   # Output: 'ABC123DEF456'
print(invitation.email)  # Output: 'jane.smith@example.com' ✓

# Step 5: Admin emails invitation code to jane.smith@example.com
# "Your invitation code is: ABC123DEF456"

# Step 6: Jane goes to signup page and enters:
# - Invitation code: ABC123DEF456
# - Email: jane.smith@example.com  ← MATCHES invitation.email ✓
# - Username: member_98765
# - Password: JanesSecurePassword123!
# - Confirm password: JanesSecurePassword123!

# Step 7: System validates and activates
# _validate_invitation_email() passes because:
# 'jane.smith@example.com'.lower() == 'jane.smith@example.com'.lower() ✓

# Jane can now login!
```

#### Alternative: If Invitation Was Already Generated With Empty Email

```python
# If admin already clicked ticket icon BEFORE adding email:

# Check existing invitation
old_invitation = InvitationCode.objects.filter(
    member_number='98765',
    is_used=False
).first()

print(old_invitation.email)  # Output: ''  (empty - unusable!)

# Solution: Delete old invitation
old_invitation.delete()

# Update user email
user.email = 'jane.smith@example.com'
user.save()

# Generate NEW invitation (now with email)
new_invitation = generate_invitation_for_member(user, member, admin_user)
print(new_invitation.email)  # Output: 'jane.smith@example.com' ✓

# Send new code to Jane
```

---

## URL Routes Reference

> **Source File:** [pages/urls.py](pages/urls.py) — Lines 129-165

```python
# pages/urls.py (lines 129-165)

urlpatterns = [
    # INVITATION CODE MANAGEMENT
    path('invitations/', views.manage_invitations, name='manage_invitations'),
    path('invitations/create/', views.create_invitation, name='create_invitation'),
    path('invitations/delete/<int:pk>/', views.delete_invitation, name='delete_invitation'),
    path('invitations/generate/<int:pk>/', views.generate_member_invitation, name='generate_member_invitation'),
    
    # MEMBER ROSTER MANAGEMENT
    path('portal/roster/', views.MemberListView.as_view(), name='member_roster'),
    path('portal/roster/create/', views.MemberCreateView.as_view(), name='create_member'),
    path('portal/roster/import/', views.import_members, name='import_members'),
    
    # AUTHENTICATION
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
]
```

---

## Summary

### Standard Workflow (Member Has Email)

| Step | Who | Action | Result |
|------|-----|--------|--------|
| 1 | Admin | Creates member account | User with random password + MemberProfile |
| 2 | System | Generates invitation code | InvitationCode linked to email |
| 3 | Admin | Sends code to member | Member receives activation code |
| 4 | Member | Completes signup with code | Password updated to member's choice |
| 5 | System | Marks invitation used | Code cannot be reused |
| 6 | Member | Logs in | Full system access |

### CSV Import Workflow (Member WITHOUT Email)

| Step | Who | Action | Result |
|------|-----|--------|--------|
| 1 | Admin | Imports CSV (no emails) | Users + MemberProfiles created |
| 2 | Admin | Contacts member | Gets their email address |
| 3 | Admin | Updates member in roster | Email added to user account |
| 4 | Admin | Generates invitation code | InvitationCode NOW has email |
| 5 | Admin | Sends code to member | Member receives activation code |
| 6 | Member | Completes signup with code | Password updated, emails match |
| 7 | Member | Logs in | Full system access |

### Security Features

- ✅ Random passwords never shared
- ✅ Members choose their own passwords
- ✅ PBKDF2-SHA256 password hashing
- ✅ Password strength validation
- ✅ One-time use invitation codes
- ✅ Brute force protection
- ✅ Complete audit trail
- ✅ Email validation prevents unauthorized signups
