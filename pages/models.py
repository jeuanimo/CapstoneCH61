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

# Upload path constants
SITE_BRANDING_PATH = 'site_branding/'

# Program label constants (SonarQube: avoid duplicate literals)
PROGRAM_LABEL_SOCIAL_ACTION = 'Social Action'
PROGRAM_LABEL_SIGMA_BETA = 'Sigma Beta Club'
PROGRAM_LABEL_EDUCATION = 'Education'
PROGRAM_LABEL_BBB = 'Bigger & Better Business'
PROGRAM_LABEL_SIGMA_WELLNESS = 'Sigma Wellness'
PROGRAM_LABEL_BUSINESS = 'Business'
PROGRAM_LABEL_OTHER = 'Other'
PROGRAM_LABEL_NO_PROGRAM = 'No Program'


class Category(models.Model):
    """
    Event categories for organizing events
    
    Fields:
        name (CharField): Unique category name
        description (TextField): Optional description of the category
        color (CharField): Hex color code for UI display (#164f90 default)
        created_at (DateTimeField): Auto-set timestamp when created
    
    Usage:
        category = Category.objects.create(name=PROGRAM_LABEL_SOCIAL_ACTION, color='#164f90')
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
        ('social_action', PROGRAM_LABEL_SOCIAL_ACTION),
        ('education', PROGRAM_LABEL_EDUCATION),
        ('business', PROGRAM_LABEL_BUSINESS),
        ('sigma_beta_club', PROGRAM_LABEL_SIGMA_BETA),
        ('sigma_wellness', PROGRAM_LABEL_SIGMA_WELLNESS),
        ('other', PROGRAM_LABEL_OTHER),
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
    member = models.ForeignKey(
        'MemberProfile', 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True, 
        related_name='leadership_positions',
        help_text="Link to member profile (allows member to manage their own photo)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['display_order', 'position']
        verbose_name = 'Chapter Leader'
        verbose_name_plural = 'Chapter Leadership'
    
    def __str__(self):
        position_name = self.position_custom if self.position_custom else self.get_position_display()
        return f"{self.full_name} - {position_name}"
    
    def get_position_title(self):
        """Return the display position title - custom title overrides category"""
        if self.position_custom:
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
    birthday = models.DateField(blank=True, null=True, help_text="Member's birthday")
    emergency_contact_name = models.CharField(max_length=200, blank=True, default='')
    emergency_contact_phone = models.CharField(max_length=20, blank=True, default='')
    address = models.TextField(blank=True, default='')
    profile_image = models.ImageField(upload_to='members/', blank=True, null=True)
    cover_image = models.ImageField(upload_to='member_covers/', blank=True, null=True, help_text="Cover photo for profile page (recommended: 820x312)")
    bio = models.TextField(blank=True, default='')
    dues_current = models.BooleanField(default=False, help_text="Are dues paid up to date?")
    is_officer = models.BooleanField(default=False, help_text="Is this member an officer with admin privileges?")
    last_seen = models.DateTimeField(blank=True, null=True, help_text="Last activity timestamp for online status")
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
    
    @property
    def is_online(self):
        """Check if member is online (active within last 5 minutes)"""
        if not self.last_seen:
            return False
        from datetime import timedelta
        from django.utils import timezone
        return timezone.now() - self.last_seen < timedelta(minutes=5)
    
    @property
    def last_seen_display(self):
        """Human-readable last seen time"""
        if not self.last_seen:
            return "Never"
        from django.utils import timezone
        from datetime import timedelta
        now = timezone.now()
        diff = now - self.last_seen
        
        if diff < timedelta(minutes=1):
            return "Just now"
        elif diff < timedelta(minutes=5):
            return "Online"
        elif diff < timedelta(hours=1):
            minutes = int(diff.total_seconds() / 60)
            return f"{minutes} min ago"
        elif diff < timedelta(days=1):
            hours = int(diff.total_seconds() / 3600)
            return f"{hours} hr ago"
        else:
            days = diff.days
            return f"{days} day{'s' if days > 1 else ''} ago"
    
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
    
    PROGRAM_CHOICES = [
        ('', PROGRAM_LABEL_NO_PROGRAM),
        ('bbb', PROGRAM_LABEL_BBB),
        ('education', PROGRAM_LABEL_EDUCATION),
        ('social_action', PROGRAM_LABEL_SOCIAL_ACTION),
        ('sigma_beta', PROGRAM_LABEL_SIGMA_BETA),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    program = models.CharField(max_length=20, choices=PROGRAM_CHOICES, blank=True, default='', help_text="Which fraternity program this album belongs to")
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
    
    PROGRAM_CHOICES = [
        ('', PROGRAM_LABEL_NO_PROGRAM),
        ('bbb', PROGRAM_LABEL_BBB),
        ('education', PROGRAM_LABEL_EDUCATION),
        ('social_action', PROGRAM_LABEL_SOCIAL_ACTION),
        ('sigma_beta', PROGRAM_LABEL_SIGMA_BETA),
    ]
    
    album = models.ForeignKey(PhotoAlbum, on_delete=models.CASCADE, related_name='photos', blank=True, null=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_photos')
    image = models.ImageField(upload_to='member_photos/')
    caption = models.TextField(blank=True, default='')
    tags = models.CharField(max_length=500, blank=True, default='', help_text="Comma-separated tags")
    program = models.CharField(max_length=20, choices=PROGRAM_CHOICES, blank=True, default='', help_text="Tag this photo for a program to show on homepage carousel")
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


# ============================================================================
# EVENT TICKETING SYSTEM
# ============================================================================

class EventTicket(models.Model):
    """
    Event ticket listing for sale.
    Similar to Product model but for event tickets.
    """
    TICKET_TYPE_CHOICES = [
        ('general', 'General Admission'),
        ('vip', 'VIP'),
        ('early_bird', 'Early Bird'),
        ('member', 'Member Only'),
        ('group', 'Group Package'),
    ]
    
    # Event Information
    event_name = models.CharField(max_length=200, help_text='Name of the event')
    description = models.TextField(blank=True, default='', help_text='Event description and details')
    event_date = models.DateField(help_text='Date of the event')
    event_time = models.TimeField(help_text='Start time of the event')
    end_time = models.TimeField(blank=True, null=True, help_text='End time (optional)')
    
    # Location
    venue_name = models.CharField(max_length=200, help_text='Name of the venue')
    location = models.CharField(max_length=300, help_text='Full address of the venue')
    city = models.CharField(max_length=100, blank=True, default='')
    state = models.CharField(max_length=50, blank=True, default='')
    
    # Ticket Details
    ticket_type = models.CharField(max_length=50, choices=TICKET_TYPE_CHOICES, default='general')
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text='Price per ticket')
    quantity_available = models.PositiveIntegerField(default=0, help_text='Total tickets available for sale')
    quantity_sold = models.PositiveIntegerField(default=0, help_text='Number of tickets sold')
    max_per_order = models.PositiveIntegerField(default=10, help_text='Maximum tickets per order')
    
    # Display
    image = models.ImageField(upload_to='event_tickets/', blank=True, null=True, help_text='Event promotional image')
    is_active = models.BooleanField(default=True, help_text='Active tickets are visible for purchase')
    is_featured = models.BooleanField(default=False, help_text='Featured events appear first')
    requires_member = models.BooleanField(default=False, help_text='Only members can purchase')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='event_tickets_created'
    )
    
    class Meta:
        ordering = ['event_date', 'event_time']
        indexes = [
            models.Index(fields=['event_date', 'is_active']),
            models.Index(fields=['is_active', '-created_at']),
            models.Index(fields=['is_featured', 'event_date']),
        ]
        verbose_name = 'Event Ticket'
        verbose_name_plural = 'Event Tickets'
    
    def __str__(self):
        return f"{self.event_name} - {self.event_date}"
    
    @property
    def tickets_remaining(self):
        """Calculate remaining tickets available"""
        return max(0, self.quantity_available - self.quantity_sold)
    
    @property
    def is_sold_out(self):
        """Check if event is sold out"""
        return self.tickets_remaining <= 0
    
    @property
    def is_past_event(self):
        """Check if event date has passed"""
        from datetime import date
        return self.event_date < date.today()
    
    def can_purchase(self, quantity=1):
        """Check if the requested quantity can be purchased"""
        return (
            self.is_active and 
            not self.is_sold_out and 
            not self.is_past_event and
            quantity <= self.tickets_remaining and
            quantity <= self.max_per_order
        )


class TicketPurchase(models.Model):
    """
    Record of ticket purchase.
    Similar to Order model but specifically for event tickets.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending Payment'),
        ('completed', 'Payment Completed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    # Ticket Reference
    ticket = models.ForeignKey(EventTicket, on_delete=models.CASCADE, related_name='purchases')
    quantity = models.PositiveIntegerField(default=1)
    price_per_ticket = models.DecimalField(max_digits=10, decimal_places=2, help_text='Price at time of purchase')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Buyer Information
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='ticket_purchases')
    email = models.EmailField(help_text='Email for ticket confirmation')
    full_name = models.CharField(max_length=200, help_text='Name on the ticket')
    phone = models.CharField(max_length=20, blank=True, default='')
    
    # Payment
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    stripe_payment_intent = models.CharField(max_length=250, blank=True, default='')
    
    # Confirmation
    confirmation_code = models.CharField(max_length=20, unique=True, help_text='Unique confirmation code')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['email', '-created_at']),
            models.Index(fields=['confirmation_code']),
            models.Index(fields=['status', '-created_at']),
        ]
        verbose_name = 'Ticket Purchase'
        verbose_name_plural = 'Ticket Purchases'
    
    def __str__(self):
        return f"Ticket #{self.confirmation_code} - {self.ticket.event_name}"
    
    def save(self, *args, **kwargs):
        # Generate confirmation code if not set
        if not self.confirmation_code:
            import random
            import string
            self.confirmation_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        # Calculate total if not set
        if not self.total_price:
            self.total_price = self.price_per_ticket * self.quantity
        super().save(*args, **kwargs)


