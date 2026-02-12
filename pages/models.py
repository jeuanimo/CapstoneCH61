"""
=============================================================================
DJANGO MODELS FOR PHI BETA SIGMA FRATERNITY CHAPTER WEBSITE
=============================================================================

This module contains all database models for the Phi Beta Sigma chapter website,
including:
- Event Management (Category, Event, EventAttendance)
- Chapter Leadership (ChapterLeadership)
- Member Portal (MemberProfile, DuesPayment, Announcements, Documents, Messages)
- Social Features (PhotoAlbum, Photo, ProfileComments, etc.)
- Payment Integration (StripeConfiguration, StripePayment)
- SMS Alerts (TwilioConfiguration, SMSPreference, SMSLog)
- E-commerce Boutique (Product, Cart, Order)

Each model includes helpful documentation and validation methods.
=============================================================================
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError


class Category(models.Model):
    """
    Event categories for organizing events
    
    Fields:
        name (CharField): Unique category name
        description (TextField): Optional description of the category
        color (CharField): Hex color code for UI display (#164f90 default)
        created_at (DateTimeField): Auto-set timestamp when created
    
    Usage:
        category = Category.objects.create(name='Social Action', color='#164f90')
        events = category.events.all()  # Get all events in this category
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, default='')
    color = models.CharField(max_length=7, default='#164f90', help_text="Hex color code for category")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
    
    def __str__(self):
        return self.name


