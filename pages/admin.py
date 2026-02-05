from django.contrib import admin
from .models import (
    Event, ChapterLeadership, MemberProfile, DuesPayment,
    EventAttendance, Announcement, AnnouncementView, Document, Message, 
    ProfileComment, CommentLike, PhotoAlbum, Photo, 
    PhotoComment, PhotoLike, InvitationCode,
    Product, Cart, CartItem, Order, OrderItem
)

class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'location', 'image')
    list_filter = ('start_date', 'category')
    search_fields = ('title', 'description', 'location')
    fieldsets = (
        ('Event Information', {
            'fields': ('title', 'description', 'category')
        }),
        ('Date & Time', {
            'fields': ('start_date', 'end_date')
        }),
        ('Location & Media', {
            'fields': ('location', 'image')
        }),
    )

class ChapterLeadershipAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'position', 'display_order', 'is_active')
    list_filter = ('position', 'is_active')
    search_fields = ('full_name', 'bio')
    list_editable = ('display_order', 'is_active')
    fieldsets = (
        ('Personal Information', {
            'fields': ('full_name', 'position', 'profile_image')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone')
        }),
        ('Biography', {
            'fields': ('bio',)
        }),
        ('Display Settings', {
            'fields': ('display_order', 'is_active')
        }),
    )

admin.site.register(Event, EventAdmin)
admin.site.register(ChapterLeadership, ChapterLeadershipAdmin)


# ============================================================================
# MEMBER PORTAL ADMIN
# ============================================================================

class MemberProfileAdmin(admin.ModelAdmin):
    list_display = ('member_number', 'get_full_name', 'status', 'initiation_date', 'dues_current', 'is_officer')
    list_filter = ('status', 'dues_current', 'initiation_date', 'is_officer')
    search_fields = ('user__first_name', 'user__last_name', 'member_number', 'line_name')
    list_editable = ('dues_current', 'is_officer')
    fieldsets = (
        ('User Account', {
            'fields': ('user',)
        }),
        ('Member Information', {
            'fields': ('member_number', 'status', 'initiation_date', 'line_name', 'line_number')
        }),
        ('Contact Information', {
            'fields': ('phone', 'address', 'emergency_contact_name', 'emergency_contact_phone')
        }),
        ('Profile', {
            'fields': ('profile_image', 'bio')
        }),
        ('Dues Status', {
            'fields': ('dues_current',)
        }),
        ('Admin Privileges', {
            'fields': ('is_officer',),
            'description': 'Check this to give this member admin/officer privileges for managing chapter operations including the boutique.'
        }),
    )

class DuesPaymentAdmin(admin.ModelAdmin):
    list_display = ('member', 'payment_type', 'amount', 'amount_paid', 'balance', 'due_date', 'status')
    list_filter = ('payment_type', 'status', 'due_date')
    search_fields = ('member__user__first_name', 'member__user__last_name', 'description')
    date_hierarchy = 'due_date'
    fieldsets = (
        ('Payment Information', {
            'fields': ('member', 'payment_type', 'amount', 'amount_paid', 'description')
        }),
        ('Dates', {
            'fields': ('due_date', 'payment_date')
        }),
        ('Status & Details', {
            'fields': ('status', 'payment_method', 'transaction_id', 'notes')
        }),
    )

class EventAttendanceAdmin(admin.ModelAdmin):
    list_display = ('event', 'member', 'status', 'points', 'rsvp_status', 'checked_in_at')
    list_filter = ('status', 'rsvp_status', 'event')
    search_fields = ('member__user__first_name', 'member__user__last_name', 'event__title')
    list_editable = ('status', 'points')

class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'priority', 'author', 'is_pinned', 'is_active', 'publish_date')
    list_filter = ('priority', 'is_pinned', 'is_active', 'publish_date')
    search_fields = ('title', 'content')
    list_editable = ('is_pinned', 'is_active')
    date_hierarchy = 'publish_date'


class AnnouncementViewAdmin(admin.ModelAdmin):
    list_display = ('user', 'announcement', 'viewed_at')
    list_filter = ('viewed_at',)
    search_fields = ('user__username', 'announcement__title')
    date_hierarchy = 'viewed_at'


