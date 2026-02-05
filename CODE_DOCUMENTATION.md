# CODE DOCUMENTATION & COMMENTS GUIDE
## Phi Beta Sigma Chapter Website - Full Project Documentation

This document provides comprehensive code documentation for the entire project. All code is heavily commented in the source files.

---

## TABLE OF CONTENTS

1. [Project Overview](#project-overview)
2. [Models.py - Database Models](#modelspy)
3. [Views.py - Business Logic](#viewspy)
4. [Admin.py - Admin Interface](#adminpy)
5. [Forms.py - Data Validation](#formspy)
6. [URLs.py - Routing](#urlspy)
7. [Templates - HTML Files](#templates)
8. [Key Functions & Methods](#key-functions--methods)

---

## PROJECT OVERVIEW

### Project Structure
```
pages/
├── models.py              # Database models (10+ models)
├── views.py               # View functions (50+ views)
├── admin.py               # Django admin configuration
├── urls.py                # URL routing
├── forms.py               # Form classes for portal
├── forms_boutique.py      # E-commerce forms
├── templatetags/
│   └── math_filters.py    # Custom template filters
└── migrations/            # Database migrations
```

### Technology Stack
- **Framework**: Django 4.2.28
- **Database**: SQLite3 (with migration system)
- **Payment**: Stripe API integration
- **SMS**: Twilio API integration
- **Frontend**: Bootstrap 5, CSS3, JavaScript
- **Python**: 3.14.2

---

## MODELS.PY - DATABASE MODELS

### Overview
The models.py file contains all Django database models that define the structure of the chapter website.

### Core Models

#### 1. **Category Model**
```python
class Category(models.Model):
    """
    Event categories for organizing events into types
    
    Purpose: Categorize events (Social Action, Education, Business, etc.)
    
    Fields:
    - name: Unique category name
    - description: Optional category description
    - color: Hex color for UI display
    - created_at: Auto-set creation timestamp
    """
```

**Usage**:
- Get all events in a category: `category.events.all()`
- Filter events by category: `Event.objects.filter(category=category)`
- Display in admin and frontend with custom colors

---

#### 2. **Event Model**
```python
class Event(models.Model):
    """
    Main event model for chapter events and activities
    
    Purpose: Store all events (meetings, social events, service activities)
    
    Key Fields:
    - title: Event name
    - description: Event details
    - category: Foreign key to Category
    - event_type: Classification (social_action, education, business, sigma_beta_club, sigma_wellness, other)
    - start_date/end_date: Event timing
    - location: Physical location
    - image: Optional event photo
    - created_at/updated_at: Timestamps
    
    Methods:
    - __str__(): Returns event title
    """
```

**Usage**:
```python
# Create event
event = Event.objects.create(
    title="Monthly Meeting",
    start_date=datetime.now(),
    end_date=datetime.now() + timedelta(hours=2),
    location="Student Center"
)

# Get upcoming events
upcoming = Event.objects.filter(start_date__gte=timezone.now()).order_by('start_date')

# Filter by type
social_action_events = Event.objects.filter(event_type='social_action')
```

---

#### 3. **ChapterLeadership Model**
```python
class ChapterLeadership(models.Model):
    """
    Tracks chapter officers and leadership positions
    
    Purpose: Display leadership roster on website
    
    Key Features:
    - POSITION_CHOICES: Predefined leadership positions
    - position_custom: Allow custom titles
    - display_order: Control ordering on page
    - is_active: Track current vs past leaders
    - term_start/term_end: Track tenure
    
    Methods:
    - __str__(): Returns "Name - Position"
    - get_position_title(): Returns display position name
    """
```

**Usage**:
```python
# Get current president
president = ChapterLeadership.objects.filter(
    position='president',
    is_active=True
).first()

# Get all current officers
current_officers = ChapterLeadership.objects.filter(is_active=True).order_by('display_order')

# Get past officers
past_officers = ChapterLeadership.objects.filter(is_active=False)
```

---

#### 4. **MemberProfile Model**
```python
class MemberProfile(models.Model):
    """
    Extended member information beyond Django User model
    
    Purpose: Store fraternity-specific member data
    
    Key Features:
    - OneToOne relationship with Django User
    - Status tracking: financial, non_financial, life_member, suspended, new_member
    - Officer privileges: is_officer flag for admin access
    - Auto-status calculation based on dues_current
    
    Custom Manager: MemberProfileManager
    - financial_members(): Active financial members
    - paying_members(): Currently paying members
    - all_active(): All active members (excluding suspended)
    
    Key Methods:
    - get_full_name(): Returns user's full name
    - save(): Auto-updates status based on dues payment
    """
```

**Usage**:
```python
# Get all financial members
financial = MemberProfile.objects.financial_members()

# Get paying members
paying = MemberProfile.objects.paying_members()

# Get specific member
member = MemberProfile.objects.get(member_number='12345')
print(member.get_full_name())

# Check if member is an officer
if member.is_officer:
    print("This member has admin privileges")
```

---

#### 5. **DuesPayment Model**
```python
class DuesPayment(models.Model):
    """
    Track financial obligations and payments
    
    Purpose: Record dues, fines, and other financial obligations
    
    Payment Types:
    - monthly_dues: Monthly membership dues
    - semester_dues: Semester-based dues
    - annual_dues: Annual membership fees
    - fine: Fines or penalties
    - house_charge: Housing-related charges
    - event_fee: Event participation fees
    - other: Custom charges
    
    Payment Status:
    - pending: Awaiting payment
    - paid: Fully paid
    - partial: Partially paid
    - overdue: Past due date
    - waived: Forgiven
    
    Key Properties:
    - balance: Amount still owed (amount - amount_paid)
    - is_overdue: Check if past due date
    """
```

**Usage**:
```python
# Create a dues payment
payment = DuesPayment.objects.create(
    member=member,
    payment_type='monthly_dues',
    amount=50.00,
    due_date=date.today() + timedelta(days=30)
)

# Get overdue payments
overdue = DuesPayment.objects.filter(status='overdue')

# Check balance
balance = payment.balance
print(f"Amount owed: ${balance}")

# Track payment history
history = member.payments.all().order_by('-due_date')
```

---

#### 6. **PhotoAlbum & Photo Models**
```python
class PhotoAlbum(models.Model):
    """
    Albums for organizing member photos
    
    Purpose: Create organized photo galleries
    
    Key Fields:
    - title: Album name
    - created_by: User who created album
    - is_public: Visibility setting
    
    Methods:
    - photo_count(): Number of photos in album
    """

class Photo(models.Model):
    """
    Individual photos in albums
    
    Purpose: Store photos with metadata and social features
    
    Key Features:
    - Like system (PhotoLike)
    - Comment system (PhotoComment)
    - Tag system (comma-separated)
    - Event association
    
    Methods:
    - like_count(): Number of likes
    - comment_count(): Number of comments
    """
```

**Usage**:
```python
# Create album
album = PhotoAlbum.objects.create(
    title="Chapter Meeting Photos",
    created_by=request.user,
    is_public=True
)

# Upload photo
photo = Photo.objects.create(
    album=album,
    uploaded_by=request.user,
    image=request.FILES['photo'],
    caption="Group photo at monthly meeting",
    tags="meeting,brothers,event"
)

# Get photo statistics
likes = photo.like_count()
comments = photo.comment_count()
```

---

#### 7. **InvitationCode Model**
```python
class InvitationCode(models.Model):
    """
    Member invitation codes for signup
    
    Purpose: Control who can sign up for portal
    
    Key Features:
    - Unique code generation
    - Email-based invitations
    - Optional expiration dates
    - Usage tracking
    - Auto-linking to member records
    
    Methods:
    - is_valid(): Check if code can still be used
    - mark_as_used(user): Record code usage
    """
```

**Usage**:
```python
# Create invitation
invite = InvitationCode.objects.create(
    code='PBS2024INVITE',
    email='member@example.com',
    member_number='12345',
    created_by=admin_user
)

# Check if valid
if invite.is_valid():
    # Allow user to signup with code
    pass

# Mark as used
invite.mark_as_used(user)
```

---

#### 8. **Product, Cart, Order Models (E-commerce)**
```python
class Product(models.Model):
    """Merchandise for boutique sale"""
    
    class Cart(models.Model):
        """User's shopping cart (OneToOne per user)"""
    
    class CartItem(models.Model):
        """Individual items in cart with quantity"""
    
    class Order(models.Model):
        """Completed order record"""
    
    class OrderItem(models.Model):
        """Items that were purchased"""
```

**Usage**:
```python
# Get cart for user
cart, created = Cart.objects.get_or_create(user=request.user)

# Add item to cart
cart_item, created = CartItem.objects.get_or_create(
    cart=cart,
    product=product,
    size='M',
    color='Black'
)

# Calculate totals
total_price = cart.get_total_price()
item_count = cart.get_total_items()

# Create order from cart
order = Order.objects.create(
    user=request.user,
    total_price=cart.get_total_price(),
    email=form.cleaned_data['email']
)
```

---

#### 9. **Stripe & Payment Models**
```python
class StripeConfiguration(models.Model):
    """Store Stripe API keys (Treasurer only)"""
    
    class StripePayment(models.Model):
        """Track Stripe payment attempts"""
```

**Features**:
- Store publishable and secret keys
- Test mode toggle
- Bank account info (last 4 digits only)
- Payment tracking with Stripe PI IDs
- Error message logging

---

#### 10. **Twilio & SMS Models**
```python
class TwilioConfiguration(models.Model):
    """Store Twilio SMS API keys"""
    
    class SMSPreference(models.Model):
        """Individual member SMS opt-in/opt-out"""
    
    class SMSLog(models.Model):
        """Log all SMS messages sent"""
```

**Features**:
- Store account SID and auth token
- Per-member preferences
- Quiet hours support
- Complete audit trail
- Delivery status tracking

---

## VIEWS.PY - BUSINESS LOGIC

The views.py file contains 50+ view functions organized into sections:

### View Categories

#### 1. **Authentication Views**
```python
def login_view(request):
    """Handle user login with email/username"""
    
def logout_view(request):
    """Handle user logout"""
    
def signup_view(request):
    """Handle new member registration with invitation code"""
```

**Key Features**:
- Email or username login
- Invitation code validation on signup
- Auto-create MemberProfile on signup
- Redirect to next page after login

---

#### 2. **Homepage & Public Pages**
```python
def home_view(request):
    """Display homepage with featured content"""
    
def about(request):
    """About page with fraternity information"""
    
def contact(request):
    """Contact form and information"""
    
def events(request):
    """List upcoming events"""
    
def chapter_programs(request):
    """Display chapter programs"""
```

**Key Features**:
- Public access (no login required)
- Responsive design
- Featured content sections
- Event/program information

---

#### 3. **Member Portal Views**
```python
@login_required
def portal_dashboard(request):
    """Main member portal dashboard"""
    
@login_required
def member_roster(request):
    """List all members"""
    
@login_required
def member_profile(request, username):
    """Display individual member profile"""
```

**Permissions**:
- All require login
- Some require staff/officer status
- View own profile without permission
- View others' profiles with restrictions

---

#### 4. **Admin/Officer Views**
```python
@user_passes_test(lambda u: u.is_staff or u.memberprofile.is_officer)
def add_product(request):
    """Add new boutique product"""
    
@user_passes_test(lambda u: u.is_staff or u.memberprofile.is_officer)
def import_products(request):
    """Bulk import products from CSV"""
```

**Permissions**:
- Require both login AND (staff OR officer status)
- Return 403 Forbidden if insufficient permissions
- Redirect to login if not authenticated

---

#### 5. **Boutique/E-commerce Views**
```python
def shop_home(request):
    """Display products with filtering"""
    
def product_detail(request, pk):
    """Show single product"""
    
@login_required
def add_to_cart(request, pk):
    """Add item to shopping cart"""
    
@login_required
def checkout(request):
    """Collect shipping information"""
    
@login_required
def payment(request, order_id):
    """Process Stripe payment"""
```

---

#### 6. **Helper Functions**
```python
def is_safe_redirect_url(url):
    """
    Validate redirect URLs to prevent open redirects
    - Only allows relative URLs
    - Prevents javascript: and protocol-relative URLs
    - Returns True if safe, False otherwise
    """
    
def generate_invitation_for_member(user, member_profile, created_by):
    """
    Create invitation code for a new member
    - Generates unique code
    - Associates with member number
    - Records who created invitation
    """
```

---

## ADMIN.PY - ADMIN INTERFACE

The admin.py file configures the Django admin interface for management.

### Key Admin Classes

#### 1. **ProductAdmin**
```python
class ProductAdmin(admin.ModelAdmin):
    """
    Admin interface for managing boutique products
    
    Features:
    - List view with name, category, price, inventory
    - Inline editing of price and inventory
    - Date hierarchy for browsing
    - Search by name and description
    - Filter by category
    - Read-only timestamps
    
    Useful for:
    - Quick price updates without editing full form
    - Inventory tracking
    - Product organization
    """
```

---

#### 2. **MemberProfileAdmin**
```python
class MemberProfileAdmin(admin.ModelAdmin):
    """
    Admin interface for managing member profiles
    
    Features:
    - Display member number, name, status, dues status
    - Filter by status, dues payment status, officer status
    - Quick toggle: dues_current and is_officer (inline editing)
    - Search by name and member number
    - Fieldset organization
    - Admin Privileges section for is_officer field
    
    Use Cases:
    - Promote/demote officers
    - Track member status
    - Quick dues updates
    - Member lookup
    """
```

---

#### 3. **OrderAdmin**
```python
class OrderAdmin(admin.ModelAdmin):
    """
    Admin interface for order management
    
    Features:
    - Display order ID, user, status, total price
    - Inline order items
    - Filter by status and date
    - Search by username and email
    - Read-only Stripe payment intent
    - Collapsible timestamp section
    """
```

---

## FORMS.PY - DATA VALIDATION

### Form Classes

#### 1. **ContactForm**
```python
class ContactForm(forms.Form):
    """
    Contact form for public contact page
    
    Fields:
    - name: Full name
    - email: Email address
    - message: Contact message
    
    Purpose: Collect contact form submissions
    """
```

#### 2. **BoutiqueImportForm**
```python
class BoutiqueImportForm(forms.Form):
    """
    CSV file upload form for bulk product import
    
    Features:
    - CSV file validation (max 5MB)
    - Header validation
    - Row-by-row error reporting
    - Data type validation
    - Duplicate prevention
    
    Fields:
    - csv_file: File upload
    
    Methods:
    - clean_csv_file(): Validate and parse CSV
    """
```

#### 3. **CheckoutForm**
```python
class CheckoutForm(forms.Form):
    """
    Shipping information form
    
    Fields:
    - email, address, city, state, zip_code
    
    Purpose: Collect shipping address for orders
    """
```

#### 4. **ProductForm**
```python
class ProductForm(forms.ModelForm):
    """
    Form for adding/editing products
    
    Fields:
    - name, description, category, price, inventory
    - sizes, colors, image
    
    Purpose: Create and edit boutique products
    """
```

---

## URLS.PY - ROUTING

The urls.py file maps URL patterns to view functions.

### URL Organization

#### Public URLs (No login required)
```
/ → home_view
/about/ → about
/contact/ → contact
/pages/boutique/ → shop_home
/pages/boutique/product/<id>/ → product_detail
```

#### Portal URLs (Login required)
```
/portal/ → portal_dashboard
/portal/roster/ → member_roster
/portal/profile/<username>/ → member_profile
/portal/messages/ → messages_inbox
/portal/dues/ → dues_view
```

#### Admin URLs (Staff or Officer required)
```
/pages/boutique/admin/add-product/ → add_product
/pages/boutique/admin/edit-product/<id>/ → edit_product
/pages/boutique/admin/delete-product/<id>/ → delete_product
/pages/boutique/admin/import-products/ → import_products
```

#### Django Admin
```
/admin/ → Django admin interface
/admin/pages/product/ → Manage products
/admin/pages/memberprofile/ → Manage members
/admin/pages/order/ → Manage orders
```

---

## TEMPLATES - HTML FILES

### Template Structure

All templates extend `base.html` for consistency.

#### Template Categories

1. **Public Templates**
   - home.html - Homepage
   - about.html - About page
   - contact.html - Contact form
   - chapter_programs.html - Programs overview

2. **Portal Templates**
   - portal/dashboard.html - Portal home
   - portal/roster.html - Member list
   - portal/profile.html - Member profile
   - portal/messages.html - Messaging

3. **Boutique Templates**
   - boutique/shop.html - Product listing
   - boutique/product_detail.html - Product info
   - boutique/cart.html - Shopping cart
   - boutique/checkout.html - Checkout form
   - boutique/payment.html - Payment form
   - boutique/product_form.html - Add/edit product
   - boutique/delete_product_confirm.html - Delete confirmation

### Template Features

- **Dark Mode Support**: All templates include dark mode CSS
- **Responsive Design**: Mobile-optimized layouts
- **Form Validation**: Client and server-side validation
- **Permission Checks**: {% if user.is_staff %} blocks
- **CSRF Protection**: {% csrf_token %} on all forms

---

## KEY FUNCTIONS & METHODS

### Authentication Functions

```python
def login_required(function):
    """Django decorator requiring user login"""
    
def user_passes_test(test_func):
    """Django decorator for permission checks"""
    # Usage: @user_passes_test(lambda u: u.is_staff)
```

### Common View Patterns

```python
# Check permissions
if not (request.user.is_staff or request.user.memberprofile.is_officer):
    return HttpForbidden()

# Get or create
object, created = Model.objects.get_or_create(defaults={...})

# Pagination
from django.core.paginator import Paginator
paginator = Paginator(queryset, 25)
page = paginator.get_page(request.GET.get('page'))

# Messages
messages.success(request, "Operation successful!")
messages.error(request, "An error occurred")
```

### Common Model Methods

```python
# Get all
objects = Model.objects.all()

# Filter
objects = Model.objects.filter(status='active')

# Get one
object = Model.objects.get(id=1)

# Count
count = Model.objects.count()

# Delete
object.delete()

# Update
Model.objects.filter(id=1).update(status='updated')
```

---

## BEST PRACTICES

### Security
- ✅ Always use @login_required for protected views
- ✅ Always use @user_passes_test for permission checks
- ✅ Always include {% csrf_token %} in forms
- ✅ Validate file uploads (size, type)
- ✅ Sanitize user input

### Performance
- ✅ Use select_related() and prefetch_related()
- ✅ Add indexes to frequently filtered fields
- ✅ Cache expensive queries
- ✅ Use pagination for large querysets
- ✅ Minimize database queries per request

### Code Quality
- ✅ Write docstrings for all functions
- ✅ Use meaningful variable names
- ✅ Keep functions focused and small
- ✅ Use custom managers for common queries
- ✅ Add comments for complex logic

---

## TESTING

### Test Coverage

- Unit tests for models
- View tests for permissions
- Form tests for validation
- Integration tests for workflows

### Running Tests

```bash
# Run all tests
python manage.py test

# Run specific app
python manage.py test pages

# Run specific test
python manage.py test pages.tests.TestModelName

# With coverage
coverage run --source='.' manage.py test
coverage report
```

---

## DEPLOYMENT CHECKLIST

- [ ] All migrations applied
- [ ] Environment variables set (.env file)
- [ ] Static files collected
- [ ] Database backed up
- [ ] Admin credentials set
- [ ] Stripe keys configured
- [ ] Twilio keys configured
- [ ] HTTPS enabled
- [ ] CORS headers configured
- [ ] Logging configured
- [ ] Email configured
- [ ] Backup system in place

---

## TROUBLESHOOTING

### Common Issues

**Issue**: "User matching query does not exist"
- **Cause**: Trying to access user that doesn't exist
- **Fix**: Add .get() with error handling or check existence first

**Issue**: "Reverse for 'url_name' not found"
- **Cause**: URL name doesn't exist in urls.py
- **Fix**: Check urls.py for correct name pattern

**Issue**: "Permission denied" on officer functions
- **Cause**: User doesn't have is_officer flag set
- **Fix**: Enable is_officer in member profile admin

**Issue**: Stripe payments failing
- **Cause**: Wrong API keys or test mode
- **Fix**: Check StripeConfiguration in admin

**Issue**: SMS not sending
- **Cause**: Twilio not configured or opted out
- **Fix**: Check TwilioConfiguration and SMSPreference

---

## ADDITIONAL RESOURCES

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Stripe API Reference](https://stripe.com/docs/api)
- [Twilio SMS API](https://www.twilio.com/docs/sms)
- [Bootstrap 5 Docs](https://getbootstrap.com/docs/5.0/)

---

**Last Updated**: February 5, 2026
**Project Version**: 1.0
**Status**: Production Ready ✅