class ChapterHistoryBackup(models.Model):
    """
    Stores backups of chapter history sections for undo/restore functionality.
    
    A backup is created before import operations (CSV, TXT, DOCX) so users
    can revert changes if something goes wrong.
    """
    
    BACKUP_TYPE_CHOICES = [
        ('pre_import', 'Before Import'),
        ('pre_clear', 'Before Clear All'),
        ('manual', 'Manual Backup'),
    ]
    
    name = models.CharField(
        max_length=200,
        help_text='Descriptive name for this backup'
    )
    backup_type = models.CharField(
        max_length=20,
        choices=BACKUP_TYPE_CHOICES,
        default='pre_import'
    )
    data = models.JSONField(
        help_text='Serialized backup of all history sections'
    )
    section_count = models.PositiveIntegerField(
        default=0,
        help_text='Number of sections in this backup'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='history_backups_created'
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Chapter History Backup'
        verbose_name_plural = 'Chapter History Backups'
    
    def __str__(self):
        return f"{self.name} ({self.section_count} sections) - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class ChapterHistorySection(models.Model):
    """
    Stores editable sections for the chapter history page.
    
    Officers can add/edit/delete history sections through the admin console
    without needing to modify HTML directly.
    """
    
    SECTION_TYPE_CHOICES = [
        ('intro', 'Introduction'),
        ('founding', 'Founding Story'),
        ('milestones', 'Milestones & Achievements'),
        ('leadership', 'Leadership Legacy'),
        ('community', 'Community Service'),
        ('national', 'National Connection'),
        ('custom', 'Custom Section'),
    ]
    
    title = models.CharField(
        max_length=200,
        help_text='Section heading (e.g., "Our Beginning")'
    )
    section_type = models.CharField(
        max_length=20,
        choices=SECTION_TYPE_CHOICES,
        default='custom',
        help_text='Type of content section'
    )
    content = models.TextField(
        help_text='Section content (supports basic HTML formatting)'
    )
    display_order = models.PositiveIntegerField(
        default=0,
        help_text='Order in which sections appear (lower = first)'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Inactive sections will not display on the page'
    )
    image = models.ImageField(
        upload_to='history_images/',
        blank=True,
        null=True,
        help_text='Optional image for this section'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='history_sections_created'
    )
    
    class Meta:
        ordering = ['display_order', 'created_at']
        verbose_name = 'Chapter History Section'
        verbose_name_plural = 'Chapter History Sections'
    
    def __str__(self):
        return f"{self.title} ({self.get_section_type_display()})"


class SiteConfiguration(models.Model):
    """
    Singleton model for site-wide configuration and branding.
    Only one instance should exist - managed via admin portal.
    
    Allows officers/admins to customize:
    - Chapter name and organization name
    - Chapter details (president, charter date, address, etc.)
    - Logos (chapter logo, PBS seal, favicon)
    - Social media links
    - Contact information
    - SEO meta tags
    - Chatbot settings
    - Feature toggles
    - Footer text
    """
    
    # Organization Branding
    organization_name = models.CharField(
        max_length=200, 
        default='Phi Beta Sigma Fraternity, Inc',
        help_text='Main organization name displayed in header'
    )
    chapter_name = models.CharField(
        max_length=200, 
        default='Nu Gamma Sigma Chapter',
        help_text='Chapter name displayed below organization name'
    )
    
    # Chapter Details
    chapter_president = models.CharField(
        max_length=200,
        blank=True,
        default='',
        help_text='Name of the current chapter president'
    )
    charter_date = models.DateField(
        blank=True,
        null=True,
        help_text='Date the chapter was chartered'
    )
    chapter_region = models.CharField(
        max_length=100,
        blank=True,
        default='',
        help_text='Regional affiliation (e.g., Great Lakes Region)'
    )
    mailing_address = models.CharField(
        max_length=300,
        blank=True,
        default='',
        help_text='Official chapter mailing address'
    )
    city_state = models.CharField(
        max_length=200,
        blank=True,
        default='',
        help_text='City and state (e.g., Belleville, Illinois)'
    )
    service_areas = models.CharField(
        max_length=500,
        blank=True,
        default='',
        help_text='Areas served by the chapter (e.g., St. Clair County, Madison County)'
    )
    
    # About Us Content
    about_us_text = models.TextField(
        blank=True,
        default='',
        help_text='Main "About the Chapter" text displayed on the About page and home page modal'
    )
    mission_statement = models.TextField(
        blank=True,
        default='',
        help_text='Chapter mission statement'
    )
    chapter_legacy = models.TextField(
        blank=True,
        default='',
        help_text='Chapter legacy/history summary text'
    )
    
    # Logo Images
    chapter_logo = models.ImageField(
        upload_to=SITE_BRANDING_PATH,
        blank=True,
        null=True,
        help_text='Chapter-specific logo (optional)'
    )
    pbs_seal = models.ImageField(
        upload_to=SITE_BRANDING_PATH,
        blank=True,
        null=True,
        help_text='Phi Beta Sigma seal/logo displayed in header'
    )
    favicon = models.ImageField(
        upload_to=SITE_BRANDING_PATH,
        blank=True,
        null=True,
        help_text='Site favicon (browser tab icon)'
    )
    
    # Social Media Links
    facebook_url = models.URLField(
        blank=True, 
        default='',
        help_text='Facebook page URL'
    )
    instagram_url = models.URLField(
        blank=True, 
        default='',
        help_text='Instagram profile URL'
    )
    twitter_url = models.URLField(
        blank=True, 
        default='',
        help_text='Twitter/X profile URL'
    )
    email_address = models.EmailField(
        blank=True, 
        default='',
        help_text='Contact email address (displayed site-wide and used for contact form)'
    )
    
    # Contact Information
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        default='',
        help_text='Chapter phone number'
    )
    meeting_location = models.CharField(
        max_length=300,
        blank=True,
        default='',
        help_text='Where the chapter holds meetings'
    )
    meeting_schedule = models.CharField(
        max_length=200,
        blank=True,
        default='',
        help_text='When the chapter meets (e.g., First Saturday of each month at 10 AM)'
    )
    pbs_hq_url = models.URLField(
        blank=True,
        default='https://phibetasigma1914.org/',
        help_text='Link to Phi Beta Sigma national headquarters website'
    )
    
    # SEO & Meta Tags
    meta_description = models.CharField(
        max_length=300,
        blank=True,
        default='',
        help_text='Site description for search engines (recommended 150-160 characters)'
    )
    meta_keywords = models.CharField(
        max_length=500,
        blank=True,
        default='',
        help_text='SEO keywords (comma-separated)'
    )
    og_image = models.ImageField(
        upload_to=SITE_BRANDING_PATH,
        blank=True,
        null=True,
        help_text='Default image for social media sharing'
    )
    
    # Chatbot Settings
    chatbot_enabled = models.BooleanField(
        default=True,
        help_text='Enable or disable the chatbot widget site-wide'
    )
    chatbot_welcome_message = models.TextField(
        blank=True,
        default="I'm here to help answer questions about our fraternity. You can ask me about our history, membership, events, values, and more.",
        help_text='Welcome message displayed when chatbot opens'
    )
    chatbot_rate_limit = models.PositiveIntegerField(
        default=30,
        help_text='Maximum chatbot requests per minute per IP address'
    )
    
    # Theme/Appearance
    primary_color = models.CharField(
        max_length=7,
        blank=True,
        default='#0047AB',
        help_text='Primary brand color (hex code, e.g., #0047AB)'
    )
    secondary_color = models.CharField(
        max_length=7,
        blank=True,
        default='#003380',
        help_text='Secondary brand color (hex code)'
    )
    dark_mode_default = models.BooleanField(
        default=False,
        help_text='Make dark mode the default for visitors'
    )
    
    # Feature Toggles
    show_boutique = models.BooleanField(
        default=True,
        help_text='Show the merchandise boutique section'
    )
    
    # Boutique Type Options
    BOUTIQUE_TYPE_CHOICES = [
        ('internal', 'Use Internal Boutique'),
        ('external', 'Link to External Store'),
    ]
    boutique_type = models.CharField(
        max_length=20,
        choices=BOUTIQUE_TYPE_CHOICES,
        default='internal',
        help_text='Choose between hosting your own boutique or linking to an external store'
    )
    external_store_url = models.URLField(
        blank=True,
        default='',
        help_text='URL of your external e-store (e.g., shopify, etsy, etc.)'
    )
    external_store_name = models.CharField(
        max_length=100,
        blank=True,
        default='Shop',
        help_text='Text to display for the store link (e.g., "Shop Now", "Visit Our Store")'
    )
    
    show_events = models.BooleanField(
        default=True,
        help_text='Show the events calendar section'
    )
    
    # Event Ticketing Feature
    show_event_tickets = models.BooleanField(
        default=False,
        help_text='Show the event ticketing section'
    )
    
    # Event Ticketing Type Options
    EVENT_TICKETS_TYPE_CHOICES = [
        ('internal', 'Use Internal Ticketing'),
        ('external', 'Link to External Ticket Site'),
    ]
    event_tickets_type = models.CharField(
        max_length=20,
        choices=EVENT_TICKETS_TYPE_CHOICES,
        default='internal',
        help_text='Choose between hosting your own ticketing or linking to an external site'
    )
    external_tickets_url = models.URLField(
        blank=True,
        default='',
        help_text='URL of your external ticket site (e.g., Eventbrite, Ticketmaster, etc.)'
    )
    external_tickets_name = models.CharField(
        max_length=100,
        blank=True,
        default='Buy Tickets',
        help_text='Text to display for the tickets link (e.g., "Get Tickets", "Buy Now")'
    )
    
    maintenance_mode = models.BooleanField(
        default=False,
        help_text='Put the site in maintenance mode (only staff can access)'
    )
    maintenance_message = models.CharField(
        max_length=500,
        blank=True,
        default='We are currently performing scheduled maintenance. Please check back soon.',
        help_text='Message to display during maintenance mode'
    )
    
    # Footer Content
    footer_text = models.CharField(
        max_length=500,
        default='© 2026 Phi Beta Sigma Fraternity, Incorporated. Nu Gamma Sigma Chapter',
        help_text='Footer copyright/text'
    )
    
    # Metadata
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='site_config_updates'
    )
    
    class Meta:
        verbose_name = 'Site Configuration'
        verbose_name_plural = 'Site Configuration'
    
    def __str__(self):
        return f"Site Configuration (Last updated: {self.updated_at.strftime('%Y-%m-%d %H:%M') if self.updated_at else 'Never'})"
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists (singleton pattern)
        if not self.pk and SiteConfiguration.objects.exists():
            # Update existing instead of creating new
            existing = SiteConfiguration.objects.first()
            self.pk = existing.pk
        super().save(*args, **kwargs)
    
    @classmethod
    def get_config(cls):
        """Get the site configuration, creating default if none exists"""
        config, _ = cls.objects.get_or_create(pk=1)
        return config