class Event(models.Model):
    EVENT_TYPE_CHOICES = [
        ('social_action', 'Social Action'),
        ('education', 'Education'),
        ('business', 'Business'),
        ('sigma_beta_club', 'Sigma Beta Club'),
        ('sigma_wellness', 'Sigma Wellness'),
        ('other', 'Other'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='events')
    event_type = models.CharField(max_length=50, choices=EVENT_TYPE_CHOICES, default='other', help_text="Select the type of event")
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    location = models.CharField(max_length=200, blank=True, default='')
    image = models.ImageField(upload_to='events/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['start_date']

    def __str__(self):
        return self.title

class ChapterLeadership(models.Model):
    """Model for chapter leadership/officers"""
    
    POSITION_CHOICES = [
        ('president', 'President'),
        ('vice_president_1st', '1st Vice President'),
        ('vice_president_2nd', '2nd Vice President'),
        ('secretary', 'Secretary'),
        ('treasurer', 'Treasurer'),
        ('parliamentarian', 'Parliamentarian'),
        ('chaplain', 'Chaplain'),
        ('historian', 'Historian'),
        ('sergeant_at_arms', 'Sergeant at Arms'),
        ('board_member', 'Board Member'),
        ('other', 'Other Position'),
    ]
    
    position = models.CharField(max_length=50, choices=POSITION_CHOICES)
    position_custom = models.CharField(max_length=100, blank=True, default='', help_text="Custom position title (if 'Other' is selected)")
    full_name = models.CharField(max_length=200)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, default='')
    bio = models.TextField(blank=True, default='', help_text="Brief biography or background")
    profile_image = models.ImageField(upload_to='leadership/', blank=True, null=True, help_text="Upload profile photo")
    display_order = models.IntegerField(default=0, help_text="Order in which to display (lower numbers first)")
    is_active = models.BooleanField(default=True, help_text="Currently serving in this position")
    term_start = models.DateField(blank=True, null=True)
    term_end = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['display_order', 'position']
        verbose_name = 'Chapter Leader'
        verbose_name_plural = 'Chapter Leadership'
    
    def __str__(self):
        position_name = self.position_custom if self.position == 'other' else self.get_position_display()
        return f"{self.full_name} - {position_name}"
    
    def get_position_title(self):
        """Return the display position title"""
        if self.position == 'other' and self.position_custom:
            return self.position_custom
        return self.get_position_display()


# ============================================================================
# MEMBER PORTAL MODELS
# ============================================================================

class MemberProfileManager(models.Manager):
    """Custom manager for MemberProfile with convenient filtering methods"""
    
    def financial_members(self):
        """Get all financial members (excludes suspended, non-financial, and non-financial life members)"""
        return self.exclude(
            status__in=['suspended', 'non_financial', 'non_financial_life_member']
        )
    
    def paying_members(self):
        """Get only current paying members (financial and financial life members)"""
        return self.filter(status__in=['financial', 'financial_life_member'])
    
    def all_active(self):
        """Get all active members including new members (excludes only suspended)"""
        return self.exclude(status='suspended')


class MemberProfile(models.Model):
    """Extended profile for fraternity members"""
    
    STATUS_CHOICES = [
        ('financial', 'Financial'),
        ('non_financial', 'Non Financial'),
        ('financial_life_member', 'Financial Life Member'),
        ('non_financial_life_member', 'Non Financial Life Member'),
        ('new_member', 'New Member'),
        ('suspended', 'Suspended'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='member_profile')
    member_number = models.CharField(max_length=50, unique=True, help_text="Unique member ID")
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='financial')
    initiation_date = models.DateField(blank=True, null=True)
    line_name = models.CharField(max_length=100, blank=True, default='')
    line_number = models.CharField(max_length=10, blank=True, default='')
    phone = models.CharField(max_length=20, blank=True, default='')
    emergency_contact_name = models.CharField(max_length=200, blank=True, default='')
    emergency_contact_phone = models.CharField(max_length=20, blank=True, default='')
    address = models.TextField(blank=True, default='')
    profile_image = models.ImageField(upload_to='members/', blank=True, null=True)
    bio = models.TextField(blank=True, default='')
    dues_current = models.BooleanField(default=False, help_text="Are dues paid up to date?")
    is_officer = models.BooleanField(default=False, help_text="Is this member an officer with admin privileges?")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # 90-day removal tracking (for members not in HQ list)
    marked_for_removal_date = models.DateTimeField(
        blank=True, 
        null=True, 
        help_text="Date member was marked for dues payment - gives 90 day window to pay national/local dues"
    )
    removal_reason = models.CharField(
        max_length=200, 
        blank=True, 
        default='',
        help_text="Reason for marking (e.g., 'Not on current HQ list - requires dues verification')"
    )
    
    # Custom manager
    objects = MemberProfileManager()
    
    class Meta:
        ordering = ['user__last_name', 'user__first_name']
        verbose_name = 'Member Profile'
        verbose_name_plural = 'Member Profiles'
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.member_number})"
    
    def get_full_name(self):
        return self.user.get_full_name() or self.user.username
    
    def is_marked_for_removal(self):
        """Check if member is marked for removal"""
        return self.marked_for_removal_date is not None
    
    def days_until_removal(self):
        """Calculate days remaining before removal (90 day window)"""
        if not self.marked_for_removal_date:
            return None
        from datetime import timedelta
        from django.utils import timezone
        removal_deadline = self.marked_for_removal_date + timedelta(days=90)
        days_left = (removal_deadline - timezone.now()).days
        return max(0, days_left)  # Return 0 if deadline has passed
    
    def should_be_removed(self):
        """Check if 90 days have passed since marking for removal"""
        if not self.marked_for_removal_date:
            return False
        from datetime import timedelta
        from django.utils import timezone
        removal_deadline = self.marked_for_removal_date + timedelta(days=90)
        return timezone.now() >= removal_deadline
    
    def save(self, *args, **kwargs):
        # Automatically update status based on dues_current (unless Life Member, New Member, or Suspended)
        if self.status not in ['financial_life_member', 'non_financial_life_member', 'new_member', 'suspended']:
            if self.dues_current:
                self.status = 'financial'
            else:
                self.status = 'non_financial'
        super().save(*args, **kwargs)


class DuesPayment(models.Model):
    """Track dues and payment history"""
    
    PAYMENT_TYPE_CHOICES = [
        ('monthly_dues', 'Monthly Dues'),
        ('semester_dues', 'Semester Dues'),
        ('annual_dues', 'Annual Dues'),
        ('fine', 'Fine'),
        ('house_charge', 'House Charge'),
        ('event_fee', 'Event Fee'),
        ('other', 'Other'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('partial', 'Partial'),
        ('overdue', 'Overdue'),
        ('waived', 'Waived'),
    ]
    
    member = models.ForeignKey(MemberProfile, on_delete=models.CASCADE, related_name='payments')
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES)
    custom_type = models.CharField(max_length=100, blank=True, default='', help_text="Custom bill type description when payment_type is 'other'")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    description = models.TextField(blank=True, default='')
    due_date = models.DateField()
    payment_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=50, blank=True, default='')
    transaction_id = models.CharField(max_length=100, blank=True, default='')
    notes = models.TextField(blank=True, default='')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_payments')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-due_date']
        verbose_name = 'Dues Payment'
        verbose_name_plural = 'Dues Payments'
    
    def __str__(self):
        return f"{self.member.user.get_full_name()} - {self.get_payment_type_display()} - ${self.amount}"
    
    @property
    def balance(self):
        return self.amount - self.amount_paid
    
    @property
    def is_overdue(self):
        return self.status == 'pending' and self.due_date < timezone.now().date()


