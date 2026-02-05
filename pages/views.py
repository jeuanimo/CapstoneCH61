from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q, Sum
from django.db import models
from django_filters import CharFilter, FilterSet
from .models import (
    Event, ChapterLeadership, MemberProfile, DuesPayment,
    EventAttendance, Announcement, AnnouncementView, Document, Message, 
    ProfileComment, CommentLike, PhotoAlbum, Photo,
    PhotoComment, PhotoLike, InvitationCode, StripeConfiguration, StripePayment,
    TwilioConfiguration, SMSPreference, SMSLog,
    Product, Cart, CartItem, Order, OrderItem
)
from .forms import ContactForm, ChapterLeadershipForm, MemberProfileForm, DuesPaymentForm, StripeConfigurationForm, TwilioConfigurationForm, SMSPreferenceForm, CreateBillForm
from .forms_profile import (
    EditProfileForm, CreatePostForm, InvitationSignupForm,
    EditPhotoForm, CreateAlbumForm, CreateEventForm, DocumentForm
)
from .forms_boutique import BoutiqueImportForm, ProductForm, CheckoutForm
from datetime import datetime, timedelta
import calendar
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
import logging
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
import os
from decimal import Decimal
from django.utils import timezone
from urllib.parse import urlparse
import csv
import io
from twilio.rest import Client
import os
import stripe
import json
from decimal import Decimal

# Template constants
SIGNUP_TEMPLATE = 'pages/signup.html'


# ==================== HELPER FUNCTIONS ====================

def is_safe_redirect_url(url):
    """
    Check if the provided URL is safe for redirect.
    Only allows relative URLs or same-origin URLs.
    Prevents open redirect vulnerabilities.
    
    Args:
        url: The URL to validate
        
    Returns:
        bool: True if safe, False otherwise
    """
    if not url:
        return False
    
    # Parse the URL
    parsed = urlparse(url)
    
    # Only allow relative URLs (no scheme or netloc)
    if parsed.scheme or parsed.netloc:
        return False
    
    # Prevent protocol-relative URLs
    if url.startswith('//'):
        return False
    
    # Prevent javascript: URLs
    if url.lower().startswith('javascript:'):
        return False
    
    return True


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
    
    logger.info(f"Invitation code generated: {invitation.code} for member {member_profile.member_number}")
    return invitation


logger = logging.getLogger(__name__)

# Create your views here.

class EventFilter(FilterSet):
    title = CharFilter(field_name='title', lookup_expr='icontains')
    
    class Meta:
        model = Event
        fields = ['title']

def home_view(request):
    """Home page view"""
    # Get upcoming events for the calendar modal
    now = datetime.now()
    upcoming_events = Event.objects.filter(
        start_date__gte=now
    ).order_by('start_date')[:5]  # Limit to next 5 events
    
    context = {
        'upcoming_events': upcoming_events
    }
    
    return render(request, 'pages/home.html', context)

def about(request):
    """About page view"""
    return render(request, 'pages/about.html')

def events(request):
    """Events & Service page view with searchable calendar"""
    events_list = Event.objects.all()
    filterset = EventFilter(request.GET, queryset=events_list)
    events_filtered = filterset.qs
    
    # Get the current month for calendar view
    now = datetime.now()
    
    # Safely parse and validate year and month parameters
    try:
        year = int(request.GET.get('year', now.year))
        month = int(request.GET.get('month', now.month))
        
        # Validate ranges
        if not (1 <= month <= 12):
            month = now.month
        if year < 1900 or year > 2100:
            year = now.year
    except (ValueError, TypeError):
        year = now.year
        month = now.month
    
    # Generate calendar for the month
    cal = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]
    
    # Get events for the current month
    events_this_month = Event.objects.filter(
        start_date__year=year,
        start_date__month=month
    ).order_by('start_date')
    
    # Check if user is an officer (for edit/delete permissions)
    is_officer = False
    if request.user.is_authenticated:
        is_officer = ChapterLeadership.objects.filter(
            email__iexact=request.user.email,
            is_active=True
        ).exists() or request.user.is_staff
    
    context = {
        'filterset': filterset,
        'events': events_filtered,
        'calendar': cal,
        'month': month,
        'year': year,
        'month_name': month_name,
        'events_this_month': events_this_month,
        'is_officer': is_officer,
    }
    return render(request, 'pages/events.html', context)

def news(request):
    """News page view"""
    return render(request, 'pages/news.html')

def programs(request):
    """Programs page view"""
    return render(request, 'pages/programs.html')

def chapter_history(request):
    """Chapter History page view"""
    return render(request, 'pages/chapter_history.html')

def chapter_leadership(request):
    """Display chapter leadership/officers"""
    # Define position order for display
    position_order = {
        'president': 0,
        'vice_president_1st': 1,
        'vice_president_2nd': 2,
        'secretary': 3,
        'treasurer': 4,
        'parliamentarian': 5,
        'chaplain': 6,
        'historian': 7,
        'sergeant_at_arms': 8,
        'board_member': 9,
        'other': 10,
    }
    
    leaders = ChapterLeadership.objects.filter(is_active=True)
    
    # Group by person name
    leaders_by_name = {}
    for leader in leaders:
        if leader.full_name not in leaders_by_name:
            leaders_by_name[leader.full_name] = {
                'person': leader,
                'positions': [],
            }
        leaders_by_name[leader.full_name]['positions'].append(leader)
    
    # Sort positions for each person by position_order
    for name, data in leaders_by_name.items():
        data['positions'].sort(key=lambda x: (position_order.get(x.position, 99), x.display_order))
    
    # Sort people by their first/primary position
    sorted_leaders = sorted(
        leaders_by_name.items(),
        key=lambda x: (position_order.get(x[1]['positions'][0].position, 99), x[1]['positions'][0].display_order)
    )
    
    leaders = [data for name, data in sorted_leaders]
    
    context = {
        'leaders': leaders,
    }
    return render(request, 'pages/chapter_leadership.html', context)

def chapter_membership(request):
    """Chapter Membership page view"""
    return render(request, 'pages/chapter_membership.html')

def chapter_programs(request):
    """Chapter Programs page view"""
    return render(request, 'pages/chapter_programs.html')

def program_business(request):
    """Bigger and Better Business program detail - officers can upload photos"""
    is_officer = request.user.is_authenticated and (request.user.is_staff or (hasattr(request.user, 'member_profile') and request.user.member_profile.is_officer))
    
    # Handle photo upload for officers
    if request.method == 'POST' and is_officer:
        if 'photo_upload' in request.FILES:
            photo = Photo(
                uploaded_by=request.user,
                image=request.FILES['photo_upload'],
                caption=request.POST.get('caption', ''),
                tags='business'  # Auto-tag as business
            )
            photo.save()
            messages.success(request, 'Photo uploaded successfully!')
            return redirect('program_business')
    
    # Get photos tagged with business-related keywords
    photos = Photo.objects.filter(
        tags__icontains='business'
    ).order_by('-created_at')[:8]
    
    context = {
        'photos': photos,
        'program_name': 'Bigger & Better Business',
        'is_officer': is_officer
    }
    return render(request, 'pages/programs/business.html', context)

def program_social_action(request):
    """Social Action program detail - officers can upload photos"""
    is_officer = request.user.is_authenticated and (request.user.is_staff or (hasattr(request.user, 'member_profile') and request.user.member_profile.is_officer))
    
    # Handle photo upload for officers
    if request.method == 'POST' and is_officer:
        if 'photo_upload' in request.FILES:
            photo = Photo(
                uploaded_by=request.user,
                image=request.FILES['photo_upload'],
                caption=request.POST.get('caption', ''),
                tags='social'  # Auto-tag as social
            )
            photo.save()
            messages.success(request, 'Photo uploaded successfully!')
            return redirect('program_social_action')
    
    # Get photos tagged with social action-related keywords
    photos = Photo.objects.filter(
        tags__icontains='social'
    ).order_by('-created_at')[:8]
    
    context = {
        'photos': photos,
        'program_name': 'Social Action',
        'is_officer': is_officer
    }
    return render(request, 'pages/programs/social_action.html', context)

def program_education(request):
    """Education program detail - officers can upload photos"""
    is_officer = request.user.is_authenticated and (request.user.is_staff or (hasattr(request.user, 'member_profile') and request.user.member_profile.is_officer))
    
    # Handle photo upload for officers
    if request.method == 'POST' and is_officer:
        if 'photo_upload' in request.FILES:
            photo = Photo(
                uploaded_by=request.user,
                image=request.FILES['photo_upload'],
                caption=request.POST.get('caption', ''),
                tags='education'  # Auto-tag as education
            )
            photo.save()
            messages.success(request, 'Photo uploaded successfully!')
            return redirect('program_education')
    
    # Get photos tagged with education-related keywords
    photos = Photo.objects.filter(
        tags__icontains='education'
    ).order_by('-created_at')[:8]
    
    context = {
        'photos': photos,
        'program_name': 'Education',
        'is_officer': is_officer
    }
    return render(request, 'pages/programs/education.html', context)

def program_sigma_beta(request):
    """Sigma Beta Club program detail - officers can upload photos"""
    is_officer = request.user.is_authenticated and (request.user.is_staff or (hasattr(request.user, 'member_profile') and request.user.member_profile.is_officer))
    
    # Handle photo upload for officers
    if request.method == 'POST' and is_officer:
        if 'photo_upload' in request.FILES:
            photo = Photo(
                uploaded_by=request.user,
                image=request.FILES['photo_upload'],
                caption=request.POST.get('caption', ''),
                tags='sigma beta'  # Auto-tag as sigma beta
            )
            photo.save()
            messages.success(request, 'Photo uploaded successfully!')
            return redirect('program_sigma_beta')
    
    # Get photos tagged with sigma beta or youth-related keywords
    photos = Photo.objects.filter(
        tags__icontains='sigma beta'
    ).order_by('-created_at')[:8]
    
    context = {
        'photos': photos,
        'program_name': 'Sigma Beta Club',
        'is_officer': is_officer
    }
    return render(request, 'pages/programs/sigma_beta.html', context)

@login_required
def edit_program_photo(request, photo_id):
    """Edit a program photo's caption (for program page uploads)"""
    photo = get_object_or_404(Photo, pk=photo_id)
    
    # Check if user is officer
    is_officer = request.user.is_authenticated and (
        request.user.is_staff or 
        (hasattr(request.user, 'member_profile') and 
         request.user.member_profile.is_officer)
    )
    
    # Only allow editing own photos or if staff
    if photo.uploaded_by != request.user and not request.user.is_staff:
        messages.error(request, "You can only edit your own photos.")
        # Redirect to appropriate program page based on tags
        return redirect('program_business')
    
    if request.method == 'POST':
        photo.caption = request.POST.get('caption', '')
        photo.save()
        messages.success(request, 'Photo caption updated successfully!')
        # Determine redirect based on tags
        if 'business' in photo.tags.lower():
            return redirect('program_business')
        elif 'social' in photo.tags.lower() and 'action' in photo.tags.lower():
            return redirect('program_social_action')
        elif 'education' in photo.tags.lower():
            return redirect('program_education')
        elif 'sigma beta' in photo.tags.lower() or 'club' in photo.tags.lower():
            return redirect('program_sigma_beta')
        return redirect('program_business')
    
    context = {
        'photo': photo,
        'is_officer': is_officer
    }
    return render(request, 'pages/edit_program_photo.html', context)

@login_required
def delete_program_photo(request, photo_id):
    """Delete a program photo (for program page uploads)"""
    photo = get_object_or_404(Photo, pk=photo_id)
    
    # Check if user is officer
    is_officer = request.user.is_authenticated and (
        request.user.is_staff or 
        (hasattr(request.user, 'member_profile') and 
         request.user.member_profile.is_officer)
    )
    
    # Only allow deleting own photos or if staff
    if photo.uploaded_by != request.user and not request.user.is_staff:
        messages.error(request, "You can only delete your own photos.")
        # Redirect to appropriate program page
        return redirect('program_business')
    
    # Determine redirect based on tags before deleting
    if 'business' in photo.tags.lower():
        redirect_view = 'program_business'
    elif 'social' in photo.tags.lower() and 'action' in photo.tags.lower():
        redirect_view = 'program_social_action'
    elif 'education' in photo.tags.lower():
        redirect_view = 'program_education'
    elif 'sigma beta' in photo.tags.lower() or 'club' in photo.tags.lower():
        redirect_view = 'program_sigma_beta'
    else:
        redirect_view = 'program_business'
    
    if request.method == 'POST':
        # Delete the photo image file
        if photo.image:
            photo.image.delete()
        photo.delete()
        messages.success(request, 'Photo deleted successfully!')
        return redirect(redirect_view)
    
    context = {
        'photo': photo,
        'is_officer': is_officer
    }
    return render(request, 'pages/delete_program_photo.html', context)