# ============================================================================
# ANALYTICS & PRIVACY MODELS
# ============================================================================

class PageView(models.Model):
    """
    Track page views for DIY analytics.
    Privacy-respecting: no personal identifiers stored for anonymous users.
    """
    path = models.CharField(max_length=500, db_index=True, help_text="URL path visited")
    method = models.CharField(max_length=10, default='GET')
    user = models.ForeignKey(
        User, 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL,
        related_name='page_views',
        help_text="Logged in user (null for anonymous)"
    )
    session_key = models.CharField(
        max_length=40, 
        blank=True, 
        default='',
        help_text="Session key (hashed for privacy)"
    )
    referrer = models.CharField(max_length=500, blank=True, default='')
    user_agent = models.CharField(max_length=500, blank=True, default='')
    ip_hash = models.CharField(
        max_length=64, 
        blank=True, 
        default='',
        help_text="Hashed IP for privacy (not reversible)"
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    response_code = models.IntegerField(default=200)
    
    # Device info (parsed from user agent)
    is_mobile = models.BooleanField(default=False)
    is_bot = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Page View'
        verbose_name_plural = 'Page Views'
        indexes = [
            models.Index(fields=['path', '-timestamp']),
            models.Index(fields=['-timestamp']),
            models.Index(fields=['user', '-timestamp']),
        ]
    
    def __str__(self):
        user_str = self.user.username if self.user else 'Anonymous'
        return f"{self.path} - {user_str} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
    
    @classmethod
    def get_popular_pages(cls, days=30, limit=10):
        """Get most visited pages in the last N days"""
        from django.utils import timezone
        from django.db.models import Count
        from datetime import timedelta
        
        cutoff = timezone.now() - timedelta(days=days)
        return cls.objects.filter(
            timestamp__gte=cutoff,
            is_bot=False
        ).values('path').annotate(
            views=Count('id')
        ).order_by('-views')[:limit]
    
    @classmethod
    def get_daily_stats(cls, days=30):
        """Get daily page view counts"""
        from django.utils import timezone
        from django.db.models import Count
        from django.db.models.functions import TruncDate
        from datetime import timedelta
        
        cutoff = timezone.now() - timedelta(days=days)
        return cls.objects.filter(
            timestamp__gte=cutoff,
            is_bot=False
        ).annotate(
            date=TruncDate('timestamp')
        ).values('date').annotate(
            views=Count('id')
        ).order_by('date')


class CookieConsent(models.Model):
    """
    Track user cookie consent preferences for GDPR compliance.
    """
    CONSENT_CHOICES = [
        ('essential', 'Essential Only'),
        ('functional', 'Essential + Functional'),
        ('analytics', 'Essential + Functional + Analytics'),
        ('all', 'All Cookies'),
    ]
    
    session_key = models.CharField(
        max_length=40, 
        unique=True, 
        db_index=True,
        help_text="Browser session key"
    )
    user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='cookie_consents'
    )
    consent_level = models.CharField(
        max_length=20,
        choices=CONSENT_CHOICES,
        default='essential'
    )
    consent_given = models.BooleanField(default=False)
    consent_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ip_hash = models.CharField(max_length=64, blank=True, default='')
    
    # Granular consent tracking
    essential_cookies = models.BooleanField(default=True)  # Always true
    functional_cookies = models.BooleanField(default=False)
    analytics_cookies = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Cookie Consent'
        verbose_name_plural = 'Cookie Consents'
        ordering = ['-consent_date']
    
    def __str__(self):
        user_str = self.user.username if self.user else f'Session {self.session_key[:8]}...'
        return f"{user_str} - {self.get_consent_level_display()}"