class EventAttendance(models.Model):
    """Track member attendance at events"""
    
    ATTENDANCE_STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('excused', 'Excused'),
        ('late', 'Late'),
    ]
    
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='attendance_records')
    member = models.ForeignKey(MemberProfile, on_delete=models.CASCADE, related_name='attendance')
    status = models.CharField(max_length=20, choices=ATTENDANCE_STATUS_CHOICES, default='absent')
    points = models.IntegerField(default=0, help_text="Points earned for attendance")
    notes = models.TextField(blank=True, default='')
    rsvp_status = models.BooleanField(default=False, help_text="Did member RSVP?")
    checked_in_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-event__start_date']
        unique_together = ['event', 'member']
        verbose_name = 'Event Attendance'
        verbose_name_plural = 'Event Attendance'
    
    def __str__(self):
        return f"{self.member.user.get_full_name()} - {self.event.title} - {self.get_status_display()}"


class Announcement(models.Model):
    """Portal announcements and communications"""
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='normal')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='announcements')
    is_pinned = models.BooleanField(default=False, help_text="Pin to top of announcements")
    is_active = models.BooleanField(default=True)
    publish_date = models.DateTimeField(default=timezone.now)
    expiry_date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_pinned', '-publish_date']
        verbose_name = 'Announcement'
        verbose_name_plural = 'Announcements'
    
    def __str__(self):
        return self.title
    
    @property
    def is_expired(self):
        if self.expiry_date:
            return timezone.now() > self.expiry_date
        return False


class AnnouncementView(models.Model):
    """Track which announcements users have viewed"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='announcement_views')
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE, related_name='views')
    viewed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'announcement']
        verbose_name = 'Announcement View'
        verbose_name_plural = 'Announcement Views'
    
    def __str__(self):
        return f"{self.user.username} viewed {self.announcement.title}"


class Document(models.Model):
    """Document storage for meeting minutes, manuals, etc."""
    
    CATEGORY_CHOICES = [
        ('meeting_minutes', 'Meeting Minutes'),
        ('calendar', 'Calendar'),
        ('manual', 'Officer Manual'),
        ('bylaws', 'Bylaws & Constitution'),
        ('financial', 'Financial Documents'),
        ('forms', 'Forms & Templates'),
        ('officer_only', 'Officer Only'),
        ('other', 'Other'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    file = models.FileField(upload_to='documents/')
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='uploaded_documents')
    is_public = models.BooleanField(default=False, help_text="Visible to all members")
    requires_officer = models.BooleanField(default=False, help_text="Only officers can view")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Document'
        verbose_name_plural = 'Documents'
    
    def __str__(self):
        return self.title


class Message(models.Model):
    """Direct messaging between members"""
    
    class Status(models.TextChoices):
        DRAFT = "DR", "Draft"
        SENT = "SE", "Sent"
        READ = "RD", "Read"
        ARCHIVED = "AR", "Archived"
        DELETED = "DE", "Deleted"
    
    class Priority(models.TextChoices):
        LOW = "LO", "Low"
        NORMAL = "NR", "Normal"
        HIGH = "HI", "High"
        URGENT = "UR", "Urgent"
    
    class Category(models.TextChoices):
        GENERAL = "GN", "General"
        OFFICIAL = "OF", "Official Chapter Business"
        EVENT = "EV", "Event Related"
        FINANCIAL = "FI", "Financial"
        COMMITTEE = "CM", "Committee"
    
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    subject = models.CharField(max_length=200, blank=True, default='')
    content = models.TextField()
    
    # Status tracking with TextChoices
    status = models.CharField(
        max_length=2,
        choices=Status.choices,
        default=Status.SENT,
    )
    priority = models.CharField(
        max_length=2,
        choices=Priority.choices,
        default=Priority.NORMAL,
    )
    category = models.CharField(
        max_length=2,
        choices=Category.choices,
        default=Category.GENERAL,
    )
    
    # Keep is_read for backward compatibility and easy querying
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(blank=True, null=True)
    parent_message = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
    
    def __str__(self):
        return f"{self.sender.username} to {self.recipient.username}: {self.subject or 'No Subject'}"
    
    def mark_as_read(self):
        """Mark message as read and update status"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.status = self.Status.READ
            self.save()
    
    def archive(self):
        """Archive the message"""
        self.status = self.Status.ARCHIVED
        self.save()
    
    def soft_delete(self):
        """Soft delete - marks as deleted but keeps in database"""
        self.status = self.Status.DELETED
        self.save()
    
    @property
    def is_urgent(self):
        """Check if message is high priority or urgent"""
        return self.priority in [self.Priority.HIGH, self.Priority.URGENT]
    
    @property
    def status_display_class(self):
        """Return Bootstrap class for status badge"""
        status_classes = {
            self.Status.DRAFT: 'secondary',
            self.Status.SENT: 'primary',
            self.Status.READ: 'success',
            self.Status.ARCHIVED: 'warning',
            self.Status.DELETED: 'danger',
        }
        return status_classes.get(self.status, 'secondary')
    
    @property
    def priority_display_class(self):
        """Return Bootstrap class for priority badge"""
        priority_classes = {
            self.Priority.LOW: 'secondary',
            self.Priority.NORMAL: 'info',
            self.Priority.HIGH: 'warning',
            self.Priority.URGENT: 'danger',
        }
        return priority_classes.get(self.priority, 'info')