class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'uploaded_by', 'is_public', 'requires_officer', 'created_at')
    list_filter = ('category', 'is_public', 'requires_officer')
    search_fields = ('title', 'description')
    list_editable = ('is_public', 'requires_officer')

class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'subject', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('sender__username', 'recipient__username', 'subject', 'content')
    date_hierarchy = 'created_at'

class ProfileCommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'profile', 'content_preview', 'created_at', 'is_edited')
    list_filter = ('is_edited', 'created_at')
    search_fields = ('author__username', 'profile__user__username', 'content')
    date_hierarchy = 'created_at'
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'

class CommentLikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'comment', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'comment__author__username')
    date_hierarchy = 'created_at'

class PhotoAlbumAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'is_public', 'photo_count', 'created_at')
    list_filter = ('is_public', 'created_at')
    search_fields = ('title', 'description', 'created_by__username')
    date_hierarchy = 'created_at'

class PhotoAdmin(admin.ModelAdmin):
    list_display = ('uploaded_by', 'album', 'caption_preview', 'like_count', 'comment_count', 'created_at')
    list_filter = ('album', 'created_at')
    search_fields = ('caption', 'tags', 'uploaded_by__username')
    date_hierarchy = 'created_at'
    
    def caption_preview(self, obj):
        return obj.caption[:50] + '...' if len(obj.caption) > 50 else obj.caption
    caption_preview.short_description = 'Caption'

class PhotoCommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'photo', 'content_preview', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('author__username', 'content')
    date_hierarchy = 'created_at'
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'

class PhotoLikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'photo', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username',)
    date_hierarchy = 'created_at'

class InvitationCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'email', 'first_name', 'last_name', 'member_number', 'is_used', 'used_by', 'created_at', 'expires_at')
    list_filter = ('is_used', 'created_at', 'expires_at')
    search_fields = ('code', 'email', 'first_name', 'last_name', 'member_number')
    readonly_fields = ('is_used', 'used_by', 'used_at')
    date_hierarchy = 'created_at'
    
    def save_model(self, request, obj, form, change):
        if not change:  # Only set created_by on new objects
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

admin.site.register(MemberProfile, MemberProfileAdmin)
admin.site.register(DuesPayment, DuesPaymentAdmin)
admin.site.register(EventAttendance, EventAttendanceAdmin)
admin.site.register(Announcement, AnnouncementAdmin)
admin.site.register(AnnouncementView, AnnouncementViewAdmin)
admin.site.register(Document, DocumentAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(ProfileComment, ProfileCommentAdmin)
admin.site.register(CommentLike, CommentLikeAdmin)
admin.site.register(PhotoAlbum, PhotoAlbumAdmin)
admin.site.register(Photo, PhotoAdmin)
admin.site.register(PhotoComment, PhotoCommentAdmin)
admin.site.register(PhotoLike, PhotoLikeAdmin)
admin.site.register(InvitationCode, InvitationCodeAdmin)


# ============================================================================
# BOUTIQUE ADMIN
# ============================================================================

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'inventory', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('name', 'description')
    list_editable = ('price', 'inventory')
    date_hierarchy = 'created_at'
    fieldsets = (
        ('Product Information', {
            'fields': ('name', 'description', 'category')
        }),
        ('Pricing & Inventory', {
            'fields': ('price', 'inventory')
        }),
        ('Variants', {
            'fields': ('sizes', 'colors')
        }),
        ('Media', {
            'fields': ('image',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    fields = ('product', 'quantity', 'size', 'color')

class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_total_items', 'get_total_price', 'updated_at')
    list_filter = ('updated_at',)
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [CartItemInline]

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ('product', 'quantity', 'size', 'color', 'price')
    readonly_fields = ('price',)

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total_price', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'email', 'stripe_payment_intent')
    readonly_fields = ('stripe_payment_intent', 'created_at', 'updated_at')
    fieldsets = (
        ('Order Information', {
            'fields': ('user', 'status', 'total_price')
        }),
        ('Shipping Details', {
            'fields': ('email', 'address', 'city', 'state', 'zip_code')
        }),
        ('Payment', {
            'fields': ('stripe_payment_intent',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    inlines = [OrderItemInline]

admin.site.register(Product, ProductAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem)
admin.site.register(Order, OrderAdmin)