def action(request):
    """Nu Gamma Sigma in Action page view"""
    return render(request, 'pages/action.html')

def signin(request):
    """Sign in page view"""
    return render(request, 'pages/signin.html')


def _validate_contact_form(name, email, message):
    """Validate contact form inputs and return list of errors"""
    errors = []
    if not name or len(name) < 2:
        errors.append("Name must be at least 2 characters long.")
    if not email or '@' not in email:
        errors.append("Please enter a valid email address.")
    if not message or len(message) < 10:
        errors.append("Message must be at least 10 characters long.")
    return errors


def _send_contact_email(name, email, message):
    """Send contact form email and return success status"""
    try:
        subject = f"Contact Form Submission from {name}"
        email_message = f"""
New contact form submission:

Name: {name}
Email: {email}

Message:
{message}

---
This email was sent from the Nu Gamma Sigma Chapter website contact form.
        """
        
        send_mail(
            subject=subject,
            message=email_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.CONTACT_EMAIL],
            fail_silently=False,
        )
        logger.info(f"Contact email sent successfully to {settings.CONTACT_EMAIL}")
        return True
    except Exception as e:
        logger.error(f"Failed to send contact email: {str(e)}")
        return False


def contact(request):
    """Contact form view with CSRF protection and validation"""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        message = request.POST.get('message', '').strip()
        
        # Validate form
        errors = _validate_contact_form(name, email, message)
        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            # Log the contact attempt
            logger.info(f"Contact form submission from: {name} ({email})")
            
            # Send email notification
            email_sent = _send_contact_email(name, email, message)
            if email_sent:
                messages.success(request, f"Thank you, {name}! Your message has been received. We'll get back to you soon.")
            else:
                messages.warning(request, f"Thank you, {name}! Your message was received, but there was an issue sending the email notification.")
            
            return redirect('home')
    
    return render(request, 'pages/contact.html')

def login_view(request):
    """Custom login view with security logging"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                logger.info(f"Successful login for user: {username}")
                messages.success(request, f"Welcome back, {username}!")
                
                next_url = request.GET.get('next', 'home')
                # Validate redirect URL to prevent open redirect vulnerability
                if not is_safe_redirect_url(next_url):
                    next_url = 'home'
                return redirect(next_url)
        else:
            logger.warning(f"Failed login attempt for username: {request.POST.get('username', 'unknown')}")
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    
    context = {
        'form': form,
    }
    return render(request, 'pages/login.html', context)

def logout_view(request):
    """Custom logout view with security logging"""
    if request.user.is_authenticated:
        username = request.user.username
        logout(request)
        logger.info(f"User logged out: {username}")
        messages.success(request, "You have been successfully logged out.")
    return redirect('home')


def _validate_invitation_code(invitation_code):
    """Validate invitation code and return (invitation, error_message) tuple"""
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
    """Check if email matches invitation"""
    if email.lower() != invitation.email.lower():
        return "Email address does not match the invitation code."
    return None


def _create_user_from_invitation(form, invitation, email, invitation_code):
    """Create user from validated form and invitation, or activate existing user"""
    username = form.cleaned_data.get('username')
    password = form.cleaned_data.get('password1')
    
    # Check if user already exists (case-insensitive search)
    try:
        user = User.objects.get(username__iexact=username)
        # User exists - just set their password and activate
        user.set_password(password)
        user.email = email
        if invitation.first_name:
            user.first_name = invitation.first_name
        if invitation.last_name:
            user.last_name = invitation.last_name
        user.is_active = True
        user.save()
        logger.info(f"Existing user activated with invitation: {user.username} (code: {invitation_code})")
    except User.DoesNotExist:
        # User doesn't exist - create new one
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
        logger.info(f"New user registered with invitation: {username} (code: {invitation_code})")
    
    # Create or update member profile if member_number exists
    if invitation.member_number:
        try:
            # Try to get existing profile by member_number
            member_profile = MemberProfile.objects.get(member_number=invitation.member_number)
            # Profile exists - update the user association if needed
            if member_profile.user != user:
                member_profile.user = user
            # Update status if not a special status
            if member_profile.status not in ['financial_life_member', 'non_financial_life_member', 'suspended']:
                member_profile.status = 'new_member'
            member_profile.save()
            logger.info(f"Updated existing MemberProfile {invitation.member_number} for user {username}")
        except MemberProfile.DoesNotExist:
            # No profile exists with this member_number - check if user has a profile without member_number
            try:
                member_profile = MemberProfile.objects.get(user=user)
                # User has a profile but no member_number - add it
                member_profile.member_number = invitation.member_number
                if member_profile.status not in ['financial_life_member', 'non_financial_life_member', 'suspended']:
                    member_profile.status = 'new_member'
                member_profile.save()
                logger.info(f"Added member_number {invitation.member_number} to existing profile for {username}")
            except MemberProfile.DoesNotExist:
                # No profile at all - create new one
                MemberProfile.objects.create(
                    user=user,
                    member_number=invitation.member_number,
                    status='new_member'
                )
                logger.info(f"Created new MemberProfile {invitation.member_number} for user {username}")
    
    # Mark invitation as used only after all operations succeed
    invitation.mark_as_used(user)
    
    return username


def _handle_signup_post(request, form):
    """Handle POST request for signup view"""
    invitation_code = request.POST.get('invitation_code', '').strip()
    
    # Validate invitation code
    invitation, error = _validate_invitation_code(invitation_code)
    if error:
        messages.error(request, error)
        return render(request, SIGNUP_TEMPLATE, {'form': form})
    
    # Validate email matches invitation
    email = request.POST.get('email', '').strip()
    error = _validate_invitation_email(invitation, email)
    if error:
        messages.error(request, error)
        return render(request, SIGNUP_TEMPLATE, {'form': form})
    
    # Process signup if form is valid
    if form.is_valid():
        username = _create_user_from_invitation(form, invitation, email, invitation_code)
        messages.success(request, f"Account created successfully for {username}! Please log in.")
        return redirect('login')
    
    # Show form errors
    for field, errors in form.errors.items():
        for error in errors:
            messages.error(request, f"{field}: {error}")
    return render(request, SIGNUP_TEMPLATE, {'form': form})


def signup_view(request):
    """User registration view with invitation code validation"""
    if request.user.is_authenticated:
        return redirect('home')
    
    form = InvitationSignupForm(request.POST) if request.method == 'POST' else InvitationSignupForm()
    
    if request.method == 'POST':
        return _handle_signup_post(request, form)
    
    return render(request, SIGNUP_TEMPLATE, {'form': form})

@login_required
@user_passes_test(lambda u: u.is_staff or (hasattr(u, 'member_profile') and u.member_profile.is_officer))
def add_leadership(request):
    """Add new chapter leadership member (admin/officers only)"""
    if request.method == 'POST':
        form = ChapterLeadershipForm(request.POST, request.FILES)
        if form.is_valid():
            leader = form.save()
            logger.info(f"Leadership member added: {leader.full_name} by {request.user.username}")
            messages.success(request, f"Successfully added {leader.full_name} to leadership!")
            return redirect('chapter_leadership')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ChapterLeadershipForm()
    
    context = {
        'form': form,
        'action': 'Add',
    }
    return render(request, 'pages/leadership_form.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff or (hasattr(u, 'member_profile') and u.member_profile.is_officer))
def edit_leadership(request, pk):
    """Edit chapter leadership member (admin/officers only)"""
    leader = get_object_or_404(ChapterLeadership, pk=pk)
    
    if request.method == 'POST':
        form = ChapterLeadershipForm(request.POST, request.FILES, instance=leader)
        if form.is_valid():
            leader = form.save()
            logger.info(f"Leadership member updated: {leader.full_name} by {request.user.username}")
            messages.success(request, f"Successfully updated {leader.full_name}!")
            return redirect('chapter_leadership')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ChapterLeadershipForm(instance=leader)
    
    context = {
        'form': form,
        'leader': leader,
        'action': 'Edit',
    }
    return render(request, 'pages/leadership_form.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff or (hasattr(u, 'member_profile') and u.member_profile.is_officer))
def delete_leadership(request, pk):
    """Delete chapter leadership member (admin/officers only)"""
    leader = get_object_or_404(ChapterLeadership, pk=pk)
    name = leader.full_name
    leader.delete()
    logger.info(f"Leadership member deleted: {name} by {request.user.username}")
    messages.success(request, f"Successfully deleted {name} from leadership.")
    return redirect('chapter_leadership')


@login_required
@user_passes_test(lambda u: u.is_staff or (hasattr(u, 'member_profile') and u.member_profile.is_officer))
def upload_leader_photo(request, pk):
    """Upload or update leader's profile photo (admin/officers only)"""
    leader = get_object_or_404(ChapterLeadership, pk=pk)
    
    if request.method == 'POST':
        if 'profile_image' in request.FILES:
            # Delete old image if exists
            if leader.profile_image:
                if os.path.exists(leader.profile_image.path):
                    os.remove(leader.profile_image.path)
            
            # Save new image
            leader.profile_image = request.FILES['profile_image']
            leader.save()
            logger.info(f"Leadership profile photo updated: {leader.full_name} by {request.user.username}")
            messages.success(request, f"Photo updated for {leader.full_name}!")
            return redirect('chapter_leadership')
        else:
            messages.error(request, "Please select an image to upload.")
    
    context = {
        'leader': leader,
    }
    return render(request, 'pages/portal/upload_leader_photo.html', context)


# ==================== INVITATION CODE MANAGEMENT ====================

@login_required
@user_passes_test(lambda u: u.is_staff)
def manage_invitations(request):
    """View and manage invitation codes (admin only)"""
    invitations = InvitationCode.objects.all().order_by('-created_at')
    
    # Separate active and used invitations
    active_invitations = [inv for inv in invitations if inv.is_valid()]
    used_invitations = invitations.filter(is_used=True)
    expired_invitations = [inv for inv in invitations if not inv.is_valid() and not inv.is_used]
    
    context = {
        'active_invitations': active_invitations,
        'used_invitations': used_invitations,
        'expired_invitations': expired_invitations,
    }
    return render(request, 'pages/manage_invitations.html', context)


@login_required
@user_passes_test(lambda u: u.is_staff)
def create_invitation(request):
    """Create new invitation code (admin only)"""
    import secrets
    
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        member_number = request.POST.get('member_number', '').strip()
        notes = request.POST.get('notes', '').strip()
        
        if not email:
            messages.error(request, "Email address is required.")
            return redirect('create_invitation')
        
        # Check if email already has an active invitation
        existing = InvitationCode.objects.filter(email=email, is_used=False).first()
        if existing and existing.is_valid():
            messages.warning(request, f"Active invitation already exists for {email}: {existing.code}")
            return redirect('manage_invitations')
        
        # Generate unique code
        code = secrets.token_urlsafe(16)[:20].upper().replace('_', '').replace('-', '')
        
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


@login_required
@user_passes_test(lambda u: u.is_staff)
def delete_invitation(request, pk):
    """Delete invitation code (admin only)"""
    invitation = get_object_or_404(InvitationCode, pk=pk)
    code = invitation.code
    invitation.delete()
    logger.info(f"Invitation deleted: {code} by {request.user.username}")
    messages.success(request, f"Invitation code {code} has been deleted.")
    return redirect('manage_invitations')


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
        messages.info(request, f"Active invitation already exists: <strong>{existing.code}</strong>")
    else:
        # Generate new invitation using helper function
        invitation = generate_invitation_for_member(user, member_profile, request.user)
        
        messages.success(
            request, 
            f"Invitation code generated: <strong>{invitation.code}</strong> "
            f"(Valid until {invitation.expires_at.strftime('%Y-%m-%d')})"
        )
    
    return redirect('member_roster')

    email = invitation.email
    invitation.delete()
    logger.info(f"Invitation deleted: {code} for {email} by {request.user.username}")
    messages.success(request, f"Invitation code {code} deleted.")
    return redirect('manage_invitations')


# ==================== MEMBER PORTAL VIEWS ====================