class ProfileComment(models.Model):
    """Comments on member profiles (like Facebook)"""
    
    profile = models.ForeignKey(MemberProfile, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='profile_comments')
    content = models.TextField()
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='replies')
    is_edited = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Profile Comment'
        verbose_name_plural = 'Profile Comments'
    
    def __str__(self):
        return f"{self.author.username} on {self.profile.user.username}'s profile"


class CommentLike(models.Model):
    """Likes on profile comments"""
    
    comment = models.ForeignKey(ProfileComment, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment_likes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['comment', 'user']
        verbose_name = 'Comment Like'
        verbose_name_plural = 'Comment Likes'
    
    def __str__(self):
        return f"{self.user.username} likes comment by {self.comment.author.username}"


class PhotoAlbum(models.Model):
    """Photo albums for organizing member photos"""
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_albums')
    is_public = models.BooleanField(default=True, help_text="Public albums visible to all members")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Photo Album'
        verbose_name_plural = 'Photo Albums'
    
    def __str__(self):
        return self.title
    
    def photo_count(self):
        return self.photos.count()


class Photo(models.Model):
    """Member photos with comments and likes"""
    
    album = models.ForeignKey(PhotoAlbum, on_delete=models.CASCADE, related_name='photos', blank=True, null=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_photos')
    image = models.ImageField(upload_to='member_photos/')
    caption = models.TextField(blank=True, default='')
    tags = models.CharField(max_length=500, blank=True, default='', help_text="Comma-separated tags")
    event = models.ForeignKey(Event, on_delete=models.SET_NULL, blank=True, null=True, related_name='photos')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Photo'
        verbose_name_plural = 'Photos'
    
    def __str__(self):
        return f"Photo by {self.uploaded_by.username} - {self.created_at.strftime('%Y-%m-%d')}"
    
    def like_count(self):
        return self.photo_likes.count()
    
    def comment_count(self):
        return self.photo_comments.count()


class PhotoComment(models.Model):
    """Comments on photos"""
    
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE, related_name='photo_comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='photo_comments_made')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
        verbose_name = 'Photo Comment'
        verbose_name_plural = 'Photo Comments'
    
    def __str__(self):
        return f"{self.author.username} on photo {self.photo.id}"


class PhotoLike(models.Model):
    """Likes on photos"""
    
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE, related_name='photo_likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='photo_likes_given')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['photo', 'user']
        verbose_name = 'Photo Like'
        verbose_name_plural = 'Photo Likes'
    
    def __str__(self):
        return f"{self.user.username} likes photo {self.photo.id}"


class InvitationCode(models.Model):
    """Invitation codes for member signup"""
    
    code = models.CharField(max_length=50, unique=True, help_text="Unique invitation code")
    email = models.EmailField(help_text="Email address this code is assigned to")
    first_name = models.CharField(max_length=100, blank=True, default='')
    last_name = models.CharField(max_length=100, blank=True, default='')
    member_number = models.CharField(max_length=50, blank=True, default='', help_text="National member number (if applicable)")
    
    is_used = models.BooleanField(default=False)
    used_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='invitation_used')
    used_at = models.DateTimeField(null=True, blank=True)
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='invitations_created')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True, help_text="Optional expiration date")
    
    notes = models.TextField(blank=True, default='', help_text="Internal notes about this invitation")
    
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


