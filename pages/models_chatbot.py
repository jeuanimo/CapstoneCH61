"""
PUBLIC INFORMATION CHATBOT MODELS
Secure, modular models for public Q&A knowledge base.
"""

from django.db import models
from django.core.validators import MinLengthValidator, MaxLengthValidator
import logging

logger = logging.getLogger(__name__)


class PublicAnswer(models.Model):
    """
    Stores approved public Q&A entries for the chatbot.
    
    Security Considerations:
    - Only PUBLIC information should be stored here
    - No sensitive member data, passwords, or private details
    - Content is searchable via keyword scoring
    - Created/updated timestamps for audit trail
    """
    
    CATEGORY_CHOICES = [
        ('about', 'About the Fraternity'),
        ('history', 'History & Traditions'),
        ('membership', 'Membership'),
        ('events', 'Events & Programs'),
        ('contact', 'Contact Information'),
        ('values', 'Values & Mission'),
        ('faq', 'Frequently Asked Questions'),
        ('other', 'Other'),
    ]
    
    # Question/keyword variations (comma-separated)
    question = models.CharField(
        max_length=500,
        validators=[MinLengthValidator(5)],
        help_text="Primary question or keyword (5-500 chars)"
    )
    
    # Keywords for matching (comma-separated, lowercase)
    keywords = models.TextField(
        help_text="Comma-separated keywords for searching (e.g., 'phi beta sigma, fraternity, brotherhood')"
    )
    
    # Answer text (public only)
    answer = models.TextField(
        validators=[MinLengthValidator(10)],
        help_text="Public answer text. NEVER include private/member data."
    )
    
    # Category for organization
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='faq'
    )
    
    # Is this answer active/visible to chatbot?
    is_active = models.BooleanField(
        default=True,
        help_text="Inactive answers won't be shown by chatbot"
    )
    
    # Confidence threshold (0-100) - higher = more specific
    confidence_threshold = models.IntegerField(
        default=30,
        help_text="Minimum confidence score (0-100) to display this answer"
    )
    
    # Admin only: Internal note
    internal_note = models.TextField(
        blank=True,
        help_text="Internal notes (not visible to public)"
    )
    
    # Audit trail
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(
        max_length=100,
        default='system',
        help_text="Admin user who created this entry"
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Public Answer'
        verbose_name_plural = 'Public Answers'
        indexes = [
            models.Index(fields=['is_active', '-created_at']),
            models.Index(fields=['category', 'is_active']),
        ]
    
    def __str__(self):
        return f"[{self.category}] {self.question[:50]}"
    
    def get_keywords_list(self):
        """Return keywords as a cleaned list."""
        return [kw.strip().lower() for kw in self.keywords.split(',') if kw.strip()]
    
    def save(self, *args, **kwargs):
        """Validate before saving."""
        # Ensure keywords are lowercase for consistency
        self.keywords = ','.join([kw.strip().lower() for kw in self.keywords.split(',') if kw.strip()])
        
        # Log sensitive operations
        if not self.pk:  # New entry
            logger.info(f"New public chatbot answer created: {self.question[:50]} (by {self.created_by})")
        
        super().save(*args, **kwargs)