@login_required
def portal_dashboard(request):
    """Member portal dashboard"""
    try:
        member_profile = MemberProfile.objects.get(user=request.user)
    except MemberProfile.DoesNotExist:
        member_profile = None
    
    # Get recent announcements
    recent_announcements = Announcement.objects.filter(
        is_active=True,
        publish_date__lte=timezone.now()
    ).order_by('-is_pinned', '-publish_date')[:5]
    
    # Get viewed announcement IDs for current user
    viewed_ids = AnnouncementView.objects.filter(
        user=request.user
    ).values_list('announcement_id', flat=True)
    
    # Mark announcements as new or not
    for announcement in recent_announcements:
        announcement.is_new = announcement.id not in viewed_ids
    
    # Get count of unread announcements
    total_announcements = Announcement.objects.filter(
        is_active=True,
        publish_date__lte=timezone.now()
    ).count()
    unread_announcements = total_announcements - AnnouncementView.objects.filter(
        user=request.user
    ).count()
    
    # Get upcoming events
    upcoming_events = Event.objects.filter(
        start_date__gte=timezone.now()
    ).order_by('start_date')[:5]
    
    # Get unread messages count
    unread_count = Message.objects.filter(
        recipient=request.user, 
        is_read=False
    ).count()
    
    # Get member stats
    if member_profile:
        total_dues = DuesPayment.objects.filter(member=member_profile).count()
        total_events = EventAttendance.objects.filter(member=member_profile).count()
        total_points = EventAttendance.objects.filter(
            member=member_profile
        ).aggregate(total=Sum('points'))['total'] or 0
    else:
        total_dues = total_events = total_points = 0
    
    context = {
        'member_profile': member_profile,
        'recent_announcements': recent_announcements,
        'upcoming_events': upcoming_events,
        'unread_count': unread_count,
        'unread_announcements': unread_announcements,
        'total_dues': total_dues,
        'total_events': total_events,
        'total_points': total_points,
    }
    return render(request, 'pages/portal/dashboard.html', context)


@login_required
def member_roster(request):
    """View all active members (financial and life members)"""
    members = MemberProfile.objects.financial_members().select_related('user').order_by('user__last_name')
    
    context = {
        'members': members,
        'is_staff': request.user.is_staff,
    }
    return render(request, 'pages/portal/roster.html', context)


@login_required
@user_passes_test(lambda u: u.is_staff)
def create_member(request):
    """Create a new member profile (admin only)"""
    if request.method == 'POST':
        form = MemberProfileForm(request.POST, request.FILES)
        if form.is_valid():
            # Create user account with random password
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                password=User.objects.make_random_password()
            )
            user.is_active = True  # Set active so they can log in after signup
            user.save()
            
            # Create member profile
            member_profile = form.save(commit=False)
            member_profile.user = user
            member_profile.save()
            
            # Handle leadership position if selected
            leadership_position = form.cleaned_data.get('leadership_position')
            if leadership_position:
                ChapterLeadership.objects.create(
                    position=leadership_position,
                    full_name=user.get_full_name() or user.username,
                    email=user.email,
                    phone=member_profile.phone,
                    is_active=True
                )
            
            # Generate invitation code using helper function
            invitation = generate_invitation_for_member(user, member_profile, request.user)
            
            logger.info(f"Member created: {member_profile.member_number} by {request.user.username}")
            
            # Show success message with invitation code
            messages.success(
                request, 
                f"Successfully created member profile for {user.get_full_name()}! "
                f"Invitation Code: <strong>{invitation.code}</strong> "
                f"(Send this code to {user.email} so they can set their password)"
            )
            return redirect('member_roster')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = MemberProfileForm()
    
    context = {
        'form': form,
        'action': 'Create',
        'title': 'Create Member Profile'
    }
    return render(request, 'pages/portal/member_form.html', context)


@login_required
@user_passes_test(lambda u: u.is_staff)
def edit_member(request, pk):
    """Edit member profile (admin only)"""
    member_profile = get_object_or_404(MemberProfile, pk=pk)
    
    if request.method == 'POST':
        form = MemberProfileForm(request.POST, request.FILES, instance=member_profile, user_instance=member_profile.user)
        if form.is_valid():
            # Update user information
            user = member_profile.user
            user.username = form.cleaned_data['username']  # Allow username change
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            user.save()
            
            # Update member profile
            member_profile = form.save()
            
            # Handle leadership position
            leadership_position = form.cleaned_data.get('leadership_position')
            # Remove existing leadership positions for this member
            ChapterLeadership.objects.filter(email__iexact=user.email).delete()
            # Add new leadership position if selected
            if leadership_position:
                ChapterLeadership.objects.create(
                    position=leadership_position,
                    full_name=user.get_full_name() or user.username,
                    email=user.email,
                    phone=member_profile.phone,
                    is_active=True
                )
            
            logger.info(f"Member updated: {member_profile.member_number} by {request.user.username}")
            messages.success(request, f"Successfully updated {user.get_full_name()}'s profile!")
            return redirect('member_roster')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
            # Form stays with the POST data and user_instance for re-display
    else:
        form = MemberProfileForm(instance=member_profile, user_instance=member_profile.user)
        # Pre-select leadership position if member is an officer
        existing_leadership = ChapterLeadership.objects.filter(email__iexact=member_profile.user.email, is_active=True).first()
        if existing_leadership:
            form.fields['leadership_position'].initial = existing_leadership.position
    
    context = {
        'form': form,
        'action': 'Edit',
        'title': 'Edit Member Profile',
        'member_profile': member_profile
    }
    return render(request, 'pages/portal/member_form.html', context)
    
    context = {
        'form': form,
        'member_profile': member_profile,
        'action': 'Edit',
        'title': f'Edit {member_profile.user.get_full_name()}'
    }
    return render(request, 'pages/portal/member_form.html', context)


@login_required
@user_passes_test(lambda u: u.is_staff)
def delete_member(request, pk):
    """Delete member profile (admin only)"""
    member_profile = get_object_or_404(MemberProfile, pk=pk)
    user = member_profile.user
    name = user.get_full_name() or user.username
    
    # Delete both user and profile (cascade will handle profile)
    user.delete()
    
    logger.info(f"Member deleted: {name} by {request.user.username}")
    messages.success(request, f"Successfully deleted member profile for {name}.")
    return redirect('member_roster')


def _validate_csv_row(row, row_num):
    """Validate a single CSV row and return (username, email, member_number, errors, should_skip)"""
    errors = []
    should_skip = False
    
    # Support multiple CSV formats:
    # - Standard: member_number, first_name, last_name
    # - IHQ Export 1: Member#, First Name, Last Name
    # - IHQ Export 2: MAJOR_KEY, FIRST_NAME, LAST_NAME
    # - IHQ Export 3 (with textbox columns): textbox# columns
    
    member_number = (row.get('member_number', '').strip() or 
                    row.get('Member#', '').strip() or 
                    row.get('MAJOR_KEY', '').strip())
    first_name = (row.get('first_name', '').strip() or 
                 row.get('First Name', '').strip() or 
                 row.get('FIRST_NAME', '').strip())
    last_name = (row.get('last_name', '').strip() or 
                row.get('Last Name', '').strip() or 
                row.get('LAST_NAME', '').strip())
    
    # Handle IHQ textbox format - extract from textbox columns
    # The member roster CSV has textbox7 with name/address info
    if not member_number or not first_name or not last_name:
        # Try to parse from textbox7 (contains name and address)
        if row.get('textbox7'):
            textbox7_lines = row.get('textbox7', '').strip().split('\n')
            if textbox7_lines and len(textbox7_lines) > 0:
                # First line is typically name
                name_parts = textbox7_lines[0].strip().split()
                if not first_name and name_parts:
                    first_name = name_parts[0]
                if not last_name and len(name_parts) > 1:
                    last_name = ' '.join(name_parts[1:])
        
        # Try textbox3 (sometimes has member number)
        if not member_number and row.get('textbox3'):
            member_number = row.get('textbox3', '').strip()
    
    email = row.get('email', '').strip() or row.get('EMAIL', '').strip()
    username = row.get('username', '').strip()
    
    # Auto-generate username if not provided
    if not username:
        if member_number:
            # Use member number as username (e.g., "member_12345")
            username = f"member_{member_number}"
        elif first_name and last_name:
            # Use first.last as username
            username = f"{first_name}.{last_name}".lower().replace(' ', '_')
        else:
            errors.append(f"Row {row_num}: Cannot generate username - need member_number or first/last name")
            return None, email, member_number, errors, False
    
    # Email is now optional
    if not member_number:
        errors.append(f"Row {row_num}: Member number is required")
        return username, email, member_number, errors, False
    
    # Check for duplicates - skip instead of error
    if member_number and MemberProfile.objects.filter(member_number=member_number).exists():
        # Silently skip this row - member already exists
        should_skip = True
        return username, email, member_number, [], should_skip
    
    if username and User.objects.filter(username=username).exists():
        # Username exists but member_number doesn't - this is an error
        errors.append(f"Row {row_num}: Username '{username}' already exists but member number is different")
        return username, email, member_number, errors, False
    
    return username, email, member_number, errors, should_skip


def _parse_initiation_date(date_str, row_num, username):
    """Parse initiation date from CSV and return (date, error)"""
    if not date_str.strip():
        return None, None
    
    for fmt in ['%Y-%m-%d', '%m/%d/%Y']:
        try:
            return datetime.strptime(date_str.strip(), fmt).date(), None
        except ValueError:
            continue
    
    return None, f"Row {row_num}: Invalid date format for '{username}'. Use YYYY-MM-DD or MM/DD/YYYY"


def _create_member_from_row(row, username, email, member_number, initiation_date):
    """Create user and member profile from CSV row"""
    # Support multiple CSV formats
    first_name = (row.get('first_name', '').strip() or 
                 row.get('First Name', '').strip() or 
                 row.get('FIRST_NAME', '').strip())
    last_name = (row.get('last_name', '').strip() or 
                row.get('Last Name', '').strip() or 
                row.get('LAST_NAME', '').strip())
    
    # Handle IHQ textbox format - extract name from textbox7
    if (not first_name or not last_name) and row.get('textbox7'):
        textbox7_lines = row.get('textbox7', '').strip().split('\n')
        if textbox7_lines and len(textbox7_lines) > 0:
            name_parts = textbox7_lines[0].strip().split()
            if not first_name and name_parts:
                first_name = name_parts[0]
            if not last_name and len(name_parts) > 1:
                last_name = ' '.join(name_parts[1:])
    
    # Create user (email can be empty)
    user = User.objects.create_user(
        username=username,
        email=email or '',  # Empty string if no email
        first_name=first_name,
        last_name=last_name,
        password=User.objects.make_random_password()
    )
    
    # Parse dues_current (only from custom format)
    dues_current = row.get('dues_current', '').strip().lower() in ['true', 'yes', '1', 'y', 'paid', 'current']
    
    # Auto-detect member status based on member number
    # If Member# contains 'LM', they are a life member; otherwise financial
    if 'LM' in member_number.upper():
        auto_status = 'financial_life_member'
        dues_current = True  # Life members always have dues current
    else:
        auto_status = 'financial'
        dues_current = True  # All imported members are financial
    
    # Allow custom status from CSV to override, or use auto-detected status
    status = row.get('status', '').strip() or auto_status
    
    # Create member profile
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


def _process_csv_row(row, row_num):
    """Process a single CSV row and return (success, errors, skipped)"""
    errors = []
    
    # Validate row
    username, email, member_number, validation_errors, should_skip = _validate_csv_row(row, row_num)
    
    # Skip if duplicate
    if should_skip:
        return False, [], True  # Not success, no errors, but skipped
    
    # Return errors if validation failed
    if validation_errors:
        return False, validation_errors, False
    
    # Parse initiation date
    initiation_date, date_error = _parse_initiation_date(row.get('initiation_date', ''), row_num, username)
    if date_error:
        errors.append(date_error)
    
    # Create member
    _create_member_from_row(row, username, email, member_number, initiation_date)
    return True, errors, False


def _process_csv_file(csv_reader, username):
    """Process all rows in CSV file and return results"""
    success_count = 0
    error_count = 0
    skipped_count = 0
    errors = []
    
    for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 (row 1 is header)
        try:
            success, row_errors, skipped = _process_csv_row(row, row_num)
            if skipped:
                skipped_count += 1
            elif success:
                success_count += 1
            else:
                error_count += 1
            errors.extend(row_errors)
        except Exception as e:
            errors.append(f"Row {row_num}: {str(e)}")
            error_count += 1
            logger.error(f"Error importing member at row {row_num}: {str(e)}")
    
    logger.info(f"CSV import completed by {username}: {success_count} successful, {error_count} failed, {skipped_count} skipped")
    return success_count, error_count, skipped_count, errors