# ============================================================================
# STRIPE PAYMENT INTEGRATION
# ============================================================================

class StripeConfiguration(models.Model):
    """Store Stripe API keys and banking information (Treasurer only)"""
    
    treasurer = models.OneToOneField(User, on_delete=models.CASCADE, related_name='stripe_config')
    stripe_publishable_key = models.CharField(max_length=255, help_text="Stripe Publishable Key")
    stripe_secret_key = models.CharField(max_length=255, help_text="Stripe Secret Key (encrypted)")
    stripe_account_id = models.CharField(max_length=255, blank=True, default='', help_text="Stripe Account ID")
    
    # Bank account info (only last 4 digits stored)
    bank_account_name = models.CharField(max_length=255, blank=True, default='')
    bank_account_last_four = models.CharField(max_length=4, blank=True, default='')
    bank_routing_number = models.CharField(max_length=10, blank=True, default='')
    
    # Configuration status
    is_active = models.BooleanField(default=True, help_text="Enable/disable online payments")
    is_test_mode = models.BooleanField(default=True, help_text="Use Stripe test keys")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Stripe Configuration'
        verbose_name_plural = 'Stripe Configuration'
    
    def __str__(self):
        return f"Stripe Config - {self.treasurer.get_full_name()} (Test Mode: {self.is_test_mode})"
    
    def get_secret_key(self):
        """Return the secret key (production environments should use encrypted storage)
        
        Note: For production deployment, implement one of:
        1. Use django-encrypted-model-fields package for field-level encryption
        2. Store in environment variables with RabbitMQ/Vault
        3. Use AWS Secrets Manager or similar cloud secret management
        """
        # WARNING: Keys stored in plaintext in development only
        # Production: Use encrypted field storage or key management service
        return self.stripe_secret_key


class StripePayment(models.Model):
    """Track Stripe payments linked to DuesPayment records"""
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('succeeded', 'Succeeded'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
        ('cancelled', 'Cancelled'),
    ]
    
    dues_payment = models.OneToOneField(DuesPayment, on_delete=models.CASCADE, related_name='stripe_payment', null=True, blank=True)
    member = models.ForeignKey(MemberProfile, on_delete=models.CASCADE, related_name='stripe_payments')
    
    stripe_payment_intent_id = models.CharField(max_length=255, unique=True, help_text="Stripe PaymentIntent ID")
    stripe_charge_id = models.CharField(max_length=255, blank=True, default='', help_text="Stripe Charge ID")
    
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Amount in cents")
    currency = models.CharField(max_length=3, default='USD')
    
    payment_type = models.CharField(max_length=20, choices=DuesPayment.PAYMENT_TYPE_CHOICES)
    description = models.TextField(blank=True, default='')
    
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    # Payment method info
    card_last_four = models.CharField(max_length=4, blank=True, default='')
    card_brand = models.CharField(max_length=20, blank=True, default='')  # visa, mastercard, etc.
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True, help_text="When payment succeeded")
    updated_at = models.DateTimeField(auto_now=True)
    
    # Error handling
    error_message = models.TextField(blank=True, default='', help_text="Error details if payment failed")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Stripe Payment'
        verbose_name_plural = 'Stripe Payments'
    
    def __str__(self):
        return f"{self.member.user.get_full_name()} - ${self.amount/100:.2f} - {self.get_status_display()}"
    
    @property
    def amount_dollars(self):
        """Return amount in dollars"""
        return self.amount / 100


