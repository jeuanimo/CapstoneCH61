"""
PUBLIC INFORMATION CHATBOT ADMIN
Secure admin interface for managing public Q&A entries.
"""

from django.contrib import admin
from django.utils.html import format_html
from pages.models_chatbot import PublicAnswer


@admin.register(PublicAnswer)
class PublicAnswerAdmin(admin.ModelAdmin):
    """Admin interface for managing public answers/Q&A for chatbot."""
    
    list_display = [
        'question',
        'category',
        'active_status',
        'confidence_threshold',
        'created_at',
        'keyword_preview'
    ]
    
    list_filter = [
        'is_active',
        'category',
        'confidence_threshold',
        'created_at',
    ]
    
    search_fields = [
        'question',
        'keywords',
        'answer',
    ]
    
    fieldsets = (
        ('Question & Keywords', {
            'fields': (
                'question',
                'keywords',
                'category',
            ),
            'description': 'Define the question and search keywords for this Q&A entry.'
        }),
        ('Answer (Public Only)', {
            'fields': (
                'answer',
            ),
            'description': '<strong style="color: red;">IMPORTANT:</strong> Only enter public information. Never include member-only data, passwords, or sensitive details.'
        }),
        ('Chatbot Settings', {
            'fields': (
                'is_active',
                'confidence_threshold',
            ),
            'description': 'Confidence threshold: higher values (60+) = more specific matching. Lower values (20-40) = broader matching.'
        }),
        ('Admin Notes (Internal Only)', {
            'fields': (
                'internal_note',
            ),
            'classes': ('collapse',),
            'description': 'Internal notes for admins. Not visible to public.'
        }),
        ('Audit Information', {
            'fields': (
                'created_by',
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = [
        'created_at',
        'updated_at',
    ]
    
    def active_status(self, obj):
        """Display active/inactive status with color."""
        if obj.is_active:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Active</span>'
            )
        return format_html(
            '<span style="color: red; font-weight: bold;">✗ Inactive</span>'
        )
    active_status.short_description = 'Status'
    
    def keyword_preview(self, obj):
        """Show preview of keywords."""
        keywords = obj.get_keywords_list()[:3]
        preview = ', '.join(keywords)
        if len(obj.get_keywords_list()) > 3:
            preview += f', +{len(obj.get_keywords_list()) - 3} more'
        return preview
    keyword_preview.short_description = 'Keywords'
    
    def save_model(self, request, obj, form, change):
        """Set created_by to current user on creation."""
        if not change:  # New object
            obj.created_by = request.user.username
        super().save_model(request, obj, form, change)
    
    actions = ['activate_answers', 'deactivate_answers']
    
    def activate_answers(self, request, queryset):
        """Bulk action to activate answers."""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} answer(s) activated.')
    activate_answers.short_description = 'Activate selected answers'
    
    def deactivate_answers(self, request, queryset):
        """Bulk action to deactivate answers."""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} answer(s) deactivated.')
    deactivate_answers.short_description = 'Deactivate selected answers'