def _show_import_results(request, success_count, error_count, skipped_count, errors):
    """Display import results to user"""
    if success_count > 0:
        messages.success(request, f"Successfully imported {success_count} new member(s)!")
    
    if skipped_count > 0:
        messages.info(request, f"Skipped {skipped_count} member(s) that already exist in the system.")
    
    if error_count > 0:
        messages.warning(request, f"Failed to import {error_count} member(s). See errors below.")
        for error in errors[:10]:  # Show first 10 errors
            messages.error(request, error)
        if len(errors) > 10:
            messages.error(request, f"... and {len(errors) - 10} more errors")


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
        # Read and decode CSV file, removing BOM if present
        decoded_file = csv_file.read().decode('utf-8-sig')  # utf-8-sig removes BOM
        lines = decoded_file.strip().split('\n')
        
        # Skip decorative header lines (like "textbox1" and title lines)
        # Find the actual CSV header row (contains MAJOR_KEY, FIRST_NAME, LAST_NAME, etc.)
        header_row_index = 0
        for i, line in enumerate(lines):
            if 'MAJOR_KEY' in line or ('FIRST_NAME' in line and 'LAST_NAME' in line):
                header_row_index = i
                break
        
        # Create StringIO from the actual data starting from header row
        csv_data = '\n'.join(lines[header_row_index:])
        io_string = io.StringIO(csv_data)
        csv_reader = csv.DictReader(io_string)
        
        # Debug: Log detected field names
        if csv_reader.fieldnames:
            logger.info(f"CSV field names detected: {csv_reader.fieldnames}")
            messages.info(request, f"CSV columns detected: {', '.join(csv_reader.fieldnames)}")
        
        # Process CSV
        success_count, error_count, skipped_count, errors = _process_csv_file(csv_reader, request.user.username)
        
        # Show results
        _show_import_results(request, success_count, error_count, skipped_count, errors)
        
        if success_count > 0:
            return redirect('member_roster')
        
    except Exception as e:
        logger.error(f"CSV import error: {str(e)}")
        messages.error(request, f"Error processing CSV file: {str(e)}")
    
    return render(request, 'pages/portal/import_members.html')


# ============================================================================
# OFFICER IMPORT FUNCTIONS
# ============================================================================

def _validate_officer_csv_row(row, row_num):
    """Validate a single officer CSV row and return (data_dict, errors, should_skip)"""
    errors = []
    should_skip = False
    
    # Support multiple CSV formats
    # Standard format: full_name, position, email columns
    full_name = (row.get('full_name', '').strip() or 
                row.get('Full Name', '').strip() or 
                row.get('FULL_NAME', '').strip())
    position = (row.get('position', '').strip() or 
               row.get('Position', '').strip() or 
               row.get('POSITION', '').strip())
    email = (row.get('email', '').strip() or 
            row.get('Email', '').strip() or 
            row.get('EMAIL', '').strip())
    phone = (row.get('phone', '').strip() or 
            row.get('Phone', '').strip() or 
            row.get('PHONE', '').strip())
    
    # IHQ format: textbox5 (position info), textbox7 (name/address), textbox11 (email/phone)
    if not full_name and row.get('textbox7'):
        # Extract name from textbox7 (first line)
        textbox7_lines = row.get('textbox7', '').strip().split('\n')
        if textbox7_lines and textbox7_lines[0].strip():
            full_name = textbox7_lines[0].strip()
            # Remove "Bro. " prefix if present
            if full_name.startswith('Bro. '):
                full_name = full_name[5:]
    
    if not position and row.get('textbox5'):
        # Extract position from textbox5 (first line, before "Effective Date")
        textbox5_lines = row.get('textbox5', '').strip().split('\n')
        if textbox5_lines and textbox5_lines[0].strip():
            position = textbox5_lines[0].strip()
    
    if not email and row.get('textbox11'):
        # Extract email from textbox11 (line starting with "Email:")
        textbox11_lines = row.get('textbox11', '').strip().split('\n')
        for line in textbox11_lines:
            if line.strip().startswith('Email:'):
                email = line.replace('Email:', '').strip()
                break
    
    if not phone and row.get('textbox11'):
        # Extract phone from textbox11 (Home Phone or Work Phone)
        textbox11_lines = row.get('textbox11', '').strip().split('\n')
        for line in textbox11_lines:
            if 'Phone:' in line:
                phone = line.split('Phone:', 1)[1].strip()
                break
    
    # Skip vacant positions
    if 'Vacant Position' in full_name or not full_name:
        should_skip = True
        return None, [], should_skip
    
    if not position:
        errors.append(f"Row {row_num}: Position is required")
        return None, errors, False
    
    # Check for duplicates - skip if same person in same position
    if ChapterLeadership.objects.filter(full_name=full_name, position=position, is_active=True).exists():
        should_skip = True
        return None, [], should_skip
    
    data = {
        'full_name': full_name,
        'position': position,
        'email': email,
        'phone': phone,
        'bio': row.get('bio', '').strip() or row.get('Bio', '').strip() or row.get('BIO', '').strip(),
        'position_custom': row.get('position_custom', '').strip(),
        'display_order': row.get('display_order', '').strip() or '0',
    }
    
    return data, errors, should_skip


def _parse_officer_date(date_str):
    """Parse date from CSV (returns None if empty or invalid)"""
    if not date_str or not date_str.strip():
        return None
    
    for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%Y/%m/%d']:
        try:
            return datetime.strptime(date_str.strip(), fmt).date()
        except ValueError:
            continue
    return None


def _create_officer_from_row(data):
    """Create ChapterLeadership record from validated data"""
    # Map common position names to model choices
    position_map = {
        'president': 'president',
        '1st vice president': 'vice_president_1st',
        '2nd vice president': 'vice_president_2nd',
        'vice president': 'vice_president_1st',  # Default to 1st if not specified
        'vp': 'vice_president_1st',
        'secretary': 'secretary',
        'financial secretary': 'secretary',
        'treasurer': 'treasurer',
        'parliamentarian': 'parliamentarian',
        'chaplain': 'chaplain',
        'historian': 'historian',
        'sergeant at arms': 'sergeant_at_arms',
        'board member': 'board_member',
        'board': 'board_member',
    }
    
    position_lower = data['position'].lower()
    position_value = position_map.get(position_lower, 'other')
    
    # For "other" positions, save the original position name as custom
    position_custom = ''
    if position_value == 'other':
        position_custom = data['position']
    elif data.get('position_custom'):
        position_custom = data.get('position_custom', '')
    
    officer = ChapterLeadership.objects.create(
        full_name=data['full_name'],
        position=position_value,
        position_custom=position_custom,
        email=data.get('email', ''),
        phone=data.get('phone', ''),
        bio=data.get('bio', ''),
        display_order=int(data.get('display_order', 0)),
        is_active=True
    )
    
    return officer


def _process_officer_csv_row(row, row_num):
    """Process a single officer CSV row"""
    # Validate row
    data, errors, should_skip = _validate_officer_csv_row(row, row_num)
    
    if should_skip:
        return True, [], True
    
    if errors:
        return False, errors, False
    
    # Create officer
    _create_officer_from_row(data)
    return True, [], False


def _process_officer_csv_file(csv_reader):
    """Process all rows in officer CSV file"""
    success_count = 0
    error_count = 0
    skipped_count = 0
    errors = []
    
    for row_num, row in enumerate(csv_reader, start=2):
        try:
            success, row_errors, skipped = _process_officer_csv_row(row, row_num)
            if skipped:
                skipped_count += 1
            elif success:
                success_count += 1
            else:
                error_count += 1
            errors.extend(row_errors)
        except Exception as e:
            errors.append(f"Row {row_num}: {str(e)}")
            error_count += 1
            logger.error(f"Error importing officer at row {row_num}: {str(e)}")
    
    logger.info(f"Officer CSV import completed: {success_count} successful, {error_count} failed, {skipped_count} skipped")
    return success_count, error_count, skipped_count, errors


@login_required
@user_passes_test(lambda u: u.is_staff or (hasattr(u, 'member_profile') and u.member_profile.is_officer))
def import_officers(request):
    """Import officers from CSV file (admin/officers only)"""
    if request.method != 'POST' or not request.FILES.get('csv_file'):
        return render(request, 'pages/portal/import_officers.html')
    
    csv_file = request.FILES['csv_file']
    
    # Validate file extension
    if not csv_file.name.endswith('.csv'):
        messages.error(request, "Please upload a CSV file.")
        return redirect('import_officers')
    
    try:
        # Read and decode CSV file, removing BOM if present
        decoded_file = csv_file.read().decode('utf-8-sig')  # utf-8-sig removes BOM
        io_string = io.StringIO(decoded_file)
        csv_reader = csv.DictReader(io_string)
        
        # Debug: Log detected field names
        if csv_reader.fieldnames:
            logger.info(f"Officer CSV field names detected: {csv_reader.fieldnames}")
            messages.info(request, f"CSV columns detected: {', '.join(csv_reader.fieldnames)}")
        
        # Process CSV
        success_count, error_count, skipped_count, errors = _process_officer_csv_file(csv_reader)
        
        # Show results
        _show_import_results(request, success_count, error_count, skipped_count, errors)
        
        if success_count > 0:
            return redirect('chapter_leadership')
        
    except Exception as e:
        logger.error(f"Officer CSV import error: {str(e)}")
        messages.error(request, f"Error processing CSV file: {str(e)}")
    
    return render(request, 'pages/portal/import_officers.html')


@login_required
def member_profile(request, username):
    """View individual member profile with comments"""
    profile_user = get_object_or_404(User, username=username)
    member_profile = get_object_or_404(MemberProfile, user=profile_user)
    
    # Get profile comments (top-level only)
    comments = ProfileComment.objects.filter(
        profile=member_profile,
        parent_comment=None
    ).select_related('author').prefetch_related('replies', 'likes').order_by('-created_at')
    
    # Add comment if POST
    if request.method == 'POST' and 'comment_content' in request.POST:
        content = request.POST.get('comment_content', '').strip()
        parent_id = request.POST.get('parent_id')
        
        if content:
            parent_comment = None
            if parent_id:
                parent_comment = ProfileComment.objects.filter(id=parent_id).first()
            
            ProfileComment.objects.create(
                profile=member_profile,
                author=request.user,
                content=content,
                parent_comment=parent_comment
            )
            messages.success(request, "Comment posted!")
            return redirect('member_profile', username=username)
    
    context = {
        'profile_user': profile_user,
        'member_profile': member_profile,
        'comments': comments,
    }
    return render(request, 'pages/portal/profile.html', context)


@login_required
def like_comment(request, comment_id):
    """Like/unlike a profile comment"""
    comment = get_object_or_404(ProfileComment, id=comment_id)
    
    # Check if already liked
    existing_like = CommentLike.objects.filter(comment=comment, user=request.user).first()
    
    if existing_like:
        existing_like.delete()
        liked = False
    else:
        CommentLike.objects.create(comment=comment, user=request.user)
        liked = True
    
    like_count = comment.likes.count()
    
    return JsonResponse({
        'liked': liked,
        'like_count': like_count
    })


@login_required
def dues_view(request):
    """View dues payments"""
    # If user is staff/admin, redirect to the dues management page
    if request.user.is_staff:
        return redirect('dues_and_payments')
    
    try:
        member_profile = MemberProfile.objects.get(user=request.user)
        dues_payments = DuesPayment.objects.filter(
            member=member_profile
        ).order_by('-payment_date')
    except MemberProfile.DoesNotExist:
        member_profile = None
        dues_payments = []
    
    context = {
        'member_profile': member_profile,
        'dues_payments': dues_payments,
    }
    return render(request, 'pages/portal/dues.html', context)


@login_required
def announcements_view(request):
    """View all announcements"""
    announcements = Announcement.objects.filter(
        is_active=True,
        publish_date__lte=timezone.now()
    ).select_related('author').order_by('-is_pinned', '-publish_date')
    
    # Get viewed announcement IDs for current user
    viewed_ids = AnnouncementView.objects.filter(
        user=request.user
    ).values_list('announcement_id', flat=True)
    
    # Mark announcements as new or not and track views
    for announcement in announcements:
        announcement.is_new = announcement.id not in viewed_ids
        # Mark as viewed when user visits this page
        AnnouncementView.objects.get_or_create(
            user=request.user,
            announcement=announcement
        )
    
    context = {
        'announcements': announcements,
    }
    return render(request, 'pages/portal/announcements.html', context)