class TwilioConfiguration(models.Model):
    """Store Twilio API credentials for SMS functionality"""
    
    admin = models.OneToOneField(User, on_delete=models.CASCADE, related_name='twilio_config', limit_choices_to={'is_staff': True})
    
    # Twilio API Credentials
    account_sid = models.CharField(max_length=255, help_text="Twilio Account SID")
    auth_token = models.CharField(max_length=255, help_text="Twilio Auth Token (will be encrypted in production)")
    twilio_phone_number = models.CharField(max_length=20, help_text="Twilio phone number (e.g., +1234567890)")
    
    # Configuration
    is_active = models.BooleanField(default=False, help_text="Enable/disable SMS alerts")
    is_test_mode = models.BooleanField(default=True, help_text="Test mode only logs SMS, doesn't send")
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Twilio Configuration'
        verbose_name_plural = 'Twilio Configurations'
    
    def __str__(self):
        return f"Twilio Config - {self.admin.get_full_name()}"


class SMSPreference(models.Model):
    """Track member SMS alert preferences"""
    
    SMS_TYPE_CHOICES = [
        ('announcements', 'Announcements'),
        ('messages', 'Direct Messages'),
        ('dues_reminders', 'Dues Payment Reminders'),
        ('event_alerts', 'Event Alerts'),
        ('all', 'All Alerts'),
    ]
    
    member = models.OneToOneField(MemberProfile, on_delete=models.CASCADE, related_name='sms_preference')
    
    # Opt-in settings
    opted_in = models.BooleanField(default=False, help_text="Member has opted in to SMS alerts")
    phone_number = models.CharField(max_length=20, blank=True, default='', help_text="Member's phone number for SMS")
    
    # Preference types
    receive_announcements = models.BooleanField(default=False)
    receive_messages = models.BooleanField(default=False)
    receive_dues_reminders = models.BooleanField(default=False)
    receive_event_alerts = models.BooleanField(default=False)
    
    # Quiet hours
    quiet_hours_enabled = models.BooleanField(default=False)
    quiet_hours_start = models.TimeField(blank=True, null=True, help_text="Start of quiet hours (e.g., 22:00)")
    quiet_hours_end = models.TimeField(blank=True, null=True, help_text="End of quiet hours (e.g., 08:00)")
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_opted_in = models.DateTimeField(blank=True, null=True)
    last_opted_out = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'SMS Preference'
        verbose_name_plural = 'SMS Preferences'
    
    def __str__(self):
        status = "Opted In" if self.opted_in else "Opted Out"
        return f"{self.member.user.get_full_name()} - {status}"


class SMSLog(models.Model):
    """Log all SMS messages sent for auditing and tracking"""
    
    SMS_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
        ('test', 'Test Mode (Not Sent)'),
    ]
    
    SMS_TYPE_CHOICES = [
        ('announcement', 'Announcement'),
        ('message', 'Direct Message'),
        ('dues_reminder', 'Dues Reminder'),
        ('event_alert', 'Event Alert'),
        ('admin', 'Admin Notification'),
    ]
    
    member = models.ForeignKey(MemberProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='sms_logs')
    
    # Message content
    phone_number = models.CharField(max_length=20)
    message_body = models.TextField()
    sms_type = models.CharField(max_length=20, choices=SMS_TYPE_CHOICES)
    
    # Twilio tracking
    twilio_sid = models.CharField(max_length=255, blank=True, default='', help_text="Twilio message SID")
    status = models.CharField(max_length=20, choices=SMS_STATUS_CHOICES, default='pending')
    
    # Message tracking
    sent_at = models.DateTimeField(blank=True, null=True)
    delivered_at = models.DateTimeField(blank=True, null=True)
    error_message = models.TextField(blank=True, default='')
    
    # Source tracking
    triggered_by = models.CharField(max_length=50, blank=True, default='', help_text="admin_manual, announcement, message, etc.")
    related_object_id = models.IntegerField(blank=True, null=True, help_text="ID of related Announcement/Message/Event")
    related_object_type = models.CharField(max_length=50, blank=True, default='', help_text="Announcement, Message, Event, etc.")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'SMS Log'
        verbose_name_plural = 'SMS Logs'
        indexes = [
            models.Index(fields=['member', '-created_at']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['sms_type', '-created_at']),
        ]
    
    def __str__(self):
        member_name = self.member.user.get_full_name() if self.member else 'Unknown'
        return f"SMS to {member_name} - {self.get_status_display()}"


# ==================== BOUTIQUE MODELS ====================