# =============================================================================
# ZOOM INTEGRATION MODELS
# =============================================================================

class ZoomConfiguration(models.Model):
    """
    Store Zoom SDK credentials for embedded meetings.
    Only one active configuration should exist at a time.
    
    Two types of credentials:
    1. Meeting SDK credentials (sdk_key, sdk_secret) - for generating SDK signatures
    2. OAuth Server-to-Server credentials - for API calls (fetching ZAK tokens for host mode)
    
    ZAK (Zoom Access Key) is required for hosts to START meetings via the SDK.
    This requires Server-to-Server OAuth credentials from a separate Zoom app.
    """
    admin = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='zoom_configs',
        help_text="Admin who configured this"
    )
    
    # Meeting SDK Credentials (for signature generation)
    sdk_key = models.CharField(
        max_length=255,
        help_text="Zoom Meeting SDK Key (Client ID)"
    )
    sdk_secret = models.CharField(
        max_length=255,
        help_text="Zoom Meeting SDK Secret (Client Secret)"
    )
    
    # OAuth Server-to-Server Credentials (for ZAK token retrieval)
    oauth_account_id = models.CharField(
        max_length=255,
        blank=True,
        default='',
        help_text="Zoom Account ID for Server-to-Server OAuth"
    )
    oauth_client_id = models.CharField(
        max_length=255,
        blank=True,
        default='',
        help_text="OAuth App Client ID (Server-to-Server)"
    )
    oauth_client_secret = models.CharField(
        max_length=255,
        blank=True,
        default='',
        help_text="OAuth App Client Secret (Server-to-Server)"
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Zoom Configuration'
        verbose_name_plural = 'Zoom Configurations'
    
    def __str__(self):
        status = "Active" if self.is_active else "Inactive"
        return f"Zoom Config ({status})"
    
    def save(self, *args, **kwargs):
        # Ensure only one active config
        if self.is_active:
            ZoomConfiguration.objects.filter(is_active=True).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)