@login_required
def documents_view(request):
    """View and download documents with category filtering and search"""
    try:
        member_profile = MemberProfile.objects.get(user=request.user)
        # Check if user is an officer by matching email in ChapterLeadership
        is_officer = ChapterLeadership.objects.filter(
            email__iexact=request.user.email, 
            is_active=True
        ).exists() if request.user.email else False
        # Check if user is a financial member
        is_financial = member_profile.status in ['financial', 'financial_life_member']
    except MemberProfile.DoesNotExist:
        is_officer = False
        is_financial = False
    
    # Staff always have officer privileges
    if request.user.is_staff:
        is_officer = True
    
    # Financial members and officers can view documents, staff can always view
    if is_financial or is_officer or request.user.is_staff:
        # Show all public documents or documents they have access to
        documents = Document.objects.filter(
            Q(is_public=True) | Q(requires_officer=False)
        )
        # Officers and staff see all documents including restricted ones
        if is_officer or request.user.is_staff:
            documents = Document.objects.all()
    else:
        # Non-financial members see only public documents
        documents = Document.objects.filter(is_public=True)
    
    # Get filter parameters
    category_filter = request.GET.get('category', '')
    search_query = request.GET.get('search', '')
    
    # Apply category filter
    if category_filter:
        documents = documents.filter(category=category_filter)
    
    # Apply search filter
    if search_query:
        documents = documents.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    documents = documents.select_related('uploaded_by').order_by('category', '-created_at')
    
    # Group documents by category for table display
    from collections import defaultdict
    documents_by_category = defaultdict(list)
    for doc in documents:
        documents_by_category[doc.category].append(doc)
    
    context = {
        'documents': documents,
        'documents_by_category': dict(documents_by_category),
        'categories': Document.CATEGORY_CHOICES,
        'selected_category': category_filter,
        'search_query': search_query,
        'is_officer': is_officer,  # Controls CRUD buttons in template
        'is_financial': is_financial,
    }
    return render(request, 'pages/portal/documents.html', context)


@login_required
def create_document(request):
    """Create a new document (officers and staff only)"""
    # Check if user is an officer or staff
    is_officer = ChapterLeadership.objects.filter(
        email__iexact=request.user.email,
        is_active=True
    ).exists() or request.user.is_staff
    
    if not is_officer:
        messages.error(request, "Only officers can upload documents.")
        return redirect('documents_view')
    
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.uploaded_by = request.user
            document.save()
            messages.success(request, f"Document '{document.title}' uploaded successfully!")
            return redirect('documents_view')
    else:
        form = DocumentForm()
    
    context = {
        'form': form,
    }
    return render(request, 'pages/portal/create_document.html', context)


@login_required
def edit_document(request, document_id):
    """Edit an existing document (officers and staff only)"""
    document = get_object_or_404(Document, id=document_id)
    
    # Check if user is an officer or staff
    is_officer = ChapterLeadership.objects.filter(
        email__iexact=request.user.email,
        is_active=True
    ).exists() or request.user.is_staff
    
    if not is_officer:
        messages.error(request, "Only officers can edit documents.")
        return redirect('documents_view')
    
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES, instance=document)
        if form.is_valid():
            form.save()
            messages.success(request, f"Document '{document.title}' updated successfully!")
            return redirect('documents_view')
    else:
        form = DocumentForm(instance=document)
    
    context = {
        'form': form,
        'document': document,
    }
    return render(request, 'pages/portal/edit_document.html', context)


@login_required
def delete_document(request, document_id):
    """Delete a document (officers and staff only)"""
    document = get_object_or_404(Document, id=document_id)
    
    # Check if user is an officer or staff
    is_officer = ChapterLeadership.objects.filter(
        email__iexact=request.user.email,
        is_active=True
    ).exists() or request.user.is_staff
    
    if not is_officer:
        messages.error(request, "Only officers can delete documents.")
        return redirect('documents_view')
    
    document_title = document.title
    # Delete the file from storage
    if document.file:
        document.file.delete()
    document.delete()
    messages.success(request, f"Document '{document_title}' deleted successfully!")
    return redirect('documents_view')


@login_required
def messages_inbox(request):
    """View inbox messages"""
    messages_list = Message.objects.filter(
        recipient=request.user
    ).select_related('sender').order_by('-created_at')
    
    context = {
        'messages_list': messages_list,
    }
    return render(request, 'pages/portal/inbox.html', context)


@login_required
def message_detail(request, message_id):
    """View single message and mark as read"""
    message = get_object_or_404(Message, id=message_id, recipient=request.user)
    message.mark_as_read()
    
    # Get replies
    replies = Message.objects.filter(
        parent_message=message
    ).select_related('sender').order_by('created_at')
    
    context = {
        'message': message,
        'replies': replies,
    }
    return render(request, 'pages/portal/message_detail.html', context)


@login_required
def send_message(request, recipient_username=None):
    """Send a new message"""
    recipient = None
    if recipient_username:
        recipient = get_object_or_404(User, username=recipient_username)
    
    if request.method == 'POST':
        recipient_id = request.POST.get('recipient')
        subject = request.POST.get('subject', '').strip()
        content = request.POST.get('content', '').strip()
        parent_id = request.POST.get('parent_id')
        
        if recipient_id and content:
            recipient_user = User.objects.get(id=recipient_id)
            parent_message = None
            if parent_id:
                parent_message = Message.objects.filter(id=parent_id).first()
            
            Message.objects.create(
                sender=request.user,
                recipient=recipient_user,
                subject=subject,
                content=content,
                parent_message=parent_message
            )
            messages.success(request, f"Message sent to {recipient_user.username}!")
            return redirect('messages_inbox')
    
    # Get all members for recipient selection
    all_members = User.objects.exclude(id=request.user.id).order_by('username')
    
    context = {
        'recipient': recipient,
        'all_members': all_members,
    }
    return render(request, 'pages/portal/send_message.html', context)


@login_required
def attendance_view(request):
    """View event attendance records"""
    # If user is staff/admin, redirect to event management
    if request.user.is_staff:
        return redirect('events')
    
    try:
        member_profile = MemberProfile.objects.get(user=request.user)
        attendance_records = EventAttendance.objects.filter(
            member=member_profile
        ).select_related('event').order_by('-event__start_date')
        
        total_points = attendance_records.aggregate(
            total=Sum('points')
        )['total'] or 0
    except MemberProfile.DoesNotExist:
        member_profile = None
        attendance_records = []
        total_points = 0
    
    context = {
        'member_profile': member_profile,
        'attendance_records': attendance_records,
        'total_points': total_points,
    }
    return render(request, 'pages/portal/attendance.html', context)


@login_required
@user_passes_test(lambda u: u.is_staff or (hasattr(u, 'member_profile') and u.member_profile.is_officer))
def manage_attendance(request):
    """Officer view to manage event attendance records"""
    # Get filter parameters
    event_filter = request.GET.get('event', '')
    member_search = request.GET.get('member', '').strip()
    status_filter = request.GET.get('status', '')
    
    # Base queryset
    attendance_records = EventAttendance.objects.all().select_related(
        'event', 'member', 'member__user'
    ).order_by('-event__start_date')
    
    # Get events for filter dropdown
    events = Event.objects.all().order_by('-start_date')
    
    # Apply filters
    if event_filter:
        attendance_records = attendance_records.filter(event_id=event_filter)
    
    if member_search:
        attendance_records = attendance_records.filter(
            member__user__first_name__icontains=member_search
        ) | attendance_records.filter(
            member__user__last_name__icontains=member_search
        ) | attendance_records.filter(
            member__member_number__icontains=member_search
        )
    
    if status_filter:
        attendance_records = attendance_records.filter(status=status_filter)
    
    context = {
        'attendance_records': attendance_records,
        'events': events,
        'event_filter': event_filter,
        'member_search': member_search,
        'status_filter': status_filter,
        'status_choices': EventAttendance.ATTENDANCE_STATUS_CHOICES,
        'record_count': attendance_records.count(),
    }
    return render(request, 'pages/portal/manage_attendance.html', context)


@login_required
@user_passes_test(lambda u: u.is_staff or (hasattr(u, 'member_profile') and u.member_profile.is_officer))
def add_attendance(request):
    """Officer view to add attendance record"""
    if request.method == 'POST':
        event_id = request.POST.get('event')
        member_id = request.POST.get('member')
        status = request.POST.get('status', 'present')
        points = request.POST.get('points', 0)
        notes = request.POST.get('notes', '')
        rsvp_status = request.POST.get('rsvp_status') == 'on'
        
        try:
            event = Event.objects.get(id=event_id)
            member = MemberProfile.objects.get(id=member_id)
            
            # Check if record already exists
            attendance, created = EventAttendance.objects.get_or_create(
                event=event,
                member=member,
                defaults={
                    'status': status,
                    'points': int(points) if points else 0,
                    'notes': notes,
                    'rsvp_status': rsvp_status,
                }
            )
            
            if not created:
                # Update existing record
                attendance.status = status
                attendance.points = int(points) if points else 0
                attendance.notes = notes
                attendance.rsvp_status = rsvp_status
                attendance.save()
                messages.success(request, f'Attendance updated for {member.user.get_full_name()}!')
            else:
                messages.success(request, f'Attendance record created for {member.user.get_full_name()}!')
            
            return redirect('manage_attendance')
        except Event.DoesNotExist:
            messages.error(request, 'Event not found.')
        except MemberProfile.DoesNotExist:
            messages.error(request, 'Member not found.')
    
    # GET request - show form
    events = Event.objects.all().order_by('-start_date')
    members = MemberProfile.objects.all().select_related('user').order_by('user__last_name')
    
    context = {
        'events': events,
        'members': members,
        'status_choices': EventAttendance.ATTENDANCE_STATUS_CHOICES,
    }
    return render(request, 'pages/portal/attendance_form.html', context)


@login_required
@user_passes_test(lambda u: u.is_staff or (hasattr(u, 'member_profile') and u.member_profile.is_officer))
def edit_attendance(request, pk):
    """Officer view to edit attendance record"""
    attendance = get_object_or_404(EventAttendance, pk=pk)
    
    if request.method == 'POST':
        attendance.status = request.POST.get('status', attendance.status)
        attendance.points = int(request.POST.get('points', attendance.points) or 0)
        attendance.notes = request.POST.get('notes', attendance.notes)
        attendance.rsvp_status = request.POST.get('rsvp_status') == 'on'
        attendance.save()
        
        messages.success(request, 'Attendance record updated successfully!')
        return redirect('manage_attendance')
    
    context = {
        'attendance': attendance,
        'status_choices': EventAttendance.ATTENDANCE_STATUS_CHOICES,
    }
    return render(request, 'pages/portal/attendance_form.html', context)


@login_required
@user_passes_test(lambda u: u.is_staff or (hasattr(u, 'member_profile') and u.member_profile.is_officer))
def delete_attendance(request, pk):
    """Officer view to delete attendance record"""
    attendance = get_object_or_404(EventAttendance, pk=pk)
    
    if request.method == 'POST':
        member_name = attendance.member.user.get_full_name()
        event_name = attendance.event.title
        attendance.delete()
        messages.success(request, f'Deleted attendance for {member_name} at {event_name}')
        return redirect('manage_attendance')
    
    context = {
        'attendance': attendance,
    }
    return render(request, 'pages/portal/attendance_confirm_delete.html', context)


# ==================== PHOTO SHARING VIEWS ====================

@login_required
def photo_gallery(request):
    """View all member photos"""
    # Get albums
    albums = PhotoAlbum.objects.filter(is_public=True).prefetch_related('photos')
    
    # Get all photos or filter by album
    album_id = request.GET.get('album')
    if album_id:
        photos = Photo.objects.filter(album_id=album_id)
    else:
        photos = Photo.objects.all()
    
    photos = photos.select_related('uploaded_by', 'album', 'event').prefetch_related(
        'photo_likes', 'photo_comments'
    ).order_by('-created_at')
    
    context = {
        'photos': photos,
        'albums': albums,
        'selected_album': album_id,
    }
    return render(request, 'pages/portal/photo_gallery.html', context)


@login_required
def upload_photo(request):
    """Upload new photo"""
    if request.method == 'POST':
        image = request.FILES.get('image')
        caption = request.POST.get('caption', '').strip()
        tags = request.POST.get('tags', '').strip()
        album_id = request.POST.get('album')
        event_id = request.POST.get('event')
        
        if image:
            album = None
            if album_id:
                album = PhotoAlbum.objects.filter(id=album_id).first()
            
            event = None
            if event_id:
                event = Event.objects.filter(id=event_id).first()
            
            Photo.objects.create(
                uploaded_by=request.user,
                image=image,
                caption=caption,
                tags=tags,
                album=album,
                event=event
            )
            messages.success(request, "Photo uploaded successfully!")
            return redirect('photo_gallery')
        else:
            messages.error(request, "Please select an image to upload.")
    
    # Get albums and events for the form
    albums = PhotoAlbum.objects.filter(is_public=True)
    events = Event.objects.all().order_by('-start_date')[:20]
    
    context = {
        'albums': albums,
        'events': events,
    }
    return render(request, 'pages/portal/upload_photo.html', context)