class Product(models.Model):
    """Merchandise product for boutique"""
    CATEGORY_CHOICES = [
        ('apparel', 'Apparel'),
        ('accessories', 'Accessories'),
        ('drinkware', 'Drinkware'),
        ('other', 'Other'),
    ]
    
    SIZE_CHOICES = [
        ('XS', 'X-Small'),
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
        ('XL', 'X-Large'),
        ('2XL', '2X-Large'),
        ('3XL', '3X-Large'),
        ('4XL', '4X-Large'),
        ('OS', 'One Size'),
    ]
    
    COLOR_CHOICES = [
        ('Black', 'Black'),
        ('White', 'White'),
        ('Blue', 'Blue'),
        ('Royal Blue', 'Royal Blue'),
        ('Navy', 'Navy'),
        ('Gold', 'Gold'),
        ('Silver', 'Silver'),
        ('Gray', 'Gray'),
        ('Red', 'Red'),
        ('Green', 'Green'),
        ('Purple', 'Purple'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='merchandise/')
    inventory = models.IntegerField(default=0, help_text='Total units available')
    sizes = models.CharField(max_length=200, blank=True, default='', help_text='Comma-separated sizes (e.g., XS,S,M,L,XL)')
    colors = models.CharField(max_length=200, blank=True, default='', help_text='Comma-separated colors (e.g., Black,White,Red)')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['category', '-created_at']),
            models.Index(fields=['is_active', '-created_at']),
        ]
    
    def __str__(self):
        return self.name
    
    def get_sizes_list(self):
        """Returns list of sizes for this product"""
        return [s.strip() for s in self.sizes.split(',') if s.strip()] if self.sizes else []
    
    def get_colors_list(self):
        """Returns list of colors for this product"""
        return [c.strip() for c in self.colors.split(',') if c.strip()] if self.colors else []
    
    @classmethod
    def get_available_sizes(cls):
        """Returns list of all standard size options"""
        return [size[0] for size in cls.SIZE_CHOICES]
    
    @classmethod
    def get_available_colors(cls):
        """Returns list of all standard color options"""
        return [color[0] for color in cls.COLOR_CHOICES]


class Cart(models.Model):
    """Shopping cart for users (authenticated or anonymous via session)"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='boutique_cart', null=True, blank=True)
    session_key = models.CharField(max_length=40, blank=True, default='', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(user__isnull=False) | models.Q(session_key__isnull=False),
                name='cart_must_have_user_or_session'
            )
        ]
    
    def __str__(self):
        if self.user:
            return f"Cart for {self.user.username}"
        return f"Cart for session {self.session_key[:8]}..."
    
    def get_total_price(self):
        """Calculate total price of cart items"""
        return sum(item.get_total_price() for item in self.items.all())
    
    def get_total_items(self):
        """Get total number of items in cart"""
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    """Individual items in shopping cart"""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    size = models.CharField(max_length=50, blank=True, default='')
    color = models.CharField(max_length=50, blank=True, default='')
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('cart', 'product', 'size', 'color')
    
    def __str__(self):
        return f"{self.product.name} (x{self.quantity})"
    
    def get_total_price(self):
        """Calculate total price for this cart item"""
        return self.product.price * self.quantity


class Order(models.Model):
    """Customer order (supports both authenticated and anonymous users)"""
    STATUS_CHOICES = [
        ('pending', 'Pending Payment'),
        ('completed', 'Payment Completed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='boutique_orders', null=True, blank=True)
    session_key = models.CharField(max_length=40, blank=True, default='', db_index=True, help_text='Session key for anonymous orders')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    stripe_payment_intent = models.CharField(max_length=250, blank=True, default='')
    email = models.EmailField()
    full_name = models.CharField(max_length=200, blank=True, default='', help_text='Customer full name')
    phone = models.CharField(max_length=20, blank=True, default='', help_text='Contact phone number')
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['session_key', '-created_at']),
            models.Index(fields=['email', '-created_at']),
        ]
    
    def __str__(self):
        if self.user:
            return f"Order #{self.id} - {self.user.username}"
        return f"Order #{self.id} - {self.email}"


class OrderItem(models.Model):
    """Items in an order"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text='Price at time of purchase')
    size = models.CharField(max_length=50, blank=True, default='')
    color = models.CharField(max_length=50, blank=True, default='')
    
    def __str__(self):
        return f"{self.product.name} (x{self.quantity}) in Order #{self.order.id}"
    
    def get_total_price(self):
        """Calculate total price for this order item"""
        return self.price * self.quantity
