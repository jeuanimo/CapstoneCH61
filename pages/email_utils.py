"""
Email utility functions for sending notifications to members
"""

from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import logging

logger = logging.getLogger(__name__)

# Email constants
CHAPTER_NAME = 'Nu Gamma Sigma'
DEFAULT_CONTACT_EMAIL = 'nugammasigma@example.com'
CHAPTER_FULL_NAME = 'Phi Beta Sigma - Nu Gamma Sigma Chapter'


def send_dues_reminder_email(member_profile):
    """
    Send dues payment reminder to member when marked as non-financial
    
    Args:
        member_profile: MemberProfile instance
    """
    if not member_profile.user.email:
        logger.warning(f"No email on file for member {member_profile.user.username}")
        return False
    
    try:
        from django.utils import timezone
        
        subject = "Phi Beta Sigma - Dues Payment Required"
        
        days_remaining = member_profile.days_until_removal()
        deadline_date = member_profile.marked_for_removal_date + timezone.timedelta(days=90) if member_profile.marked_for_removal_date else None
        
        context = {
            'member_name': member_profile.user.get_full_name() or member_profile.user.username,
            'days_remaining': days_remaining,
            'deadline_date': deadline_date,
            'chapter_name': CHAPTER_NAME,
            'portal_url': settings.SITE_URL + '/portal/dues/' if hasattr(settings, 'SITE_URL') else 'https://nugammasigma.org/portal/dues/',
            'contact_email': getattr(settings, 'CONTACT_EMAIL', DEFAULT_CONTACT_EMAIL),
        }
        
        # Try to use template if it exists, otherwise use plain text
        try:
            html_message = render_to_string('pages/emails/dues_reminder.html', context)
            plain_message = strip_tags(html_message)
        except Exception:
            plain_message = f"""
Hello {context['member_name']},

You have been marked as non-financial and must pay your national and local dues within {days_remaining} days to maintain access to the member portal.

If you have already paid your dues, please contact an officer to update your status.

To pay your dues, visit the member portal at:
{context['portal_url']}

Questions? Contact your chapter officers at:
{context['contact_email']}

---
{CHAPTER_FULL_NAME}
"""
            html_message = None
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[member_profile.user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Dues reminder email sent to {member_profile.user.email} ({member_profile.user.username})")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send dues reminder to {member_profile.user.email}: {str(e)}")
        return False


def send_announcement_email(title, content, recipient_emails):
    """
    Send announcement email to members
    
    Args:
        title: Announcement title
        content: Announcement content
        recipient_emails: List of email addresses
    """
    if not recipient_emails:
        logger.warning("No recipient emails provided for announcement")
        return False
    
    try:
        from django.utils import timezone
        
        subject = f"Phi Beta Sigma - {title}"
        
        context = {
            'title': title,
            'content_html': content,
            'announcement_date': timezone.now().strftime("%B %d, %Y"),
            'chapter_name': CHAPTER_NAME,
            'portal_url': getattr(settings, 'SITE_URL', 'https://nugammasigma.org') + '/portal/',
            'contact_email': getattr(settings, 'CONTACT_EMAIL', DEFAULT_CONTACT_EMAIL),
            'include_portal_link': True,
        }
        
        # Try to use template if it exists, otherwise use plain text
        try:
            html_message = render_to_string('pages/emails/announcement.html', context)
            plain_message = strip_tags(html_message)
        except Exception:
            plain_message = f"""
{title}

{content}

Visit the chapter portal for more information:
{context['portal_url']}

---
{CHAPTER_FULL_NAME}
"""
            html_message = None
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_emails,
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Announcement email sent to {len(recipient_emails)} members")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send announcement email: {str(e)}")
        return False


def send_payment_confirmation_email(member_profile, payment_amount, payment_date, transaction_id=None):
    """
    Send dues payment confirmation email
    
    Args:
        member_profile: MemberProfile instance
        payment_amount: Amount paid
        payment_date: Date of payment
        transaction_id: Optional transaction ID for reference
    """
    if not member_profile.user.email:
        logger.warning(f"No email on file for member {member_profile.user.username}")
        return False
    
    try:
        from django.utils import timezone
        
        subject = "Phi Beta Sigma - Payment Received"
        
        if isinstance(payment_date, str):
            from datetime import datetime
            try:
                payment_date = datetime.strptime(payment_date, "%Y-%m-%d").date()
            except (ValueError, TypeError):
                pass
        
        context = {
            'member_name': member_profile.user.get_full_name() or member_profile.user.username,
            'payment_amount': payment_amount,
            'payment_date': payment_date,
            'transaction_id': transaction_id,
            'chapter_name': CHAPTER_NAME,
            'portal_url': getattr(settings, 'SITE_URL', 'https://nugammasigma.org') + '/portal/profile/',
            'contact_email': getattr(settings, 'CONTACT_EMAIL', DEFAULT_CONTACT_EMAIL),
        }
        
        # Try to use template if it exists, otherwise use plain text
        try:
            html_message = render_to_string('pages/emails/payment_confirmation.html', context)
            plain_message = strip_tags(html_message)
        except Exception:
            plain_message = f"""
Hello {context['member_name']},

Thank you for your payment!

Payment Details:
Amount: ${context['payment_amount']}
Date: {context['payment_date']}
{"Transaction ID: " + context['transaction_id'] if context['transaction_id'] else ""}

Your dues status has been updated and document access has been restored. If you have questions, contact an officer.

Visit your profile: {context['portal_url']}

---
{CHAPTER_FULL_NAME}
"""
            html_message = None
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[member_profile.user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Payment confirmation email sent to {member_profile.user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send payment confirmation to {member_profile.user.email}: {str(e)}")
        return False


def send_bulk_email_to_members(member_profiles, subject, message, bcc=True):
    """
    Send bulk email to multiple members
    
    Args:
        member_profiles: List of MemberProfile instances or QuerySet
        subject: Email subject
        message: Email message body (plain text or HTML)
        bcc: If True, use BCC (members won't see other recipients)
    
    Returns:
        Number of emails sent successfully
    """
    recipient_emails = [
        m.user.email for m in member_profiles 
        if m.user.email
    ]
    
    if not recipient_emails:
        logger.warning("No valid email addresses found for bulk email")
        return 0
    
    try:
        if bcc:
            # Send one email with all recipients in BCC
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.DEFAULT_FROM_EMAIL],  # Send to self
                bcc=recipient_emails,
                fail_silently=False,
            )
        else:
            # Send individual emails
            for email in recipient_emails:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False,
                )
        
        logger.info(f"Bulk email sent to {len(recipient_emails)} members (subject: {subject})")
        return len(recipient_emails)
        
    except Exception as e:
        logger.error(f"Failed to send bulk email: {str(e)}")
        return 0