@login_required
def photo_detail(request, photo_id):
    """View single photo with comments"""
    photo = get_object_or_404(Photo, id=photo_id)
    
    # Check if user liked this photo
    user_liked = PhotoLike.objects.filter(photo=photo, user=request.user).exists()
    
    # Get comments
    comments = photo.photo_comments.select_related('author').order_by('created_at')
    
    # Add comment if POST
    if request.method == 'POST' and 'comment_content' in request.POST:
        content = request.POST.get('comment_content', '').strip()
        if content:
            PhotoComment.objects.create(
                photo=photo,
                author=request.user,
                content=content
            )
            messages.success(request, "Comment added!")
            return redirect('photo_detail', photo_id=photo_id)
    
    context = {
        'photo': photo,
        'comments': comments,
        'user_liked': user_liked,
    }
    return render(request, 'pages/portal/photo_detail.html', context)


@login_required
def like_photo(request, photo_id):
    """Like/unlike a photo"""
    photo = get_object_or_404(Photo, id=photo_id)
    
    # Check if already liked
    existing_like = PhotoLike.objects.filter(photo=photo, user=request.user).first()
    
    if existing_like:
        existing_like.delete()
        liked = False
    else:
        PhotoLike.objects.create(photo=photo, user=request.user)
        liked = True
    
    like_count = photo.photo_likes.count()
    
    return JsonResponse({
        'liked': liked,
        'like_count': like_count
    })


@login_required
def delete_photo(request, photo_id):
    """Delete own photo (or officers/staff can delete any)"""
    photo = get_object_or_404(Photo, id=photo_id)
    
    # Check permissions: owner, staff, or officer
    is_officer = hasattr(request.user, 'member_profile') and request.user.member_profile.is_officer
    if photo.uploaded_by == request.user or request.user.is_staff or is_officer:
        photo.delete()
        messages.success(request, "Photo deleted successfully!")
    else:
        messages.error(request, "You don't have permission to delete this photo.")
    
    return redirect('photo_gallery')


@login_required
def edit_photo(request, photo_id):
    """Edit photo details (owner, officers, or staff)"""
    photo = get_object_or_404(Photo, id=photo_id)
    
    # Check permissions: owner, staff, or officer
    is_officer = hasattr(request.user, 'member_profile') and request.user.member_profile.is_officer
    if photo.uploaded_by != request.user and not request.user.is_staff and not is_officer:
        messages.error(request, "You don't have permission to edit this photo.")
        return redirect('photo_detail', photo_id=photo.id)
    
    if request.method == 'POST':
        form = EditPhotoForm(request.POST, instance=photo)
        if form.is_valid():
            form.save()
            messages.success(request, "Photo updated successfully!")
            return redirect('photo_detail', photo_id=photo.id)
    else:
        form = EditPhotoForm(instance=photo)
    
    context = {
        'form': form,
        'photo': photo,
    }
    return render(request, 'pages/portal/edit_photo.html', context)


@login_required
def create_album(request):
    """Create a new photo album"""
    if request.method == 'POST':
        form = CreateAlbumForm(request.POST)
        if form.is_valid():
            album = form.save(commit=False)
            album.created_by = request.user
            album.save()
            messages.success(request, f"Album '{album.title}' created successfully!")
            return redirect('photo_gallery')
    else:
        form = CreateAlbumForm()
    
    context = {
        'form': form,
    }
    return render(request, 'pages/portal/create_album.html', context)


@login_required
def create_event(request):
    """Create a new event"""
    # Staff always have permission
    if request.user.is_staff:
        is_officer = True
    else:
        # Check if user is an officer
        is_officer = ChapterLeadership.objects.filter(
            email__iexact=request.user.email,
            is_active=True
        ).exists()
        
        if not is_officer:
            messages.error(request, "Only officers can create events.")
            return redirect('portal_dashboard')
    
    if request.method == 'POST':
        form = CreateEventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save()
            messages.success(request, f"Event '{event.title}' created successfully!")
            return redirect('events')
    else:
        form = CreateEventForm()
    
    context = {
        'form': form,
    }
    return render(request, 'pages/portal/create_event.html', context)


@login_required
def edit_event(request, event_id):
    """Edit an existing event (officers and staff only)"""
    event = get_object_or_404(Event, id=event_id)
    
    # Check if user is an officer or staff
    is_officer = ChapterLeadership.objects.filter(
        email__iexact=request.user.email,
        is_active=True
    ).exists()
    
    if not is_officer and not request.user.is_staff:
        messages.error(request, "Only officers can edit events.")
        return redirect('events')
    
    if request.method == 'POST':
        form = CreateEventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, f"Event '{event.title}' updated successfully!")
            return redirect('events')
    else:
        form = CreateEventForm(instance=event)
    
    context = {
        'form': form,
        'event': event,
    }
    return render(request, 'pages/portal/edit_event.html', context)


@login_required
def delete_event(request, event_id):
    """Delete an event (officers and staff only)"""
    event = get_object_or_404(Event, id=event_id)
    
    # Check if user is an officer or staff
    is_officer = ChapterLeadership.objects.filter(
        email__iexact=request.user.email,
        is_active=True
    ).exists()
    
    if not is_officer and not request.user.is_staff:
        messages.error(request, "Only officers can delete events.")
        return redirect('events')
    
    event_title = event.title
    event.delete()
    messages.success(request, f"Event '{event_title}' deleted successfully!")
    return redirect('events')


@login_required
def edit_own_profile(request):
    """Allow members to edit their own profile"""
    try:
        member_profile = MemberProfile.objects.get(user=request.user)
    except MemberProfile.DoesNotExist:
        messages.error(request, "You don't have a member profile.")
        return redirect('portal_dashboard')
    
    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=member_profile, user=request.user)
        if form.is_valid():
            # Update user fields
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.email = form.cleaned_data['email']
            request.user.save()
            
            # Update profile fields
            form.save()
            
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('member_profile', username=request.user.username)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = EditProfileForm(instance=member_profile, user=request.user)
    
    context = {
        'form': form,
        'member_profile': member_profile,
    }
    return render(request, 'pages/portal/edit_profile.html', context)


@login_required
def create_post(request):
    """Allow members to create posts/announcements"""
    if request.method == 'POST':
        form = CreatePostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.is_active = True  # Auto-approve for now, can add moderation later
            post.save()
            
            messages.success(request, "Your post has been created successfully!")
            return redirect('portal_dashboard')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = CreatePostForm()
    
    context = {
        'form': form,
    }
    return render(request, 'pages/portal/create_post.html', context)


@login_required
def my_posts(request):
    """View user's own posts"""
    posts = Announcement.objects.filter(author=request.user).order_by('-created_at')
    
    context = {
        'posts': posts,
    }
    return render(request, 'pages/portal/my_posts.html', context)


@login_required
def edit_post(request, post_id):
    """Edit user's own post"""
    post = get_object_or_404(Announcement, id=post_id, author=request.user)
    
    if request.method == 'POST':
        form = CreatePostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "Post updated successfully!")
            return redirect('my_posts')
    else:
        form = CreatePostForm(instance=post)
    
    context = {
        'form': form,
        'post': post,
        'editing': True,
    }
    return render(request, 'pages/portal/create_post.html', context)


@login_required
def delete_post(request, post_id):
    """Delete user's own post"""
    post = get_object_or_404(Announcement, id=post_id, author=request.user)
    
    if request.method == 'POST':
        post.delete()
        messages.success(request, "Post deleted successfully!")
        return redirect('my_posts')
    
    context = {
        'post': post,
    }
    return render(request, 'pages/portal/delete_post_confirm.html', context)


# ============================================================================
# DUES AND PAYMENTS MANAGEMENT
# ============================================================================

def _is_financial_officer(user):
    """Check if user is admin, financial secretary, or treasurer"""
    if user.is_staff:
        return True
    # Check if user has officer profile
    if hasattr(user, 'member_profile'):
        # Check if they hold a financial position
        return ChapterLeadership.objects.filter(
            full_name__icontains=user.get_full_name() or user.username,
            position__in=['treasurer', 'secretary']  # secretary can be financial secretary
        ).exists() or user.memberprofile.is_officer
    return False


@login_required
@user_passes_test(lambda u: u.is_staff or (hasattr(u, 'member_profile') and u.member_profile.is_officer))
def dues_and_payments(request):
    """View all dues and payments (officers only)"""
    # Get filter parameters
    filter_type = request.GET.get('filter', 'all')
    member_search = request.GET.get('member', '').strip()
    status_filter = request.GET.get('status', '')
    
    # Base queryset
    payments = DuesPayment.objects.all().select_related('member', 'member__user', 'created_by')
    
    # Apply member search
    if member_search:
        payments = payments.filter(
            member__user__first_name__icontains=member_search
        ) | payments.filter(
            member__user__last_name__icontains=member_search
        ) | payments.filter(
            member__member_number__icontains=member_search
        )
    
    # Apply status filter
    if status_filter:
        payments = payments.filter(status=status_filter)
    
    # Apply time filter
    from django.utils import timezone
    from datetime import timedelta
    
    if filter_type == 'overdue':
        payments = payments.filter(status='pending', due_date__lt=timezone.now().date())
    elif filter_type == 'pending':
        payments = payments.filter(status='pending', due_date__gte=timezone.now().date())
    elif filter_type == 'paid':
        payments = payments.filter(status='paid')
    elif filter_type == 'this_month':
        now = timezone.now()
        start = now.replace(day=1)
        if now.month == 12:
            end = start.replace(year=now.year + 1, month=1) - timedelta(days=1)
        else:
            end = start.replace(month=now.month + 1) - timedelta(days=1)
        payments = payments.filter(due_date__range=[start.date(), end.date()])
    
    # Sort by due date
    payments = payments.order_by('-due_date')
    
    # Calculate summary statistics
    total_amount = payments.aggregate(models.Sum('amount'))['amount__sum'] or 0
    total_paid = payments.aggregate(models.Sum('amount_paid'))['amount_paid__sum'] or 0
    overdue_count = DuesPayment.objects.filter(status='pending', due_date__lt=timezone.now().date()).count()
    pending_count = DuesPayment.objects.filter(status='pending', due_date__gte=timezone.now().date()).count()
    
    context = {
        'payments': payments,
        'filter_type': filter_type,
        'member_search': member_search,
        'status_filter': status_filter,
        'status_choices': DuesPayment.PAYMENT_STATUS_CHOICES,
        'total_amount': total_amount,
        'total_paid': total_paid,
        'outstanding': total_amount - total_paid,
        'overdue_count': overdue_count,
        'pending_count': pending_count,
    }
    return render(request, 'pages/portal/dues_and_payments.html', context)


@login_required
@user_passes_test(lambda u: u.is_staff or (hasattr(u, 'member_profile') and u.member_profile.is_officer))
def add_dues_payment(request):
    """Add new dues/payment entry (officers only)"""
    if request.method == 'POST':
        form = DuesPaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.created_by = request.user
            payment.save()
            logger.info(f"Dues payment added: {payment.member.user.get_full_name()} - {payment.get_payment_type_display()} by {request.user.username}")
            messages.success(request, f"Successfully added dues payment for {payment.member.user.get_full_name()}!")
            return redirect('dues_and_payments')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = DuesPaymentForm()
    
    context = {
        'form': form,
        'action': 'Add',
    }
    return render(request, 'pages/portal/dues_payment_form.html', context)


@login_required
@user_passes_test(lambda u: u.is_staff or (hasattr(u, 'member_profile') and u.member_profile.is_officer))
def create_bill(request):
    """Create a bill for a member (simplified interface for treasurer, financial secretary, admin)"""
    if request.method == 'POST':
        form = CreateBillForm(request.POST)
        if form.is_valid():
            send_to_all = form.cleaned_data.get('send_to_all_members', False)
            custom_type = request.POST.get('custom_type', '').strip()
            
            # Determine which members to create bills for
            if send_to_all:
                # Get all active members (those with MemberProfile)
                members = MemberProfile.objects.all()
                if not members.exists():
                    messages.error(request, 'No active members found in the chapter.')
                    return redirect('create_bill')
            else:
                # Single member
                member = form.cleaned_data.get('member')
                if not member:
                    messages.error(request, 'Please select a member or check "Send to All Active Members".')
                    return redirect('create_bill')
                members = [member]
            
            # Create bills for each member
            bills_created = 0
            payment_type = form.cleaned_data['payment_type']
            for member in members:
                bill = DuesPayment.objects.create(
                    member=member,
                    payment_type=payment_type,
                    custom_type=custom_type if payment_type == 'other' else '',
                    amount=form.cleaned_data['amount'],
                    amount_paid=0,
                    description=form.cleaned_data.get('description', ''),
                    due_date=form.cleaned_data['due_date'],
                    status='pending',
                    created_by=request.user
                )
                bills_created += 1
                logger.info(f"Bill created: {member.user.get_full_name()} - ${bill.amount:.2f} - {bill.get_payment_type_display()} by {request.user.username}")
            
            if send_to_all:
                messages.success(request, f"Bills created for {bills_created} members! Due: {form.cleaned_data['due_date'].strftime('%B %d, %Y')}")
            else:
                member_name = members[0].user.get_full_name()
                messages.success(request, f"Bill created for {member_name}! Due: {form.cleaned_data['due_date'].strftime('%B %d, %Y')}")
            return redirect('dues_and_payments')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CreateBillForm()
    
    context = {
        'form': form,
    }
    return render(request, 'pages/portal/create_bill.html', context)