class ZoomMeeting(models.Model):
    """
    Stores virtual meeting information for chapter meetings.
    Supports multiple platforms: Zoom (embedded), Google Meet, Teams, etc.
    """
    PLATFORM_CHOICES = [
        ('zoom', 'Zoom (Embedded)'),
        ('google_meet', 'Google Meet'),
        ('teams', 'Microsoft Teams'),
        ('webex', 'Cisco Webex'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    
    # Platform selection
    platform = models.CharField(
        max_length=20,
        choices=PLATFORM_CHOICES,
        default='zoom',
        help_text="Select the meeting platform"
    )
    
    # For Zoom embedded meetings
    meeting_number = models.CharField(
        max_length=50,
        blank=True,
        default='',
        help_text="Zoom Meeting ID (for Zoom only)"
    )
    meeting_password = models.CharField(
        max_length=50,
        blank=True,
        default='',
        help_text="Meeting password (if required)"
    )
    
    # For external platforms (Google Meet, Teams, etc.)
    meeting_url = models.URLField(
        max_length=500,
        blank=True,
        default='',
        help_text="Meeting link for Google Meet, Teams, or other platforms"
    )
    
    host = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='hosted_meetings'
    )
    event = models.ForeignKey(
        'Event',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='zoom_meetings',
        help_text="Link to an event (optional)"
    )
    scheduled_time = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(
        default=60,
        help_text="Expected meeting duration in minutes"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='scheduled'
    )
    # Access control
    members_only = models.BooleanField(
        default=True,
        help_text="Only logged-in members can join"
    )
    financial_only = models.BooleanField(
        default=False,
        help_text="Only financial members can join"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Virtual Meeting'
        verbose_name_plural = 'Virtual Meetings'
        ordering = ['-scheduled_time']
    
    def __str__(self):
        return f"{self.title} - {self.scheduled_time.strftime('%Y-%m-%d %H:%M')}"
    
    @property
    def is_upcoming(self):
        return self.status == 'scheduled' and self.scheduled_time > timezone.now()
    
    @property
    def is_active(self):
        return self.status == 'in_progress'
    
    @property
    def is_zoom_embedded(self):
        """Check if this meeting uses embedded Zoom"""
        return self.platform == 'zoom' and bool(self.meeting_number)
    
    @property
    def is_external_link(self):
        """Check if this meeting uses an external link"""
        return self.platform != 'zoom' or (self.platform == 'zoom' and not self.meeting_number and bool(self.meeting_url))
    
    def get_join_url(self):
        """Get the URL to join this meeting (for external platforms)"""
        if self.meeting_url:
            return self.meeting_url
        return None
    
    def get_platform_icon(self):
        """Get Font Awesome icon for platform"""
        icons = {
            'zoom': 'fa-video',
            'google_meet': 'fa-google',
            'teams': 'fa-microsoft',
            'webex': 'fa-video',
            'other': 'fa-link',
        }
        return icons.get(self.platform, 'fa-video')
    
    def get_end_time(self):
        from datetime import timedelta
        return self.scheduled_time + timedelta(minutes=self.duration_minutes)


# =============================================================================
# POLLING / VOTING MODELS
# =============================================================================

class Poll(models.Model):
    """
    A poll or vote for members to participate in.
    Can be linked to a meeting for live voting.
    """
    POLL_TYPE_CHOICES = [
        ('meeting', 'Meeting Poll'),
        ('general', 'General Poll'),
        ('election', 'Election'),
        ('motion', 'Motion Vote'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(
        blank=True,
        default='',
        help_text="Explain what members are voting on"
    )
    poll_type = models.CharField(
        max_length=20,
        choices=POLL_TYPE_CHOICES,
        default='general'
    )
    meeting = models.ForeignKey(
        ZoomMeeting,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='polls',
        help_text="Associate with a meeting (optional)"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_polls'
    )
    
    # Privacy settings (configurable per poll)
    is_anonymous = models.BooleanField(
        default=False,
        help_text="If true, individual votes are not recorded"
    )
    show_results_during = models.BooleanField(
        default=True,
        help_text="Show live results while voting is open"
    )
    
    # Voting rules
    allow_multiple = models.BooleanField(
        default=False,
        help_text="Allow selecting multiple options"
    )
    max_selections = models.PositiveIntegerField(
        default=1,
        help_text="Maximum selections if multiple allowed"
    )
    
    # Access control
    financial_only = models.BooleanField(
        default=False,
        help_text="Only financial members can vote"
    )
    
    # Timing
    is_active = models.BooleanField(default=True)
    starts_at = models.DateTimeField(default=timezone.now)
    ends_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Leave blank for no deadline"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Poll'
        verbose_name_plural = 'Polls'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.get_poll_type_display()})"
    
    @property
    def is_open(self):
        """Check if voting is currently open"""
        now = timezone.now()
        if not self.is_active:
            return False
        if self.starts_at > now:
            return False
        if self.ends_at and self.ends_at < now:
            return False
        return True
    
    @property
    def total_votes(self):
        return self.votes.count()
    
    @property
    def total_voters(self):
        return self.votes.values('voter').distinct().count()
    
    def user_has_voted(self, user):
        """Check if a user has already voted"""
        return self.votes.filter(voter=user).exists()
    
    def get_results(self):
        """Get vote counts per option"""
        from django.db.models import Count
        return self.options.annotate(
            votes_count=Count('votes')
        ).order_by('-votes_count')


class PollOption(models.Model):
    """
    An option/choice within a poll.
    """
    poll = models.ForeignKey(
        Poll,
        on_delete=models.CASCADE,
        related_name='options'
    )
    text = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = 'Poll Option'
        verbose_name_plural = 'Poll Options'
        ordering = ['order', 'id']
    
    def __str__(self):
        return f"{self.poll.title}: {self.text}"
    
    @property
    def vote_count(self):
        return self.votes.count()
    
    @property
    def percentage(self):
        total = self.poll.total_votes
        if total == 0:
            return 0
        return round((self.vote_count / total) * 100, 1)


class Vote(models.Model):
    """
    A member's vote on a poll option.
    """
    poll = models.ForeignKey(
        Poll,
        on_delete=models.CASCADE,
        related_name='votes'
    )
    option = models.ForeignKey(
        PollOption,
        on_delete=models.CASCADE,
        related_name='votes'
    )
    voter = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='poll_votes'
    )
    voted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Vote'
        verbose_name_plural = 'Votes'
        # For single-choice polls, enforce one vote per user per poll
        # Multiple choice handled at view level
        ordering = ['-voted_at']
    
    def __str__(self):
        voter_name = self.voter.username if self.voter else 'Anonymous'
        return f"{voter_name} -> {self.option.text}"


class MeetingVoteRecord(models.Model):
    """
    Official record of motion votes for meeting minutes.
    Captures who voted, the motion, date, and final result.
    """
    RESULT_CHOICES = [
        ('passed', 'Passed'),
        ('failed', 'Failed'),
        ('tabled', 'Tabled'),
        ('withdrawn', 'Withdrawn'),
    ]
    
    # Motion details
    motion_title = models.CharField(
        max_length=300,
        help_text="The motion being voted on"
    )
    motion_description = models.TextField(
        blank=True,
        default='',
        help_text="Additional details about the motion"
    )
    
    # Meeting info
    meeting = models.ForeignKey(
        ZoomMeeting,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='vote_records',
        help_text="Associated meeting (optional)"
    )
    meeting_date = models.DateField(
        help_text="Date of the meeting/vote"
    )
    
    # Voting results
    result = models.CharField(
        max_length=20,
        choices=RESULT_CHOICES,
        default='passed'
    )
    votes_for = models.PositiveIntegerField(default=0)
    votes_against = models.PositiveIntegerField(default=0)
    abstentions = models.PositiveIntegerField(default=0)
    
    # Who voted how (for recorded votes)
    voters_for = models.TextField(
        blank=True,
        default='',
        help_text="Names of members who voted in favor (comma-separated)"
    )
    voters_against = models.TextField(
        blank=True,
        default='',
        help_text="Names of members who voted against (comma-separated)"
    )
    voters_abstained = models.TextField(
        blank=True,
        default='',
        help_text="Names of members who abstained (comma-separated)"
    )
    
    # Motion maker/seconder
    moved_by = models.CharField(
        max_length=100,
        blank=True,
        default='',
        help_text="Name of member who made the motion"
    )
    seconded_by = models.CharField(
        max_length=100,
        blank=True,
        default='',
        help_text="Name of member who seconded"
    )
    
    # Link to poll if created from one
    poll = models.ForeignKey(
        Poll,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='vote_records',
        help_text="Associated poll if voted electronically"
    )
    
    # Metadata
    recorded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='recorded_votes'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(
        blank=True,
        default='',
        help_text="Additional notes for the record"
    )
    
    class Meta:
        verbose_name = 'Meeting Vote Record'
        verbose_name_plural = 'Meeting Vote Records'
        ordering = ['-meeting_date', '-created_at']
    
    def __str__(self):
        return f"{self.motion_title} - {self.get_result_display()} ({self.meeting_date})"
    
    @property
    def meeting_month_year(self):
        """Return formatted month and year"""
        return self.meeting_date.strftime('%B %Y')
    
    @property
    def total_votes(self):
        """Total votes cast"""
        return self.votes_for + self.votes_against + self.abstentions
    
    @property
    def voters_for_list(self):
        """Return list of names who voted for"""
        if not self.voters_for:
            return []
        return [name.strip() for name in self.voters_for.split(',') if name.strip()]
    
    @property
    def voters_against_list(self):
        """Return list of names who voted against"""
        if not self.voters_against:
            return []
        return [name.strip() for name in self.voters_against.split(',') if name.strip()]
    
    @property
    def voters_abstained_list(self):
        """Return list of names who abstained"""
        if not self.voters_abstained:
            return []
        return [name.strip() for name in self.voters_abstained.split(',') if name.strip()]