@login_required
@user_passes_test(lambda u: u.is_staff or (hasattr(u, 'member_profile') and u.member_profile.is_officer))
def edit_dues_payment(request, pk):
    """Edit dues/payment entry (officers only)"""
    payment = get_object_or_404(DuesPayment, pk=pk)
    
    if request.method == 'POST':
        form = DuesPaymentForm(request.POST, instance=payment)
        if form.is_valid():
            payment = form.save()
            logger.info(f"Dues payment updated: {payment.member.user.get_full_name()} - {payment.get_payment_type_display()} by {request.user.username}")
            messages.success(request, f"Successfully updated dues payment for {payment.member.user.get_full_name()}!")
            return redirect('dues_and_payments')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = DuesPaymentForm(instance=payment)
    
    context = {
        'form': form,
        'payment': payment,
        'action': 'Edit',
    }
    return render(request, 'pages/portal/dues_payment_form.html', context)


@login_required
@user_passes_test(lambda u: u.is_staff or (hasattr(u, 'member_profile') and u.member_profile.is_officer))
def delete_dues_payment(request, pk):
    """Delete dues/payment entry (officers only)"""
    payment = get_object_or_404(DuesPayment, pk=pk)
    member_name = payment.member.user.get_full_name()
    payment_type = payment.get_payment_type_display()
    amount = payment.amount
    
    if request.method == 'POST':
        payment.delete()
        logger.info(f"Dues payment deleted: {member_name} - {payment_type} - ${amount} by {request.user.username}")
        messages.success(request, f"Successfully deleted dues payment for {member_name}.")
        return redirect('dues_and_payments')
    
    context = {
        'payment': payment,
    }
    return render(request, 'pages/portal/dues_payment_confirm_delete.html', context)


@login_required
@user_passes_test(lambda u: u.is_staff or (hasattr(u, 'member_profile') and u.member_profile.is_officer))
def member_dues_summary(request):
    """View dues summary for all members (officers only)"""
    # Get all members with their payment summaries
    members = MemberProfile.objects.all().select_related('user').prefetch_related('payments')
    
    member_data = []
    for member in members:
        payments = member.payments.all()
        total_owed = payments.aggregate(models.Sum('amount'))['amount__sum'] or 0
        total_paid = payments.aggregate(models.Sum('amount_paid'))['amount_paid__sum'] or 0
        balance = total_owed - total_paid
        
        overdue_payments = payments.filter(status='pending', due_date__lt=timezone.now().date()).count()
        
        member_data.append({
            'member': member,
            'total_owed': total_owed,
            'total_paid': total_paid,
            'balance': balance,
            'overdue_count': overdue_payments,
            'payment_count': payments.count(),
        })
    
    # Sort by balance (highest owed first)
    member_data.sort(key=lambda x: x['balance'], reverse=True)
    
    # Calculate totals
    total_owed = sum(m['total_owed'] for m in member_data)
    total_paid = sum(m['total_paid'] for m in member_data)
    
    context = {
        'member_data': member_data,
        'total_owed': total_owed,
        'total_paid': total_paid,
        'outstanding': total_owed - total_paid,
    }
    return render(request, 'pages/portal/member_dues_summary.html', context)


# ============================================================================
# STRIPE PAYMENT INTEGRATION
# ============================================================================

@login_required
@user_passes_test(lambda u: u.is_staff or (hasattr(u, 'member_profile') and u.member_profile.is_officer))
def setup_stripe_config(request):
    """Configure Stripe payment settings (Treasurer/Admin only)"""
    try:
        config = StripeConfiguration.objects.get(treasurer=request.user)
    except StripeConfiguration.DoesNotExist:
        config = None
    
    if request.method == 'POST':
        form = StripeConfigurationForm(request.POST, instance=config)
        if form.is_valid():
            stripe_config = form.save(commit=False)
            stripe_config.treasurer = request.user
            stripe_config.save()
            
            # Set Stripe API key for this session
            stripe.api_key = stripe_config.stripe_secret_key
            
            logger.info(f"Stripe configuration updated by {request.user.username}")
            messages.success(request, "Stripe configuration saved successfully!")
            return redirect('stripe_config')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = StripeConfigurationForm(instance=config)
    
    context = {
        'form': form,
        'config': config,
    }
    return render(request, 'pages/portal/stripe_config.html', context)


@login_required
def pay_dues_online(request, payment_id):
    """Display payment form and handle Stripe checkout"""
    payment = get_object_or_404(DuesPayment, id=payment_id, member__user=request.user)
    
    # Check if Stripe is configured
    try:
        stripe_config = StripeConfiguration.objects.get(is_active=True)
    except StripeConfiguration.DoesNotExist:
        messages.error(request, "Online payments are not currently available.")
        return redirect('dues_view')
    
    # Set Stripe API key
    stripe.api_key = stripe_config.stripe_secret_key
    
    if request.method == 'POST':
        try:
            # Create a PaymentIntent
            amount_cents = int(payment.balance * 100)  # Stripe uses cents
            
            payment_intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency='usd',
                payment_method_types=['card'],
                metadata={
                    'payment_id': payment.id,
                    'member_id': payment.member.id,
                    'member_number': payment.member.member_number,
                }
            )
            
            # Create StripePayment record
            stripe_payment = StripePayment.objects.create(
                dues_payment=payment,
                member=payment.member,
                stripe_payment_intent_id=payment_intent.id,
                amount=amount_cents,
                payment_type=payment.payment_type,
                description=f"{payment.get_payment_type_display()} - {payment.member.user.get_full_name()}",
            )
            
            logger.info(f"PaymentIntent created: {payment_intent.id} for member {payment.member.member_number}")
            
            context = {
                'stripe_public_key': stripe_config.stripe_publishable_key,
                'client_secret': payment_intent.client_secret,
                'payment': payment,
                'stripe_payment': stripe_payment,
                'amount': payment.balance,
            }
            return render(request, 'pages/portal/stripe_checkout.html', context)
        
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error: {str(e)}")
            messages.error(request, f"Payment error: {str(e)}")
            return redirect('dues_view')
    
    context = {
        'payment': payment,
        'stripe_public_key': stripe_config.stripe_publishable_key,
    }
    return render(request, 'pages/portal/payment_detail.html', context)


@login_required
def stripe_webhook(request):
    """Handle Stripe webhook events"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)
    
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        stripe_config = StripeConfiguration.objects.get(is_active=True)
        stripe.api_key = stripe_config.stripe_secret_key
        
        # Verify signature - in production, use webhook endpoint secret
        event = json.loads(payload)
        
    except ValueError:
        logger.error("Invalid webhook payload")
        return JsonResponse({'error': 'Invalid payload'}, status=400)
    except StripeConfiguration.DoesNotExist:
        logger.error("Stripe not configured")
        return JsonResponse({'error': 'Stripe not configured'}, status=500)
    
    # Handle payment intent succeeded
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        payment_intent_id = payment_intent['id']
        
        try:
            stripe_payment = StripePayment.objects.get(stripe_payment_intent_id=payment_intent_id)
            stripe_payment.status = 'succeeded'
            stripe_payment.stripe_charge_id = payment_intent.get('charges', {}).get('data', [{}])[0].get('id', '')
            stripe_payment.completed_at = timezone.now()
            stripe_payment.save()
            
            # Update DuesPayment
            if stripe_payment.dues_payment:
                dues = stripe_payment.dues_payment
                dues.amount_paid += Decimal(str(stripe_payment.amount_dollars))
                dues.status = 'paid' if dues.amount_paid >= dues.amount else 'partial'
                dues.payment_date = timezone.now().date()
                dues.payment_method = 'Stripe'
                dues.save()
                
                # Update member status
                member = dues.member
                if member.payments.filter(status='pending').exists():
                    member.dues_current = False
                else:
                    member.dues_current = True
                member.save()
            
            logger.info(f"Payment succeeded: {payment_intent_id}")
        
        except StripePayment.DoesNotExist:
            logger.error(f"StripePayment not found: {payment_intent_id}")
    
    # Handle payment intent payment_failed
    elif event['type'] == 'payment_intent.payment_failed':
        payment_intent = event['data']['object']
        payment_intent_id = payment_intent['id']
        
        try:
            stripe_payment = StripePayment.objects.get(stripe_payment_intent_id=payment_intent_id)
            stripe_payment.status = 'failed'
            stripe_payment.error_message = payment_intent.get('last_payment_error', {}).get('message', 'Unknown error')
            stripe_payment.save()
            
            logger.warning(f"Payment failed: {payment_intent_id} - {stripe_payment.error_message}")
        
        except StripePayment.DoesNotExist:
            logger.error(f"StripePayment not found: {payment_intent_id}")
    
    return JsonResponse({'status': 'success'}, status=200)


@login_required
def payment_success(request, stripe_payment_id):
    """Display payment success page"""
    stripe_payment = get_object_or_404(StripePayment, id=stripe_payment_id)
    
    # Verify the payment belongs to the logged-in user
    if stripe_payment.member.user != request.user and not request.user.is_staff:
        messages.error(request, "You don't have permission to view this payment.")
        return redirect('dues_view')
    
    context = {
        'stripe_payment': stripe_payment,
        'dues_payment': stripe_payment.dues_payment,
    }
    return render(request, 'pages/portal/payment_success.html', context)


@login_required
def payment_cancelled(request, stripe_payment_id):
    """Display payment cancelled page"""
    stripe_payment = get_object_or_404(StripePayment, id=stripe_payment_id)
    
    # Verify the payment belongs to the logged-in user
    if stripe_payment.member.user != request.user and not request.user.is_staff:
        messages.error(request, "You don't have permission to view this payment.")
        return redirect('dues_view')
    
    stripe_payment.status = 'cancelled'
    stripe_payment.save()
    
    context = {
        'stripe_payment': stripe_payment,
    }
    return render(request, 'pages/portal/payment_cancelled.html', context)


# ==================== SMS/Twilio Views ====================

def _is_admin(user):
    """Check if user is admin"""
    return user.is_staff or user.is_superuser


def _send_sms(phone_number, message_body, sms_type, triggered_by='admin_manual', member=None, related_object_id=None, related_object_type=''):
    """
    Send SMS via Twilio or log for test mode
    Returns True if successful, False otherwise
    """
    try:
        config = TwilioConfiguration.objects.get(is_active=True)
    except TwilioConfiguration.DoesNotExist:
        logging.warning(f"Twilio not configured - SMS not sent to {phone_number}")
        return False
    
    # Create SMS log record
    sms_log = SMSLog.objects.create(
        member=member,
        phone_number=phone_number,
        message_body=message_body,
        sms_type=sms_type,
        triggered_by=triggered_by,
        related_object_id=related_object_id,
        related_object_type=related_object_type,
        status='test' if config.is_test_mode else 'pending'
    )
    
    # In test mode, just log it
    if config.is_test_mode:
        logging.info(f"SMS Test Mode: {phone_number} - {message_body[:50]}...")
        return True
    
    # Send via Twilio
    try:
        client = Client(config.account_sid, config.auth_token)
        message = client.messages.create(
            body=message_body,
            from_=config.twilio_phone_number,
            to=phone_number
        )
        
        # Update log with successful send
        sms_log.status = 'sent'
        sms_log.twilio_sid = message.sid
        sms_log.sent_at = timezone.now()
        sms_log.save()
        
        return True
    except Exception as e:
        logging.error(f"Twilio SMS Error: {str(e)}")
        sms_log.status = 'failed'
        sms_log.error_message = str(e)
        sms_log.save()
        return False


@login_required
@user_passes_test(_is_admin)
def setup_twilio_config(request):
    """Admin view to configure Twilio settings"""
    # Get or create config for current user
    config, created = TwilioConfiguration.objects.get_or_create(admin=request.user)
    
    if request.method == 'POST':
        form = TwilioConfigurationForm(request.POST, instance=config)
        if form.is_valid():
            form.save()
            messages.success(request, 'Twilio configuration saved successfully!')
            return redirect('twilio_config')
    else:
        form = TwilioConfigurationForm(instance=config)
    
    context = {
        'form': form,
        'config': config,
    }
    return render(request, 'pages/portal/twilio_config.html', context)


@login_required
def update_sms_preferences(request):
    """Member view to update SMS preferences"""
    member = request.user.member_profile
    
    # Create SMSPreference if it doesn't exist
    sms_pref, created = SMSPreference.objects.get_or_create(member=member)
    
    if request.method == 'POST':
        form = SMSPreferenceForm(request.POST, instance=sms_pref)
        if form.is_valid():
            # Update opted_in based on any preference being checked
            preferences = form.cleaned_data
            opted_in = (
                preferences.get('receive_announcements') or
                preferences.get('receive_messages') or
                preferences.get('receive_dues_reminders') or
                preferences.get('receive_event_alerts')
            )
            
            instance = form.save(commit=False)
            instance.opted_in = opted_in
            
            if opted_in:
                instance.last_opted_in = timezone.now()
            else:
                instance.last_opted_out = timezone.now()
            
            instance.save()
            messages.success(request, 'SMS preferences updated successfully!')
            return redirect('member_profile')
    else:
        form = SMSPreferenceForm(instance=sms_pref)
    
    context = {
        'form': form,
        'sms_preference': sms_pref,
    }
    return render(request, 'pages/portal/sms_preferences.html', context)


@login_required
@user_passes_test(_is_admin)
def send_sms_alert(request):
    """Admin view to manually send SMS alerts to members"""
    if request.method == 'POST':
        alert_type = request.POST.get('alert_type', 'announcement')
        message_content = request.POST.get('message_content', '')
        recipient_type = request.POST.get('recipient_type', 'opted_in')  # opted_in or specific_type
        
        if not message_content:
            messages.error(request, 'Please enter a message.')
            return redirect('send_sms_alert')
        
        # Get eligible recipients based on preferences
        if recipient_type == 'opted_in':
            preferences = SMSPreference.objects.filter(opted_in=True)
        elif recipient_type == 'announcements':
            preferences = SMSPreference.objects.filter(receive_announcements=True, opted_in=True)
        elif recipient_type == 'dues_reminders':
            preferences = SMSPreference.objects.filter(receive_dues_reminders=True, opted_in=True)
        elif recipient_type == 'event_alerts':
            preferences = SMSPreference.objects.filter(receive_event_alerts=True, opted_in=True)
        else:
            preferences = SMSPreference.objects.filter(opted_in=True)
        
        sent_count = 0
        failed_count = 0
        
        for pref in preferences:
            if pref.phone_number:
                success = _send_sms(
                    phone_number=pref.phone_number,
                    message_body=message_content,
                    sms_type=alert_type,
                    triggered_by='admin_manual',
                    member=pref.member,
                )
                if success:
                    sent_count += 1
                else:
                    failed_count += 1
        
        messages.success(request, f'SMS alerts sent to {sent_count} members. ({failed_count} failed)')
        return redirect('send_sms_alert')
    
    context = {
        'alert_types': SMSLog.SMS_TYPE_CHOICES,
        'recipient_types': [
            ('opted_in', 'All Opted-In Members'),
            ('announcements', 'Members who want Announcements'),
            ('dues_reminders', 'Members who want Dues Reminders'),
            ('event_alerts', 'Members who want Event Alerts'),
        ]
    }
    return render(request, 'pages/portal/send_sms_alert.html', context)


@login_required
def view_sms_logs(request):
    """Member/Admin view SMS logs"""
    if request.user.is_staff:
        # Admin sees all SMS logs
        sms_logs = SMSLog.objects.all().order_by('-created_at')[:100]
    else:
        # Members see their own SMS logs
        member = request.user.member_profile
        sms_logs = SMSLog.objects.filter(member=member).order_by('-created_at')[:50]
    
    context = {
        'sms_logs': sms_logs,
    }
    return render(request, 'pages/portal/sms_logs.html', context)


# ==================== BOUTIQUE VIEWS ====================

def shop_home(request):
    """Display all products with optional filtering"""
    products = Product.objects.all()
    category = request.GET.get('category')
    
    if category:
        products = products.filter(category=category)
    
    categories = Product.objects.values_list('category', flat=True).distinct()
    
    context = {
        'products': products,
        'categories': categories,
        'selected_category': category,
    }
    return render(request, 'pages/boutique/shop.html', context)


def product_detail(request, pk):
    """Display product details"""
    product = get_object_or_404(Product, pk=pk)
    
    context = {
        'product': product,
        'sizes': product.get_sizes_list(),
        'colors': product.get_colors_list(),
    }
    return render(request, 'pages/boutique/product_detail.html', context)


@login_required
def add_to_cart(request, pk):
    """Add product to cart"""
    product = get_object_or_404(Product, pk=pk)
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        size = request.POST.get('size', '')
        color = request.POST.get('color', '')
        
        if quantity > 0 and quantity <= product.inventory:
            cart_item, item_created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                size=size,
                color=color,
                defaults={'quantity': quantity}
            )
            
            if not item_created:
                cart_item.quantity += quantity
                cart_item.save()
            
            messages.success(request, f'{product.name} added to cart!')
            return redirect('view_cart')
        else:
            messages.error(request, 'Invalid quantity or insufficient inventory')
    
    return redirect('product_detail', pk=pk)


@login_required
def view_cart(request):
    """Display shopping cart"""
    try:
        cart = Cart.objects.get(user=request.user)
    except Cart.DoesNotExist:
        cart = None
    
    context = {
        'cart': cart,
    }
    return render(request, 'pages/boutique/cart.html', context)


@login_required
def update_cart_item(request, item_id):
    """Update cart item quantity"""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity > 0:
            if quantity <= cart_item.product.inventory:
                cart_item.quantity = quantity
                cart_item.save()
                messages.success(request, 'Cart updated!')
            else:
                messages.error(request, 'Insufficient inventory')
        else:
            cart_item.delete()
            messages.success(request, 'Item removed from cart')
    
    return redirect('view_cart')


@login_required
def remove_from_cart(request, item_id):
    """Remove item from cart"""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    messages.success(request, 'Item removed from cart')
    return redirect('view_cart')


@login_required
def checkout(request):
    """Checkout and create order"""
    try:
        cart = Cart.objects.get(user=request.user)
    except Cart.DoesNotExist:
        messages.error(request, 'Your cart is empty')
        return redirect('shop_home')
    
    if not cart.cartitem_set.exists():
        messages.error(request, 'Your cart is empty')
        return redirect('shop_home')
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Create order
            order = Order.objects.create(
                user=request.user,
                total_price=cart.get_total_price(),
                email=form.cleaned_data['email'],
                address=form.cleaned_data['address'],
                city=form.cleaned_data['city'],
                state=form.cleaned_data['state'],
                zip_code=form.cleaned_data['zip_code'],
            )
            
            # Create order items from cart
            for cart_item in cart.cartitem_set.all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    size=cart_item.size,
                    color=cart_item.color,
                    price=cart_item.product.price,
                )
            
            # Clear cart
            cart.cartitem_set.all().delete()
            
            return redirect('payment', order_id=order.id)
    else:
        form = CheckoutForm(initial={
            'email': request.user.email,
        })
    
    context = {
        'form': form,
        'cart': cart,
    }
    return render(request, 'pages/boutique/checkout.html', context)


@login_required
def payment(request, order_id):
    """Handle Stripe payment"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    stripe.api_key = settings.STRIPE_SECRET_KEY
    
    if order.status != 'pending':
        messages.error(request, 'This order cannot be paid')
        return redirect('shop_home')
    
    if request.method == 'POST':
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(order.total_price * 100),  # Convert to cents
                currency='usd',
                metadata={
                    'order_id': order.id,
                    'user_id': request.user.id,
                }
            )
            
            order.stripe_payment_intent = intent['id']
            order.save()
            
            context = {
                'order': order,
                'client_secret': intent['client_secret'],
                'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
            }
            return render(request, 'pages/boutique/payment.html', context)
        except stripe.error.StripeError as e:
            messages.error(request, f'Payment error: {str(e)}')
            return redirect('checkout', order_id=order.id)
    
    context = {
        'order': order,
    }
    return render(request, 'pages/boutique/payment.html', context)


@login_required
def payment_success(request, order_id):
    """Handle successful payment"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order.status = 'completed'
    order.save()
    
    context = {
        'order': order,
    }
    return render(request, 'pages/boutique/payment_success.html', context)


@login_required
def order_history(request):
    """Display user's order history"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'orders': orders,
    }
    return render(request, 'pages/boutique/order_history.html', context)


@login_required
@user_passes_test(lambda u: u.is_staff or (hasattr(u, 'member_profile') and u.member_profile.is_officer))
def import_products(request):
    """Admin/Officer view to import products from CSV with optional images"""
    if request.method == 'POST':
        form = BoutiqueImportForm(request.POST, request.FILES)
        if form.is_valid():
            products_data = form.parse_csv()
            images_zip = form.cleaned_data.get('images_zip')
            
            # Extract images from ZIP if provided
            images_dict = {}
            if images_zip:
                import zipfile
                try:
                    with zipfile.ZipFile(images_zip) as zip_ref:
                        for file_info in zip_ref.filelist:
                            if not file_info.is_dir():
                                images_dict[file_info.filename] = zip_ref.read(file_info.filename)
                except Exception as e:
                    messages.error(request, f'Error extracting images: {str(e)}')
                    return render(request, 'pages/boutique/import_products.html', {'form': form})
            
            created_count = 0
            error_count = 0
            
            for product_data in products_data:
                try:
                    product, created = Product.objects.get_or_create(
                        name=product_data['name'],
                        defaults={
                            'description': product_data.get('description', ''),
                            'category': product_data['category'],
                            'price': Decimal(str(product_data['price'])),
                            'inventory': int(product_data.get('inventory', 100)),
                            'sizes': product_data.get('sizes', ''),
                            'colors': product_data.get('colors', ''),
                        }
                    )
                    
                    # Handle image from image_path (ZIP file)
                    if product_data.get('image_path') and images_dict:
                        image_path = product_data['image_path']
                        if image_path in images_dict:
                            from django.core.files.base import ContentFile
                            # Get file extension
                            _, ext = os.path.splitext(image_path)
                            filename = f"{product.name.replace(' ', '_')}{ext}"
                            product.image.save(filename, ContentFile(images_dict[image_path]), save=True)
                    
                    # Handle image from image_url (download from internet)
                    elif product_data.get('image_url'):
                        image_url = product_data['image_url']
                        try:
                            import requests
                            response = requests.get(image_url, timeout=10)
                            if response.status_code == 200:
                                from django.core.files.base import ContentFile
                                # Get file extension from URL
                                from urllib.parse import urlparse
                                parsed_url = urlparse(image_url)
                                _, ext = os.path.splitext(parsed_url.path)
                                if not ext:
                                    ext = '.jpg'  # Default to jpg
                                filename = f"{product.name.replace(' ', '_')}{ext}"
                                product.image.save(filename, ContentFile(response.content), save=True)
                        except Exception as e:
                            # Image download failed, but product was created
                            pass
                    
                    if created:
                        created_count += 1
                
                except Exception as e:
                    error_count += 1
                    continue
            
            if error_count > 0:
                messages.warning(request, f'Imported {created_count} new products with {error_count} errors.')
            else:
                messages.success(request, f'Successfully imported {created_count} new products!')
            return redirect('import_products')
    else:
        form = BoutiqueImportForm()
    
    context = {
        'form': form,
    }
    return render(request, 'pages/boutique/import_products.html', context)


@login_required
@user_passes_test(lambda u: u.is_staff or (hasattr(u, 'member_profile') and u.member_profile.is_officer))
def add_product(request):
    """Admin/Officer view to add a new product"""
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'Product "{product.name}" created successfully!')
            return redirect('product_detail', pk=product.id)
    else:
        form = ProductForm()
    
    context = {
        'form': form,
        'title': 'Add New Product'
    }
    return render(request, 'pages/boutique/product_form.html', context)


@login_required
@user_passes_test(lambda u: u.is_staff or (hasattr(u, 'member_profile') and u.member_profile.is_officer))
def edit_product(request, pk):
    """Admin/Officer view to edit a product"""
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'Product "{product.name}" updated successfully!')
            return redirect('product_detail', pk=product.id)
    else:
        form = ProductForm(instance=product)
    
    context = {
        'form': form,
        'product': product,
        'title': f'Edit {product.name}'
    }
    return render(request, 'pages/boutique/product_form.html', context)


@login_required
@user_passes_test(lambda u: u.is_staff or (hasattr(u, 'member_profile') and u.member_profile.is_officer))
def delete_product(request, pk):
    """Admin/Officer view to delete a product"""
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        product_name = product.name
        product.delete()
        messages.success(request, f'Product "{product_name}" deleted successfully!')
        return redirect('shop_home')
    
    context = {
        'product': product,
    }
    return render(request, 'pages/boutique/delete_product_confirm.html', context)
