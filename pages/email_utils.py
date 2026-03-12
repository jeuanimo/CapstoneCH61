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


def send_invitation_email(invitation):
    """
    Send invitation email to a new member with their signup code.
    
    Args:
        invitation: InvitationCode instance
        
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    if not invitation.email:
        logger.warning(f"No email for invitation {invitation.code}")
        return False
    
    try:
        subject = "Nu Gamma Sigma Chapter - Your Invitation to Join"
        
        signup_url = "https://ngs1914.org/signup"
        
        name = invitation.first_name or "Brother"
        
        message = f"""
{name},

You have been invited to join the Nu Gamma Sigma Chapter member portal.

Your Invitation Code: {invitation.code}

To create your account:
1. Visit: {signup_url}
2. Enter your invitation code: {invitation.code}
3. Enter your email: {invitation.email}
4. Create a username and password

This code expires on {invitation.expires_at.strftime('%B %d, %Y')}.

If you have any questions, please contact us at {getattr(settings, 'CONTACT_EMAIL', 'contact@ngs1914.org')}.

Blue Phi,
Nu Gamma Sigma Chapter
Phi Beta Sigma Fraternity, Inc.
"""
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[invitation.email],
            fail_silently=False,
        )
        
        logger.info(f"Invitation email sent to {invitation.email} (code: {invitation.code})")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send invitation email to {invitation.email}: {str(e)}")
        return False


def send_message_email_notification(message_obj, from_email=None):
    """
    Send an email notification for an internal Message.
    Uses the recipient's email if they have one on file.
    
    Args:
        message_obj: Message model instance
        from_email: Optional custom sender email (defaults to CONTACT_EMAIL)
    
    Returns:
        True if email was sent successfully, False otherwise
    """
    # Check if recipient has an email on file
    if not message_obj.recipient.email:
        logger.info(f"No email on file for {message_obj.recipient.username}, skipping email notification")
        return False
    
    try:
        # Use CONTACT_EMAIL as the sender (contact@ngs1914.org)
        sender_email = from_email or getattr(settings, 'CONTACT_EMAIL', 'contact@ngs1914.org')
        
        # Format the subject with chapter prefix
        subject = f"[Nu Gamma Sigma] {message_obj.subject or 'New Message'}"
        
        # Get priority label for urgent messages
        priority_label = ""
        if message_obj.priority in ['HI', 'UR']:
            priority_label = "[IMPORTANT] "
            subject = priority_label + subject
        
        # Get recipient's display name
        recipient_name = message_obj.recipient.get_full_name() or message_obj.recipient.username
        sender_name = message_obj.sender.get_full_name() or message_obj.sender.username
        
        # Build the email body
        portal_url = getattr(settings, 'SITE_URL', 'https://ngs1914.org') + '/portal/messages/'
        
        plain_message = f"""Hello {recipient_name},

You have a new message in the Nu Gamma Sigma Member Portal.

From: {sender_name}
Subject: {message_obj.subject or 'No Subject'}
Category: {message_obj.get_category_display()}

---
{message_obj.content}
---

To view and reply to this message, visit the Member Portal:
{portal_url}

---
Nu Gamma Sigma Chapter
Phi Beta Sigma Fraternity, Inc.

This is an automated notification. Please log in to the portal to reply.
"""
        
        # Try to use HTML template if available
        html_message = None
        try:
            context = {
                'recipient_name': recipient_name,
                'sender_name': sender_name,
                'subject': message_obj.subject,
                'content': message_obj.content,
                'category': message_obj.get_category_display(),
                'priority': message_obj.get_priority_display(),
                'is_urgent': message_obj.priority in ['HI', 'UR'],
                'portal_url': portal_url,
                'chapter_name': CHAPTER_NAME,
            }
            html_message = render_to_string('pages/emails/message_notification.html', context)
        except Exception:
            # Fall back to plain text if template doesn't exist
            pass
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=sender_email,
            recipient_list=[message_obj.recipient.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Email notification sent to {message_obj.recipient.email} for message '{message_obj.subject}'")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email notification to {message_obj.recipient.email}: {str(e)}")
        return False


def send_bulk_message_email_notifications(messages_list, from_email=None):
    """
    Send email notifications for multiple internal Messages.
    
    Args:
        messages_list: List of Message model instances
        from_email: Optional custom sender email (defaults to CONTACT_EMAIL)
    
    Returns:
        Dictionary with 'sent' and 'failed' counts
    """
    sent_count = 0
    failed_count = 0
    no_email_count = 0
    
    for message_obj in messages_list:
        if not message_obj.recipient.email:
            no_email_count += 1
            continue
            
        if send_message_email_notification(message_obj, from_email):
            sent_count += 1
        else:
            failed_count += 1
    
    logger.info(f"Bulk email notifications: {sent_count} sent, {failed_count} failed, {no_email_count} no email on file")
    return {
        'sent': sent_count,
        'failed': failed_count,
        'no_email': no_email_count
    }


def send_poll_email_notification(poll, recipient_user, from_email=None):
    """
    Send an email notification about a new poll that requires a vote.
    
    Args:
        poll: Poll model instance
        recipient_user: User model instance (the recipient)
        from_email: Optional custom sender email (defaults to CONTACT_EMAIL)
    
    Returns:
        True if email was sent successfully, False otherwise
    """
    # Check if recipient has an email on file
    if not recipient_user.email:
        logger.info(f"No email on file for {recipient_user.username}, skipping poll email notification")
        return False
    
    try:
        # Use CONTACT_EMAIL as the sender (contact@ngs1914.org)
        sender_email = from_email or getattr(settings, 'CONTACT_EMAIL', 'contact@ngs1914.org')
        
        # Subject with "You Have a Vote to Make" header
        subject = f"[Nu Gamma Sigma] You Have a Vote to Make: {poll.title}"
        
        # Get recipient's display name
        recipient_name = recipient_user.get_full_name() or recipient_user.username
        
        # Get poll details
        poll_type_display = poll.get_poll_type_display()
        deadline_text = ""
        if poll.ends_at:
            deadline_text = f"⏰ Voting Deadline: {poll.ends_at.strftime('%B %d, %Y at %I:%M %p')}"
        else:
            deadline_text = "⏰ No deadline - vote at your convenience"
        
        # Build the portal URL for polls
        portal_url = getattr(settings, 'SITE_URL', 'https://ngs1914.org') + f'/portal/polls/{poll.pk}/'
        
        plain_message = f"""Hello {recipient_name},

═══════════════════════════════════════
   🗳️  YOU HAVE A VOTE TO MAKE  🗳️
═══════════════════════════════════════

A new {poll_type_display.lower()} has been created and YOUR VOTE is needed!

Poll: {poll.title}
Type: {poll_type_display}

{poll.description if poll.description else ''}

{deadline_text}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Cast your vote now:
{portal_url}

Or visit the Member Portal and go to Polls.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Blue Phi,
Nu Gamma Sigma Chapter
Phi Beta Sigma Fraternity, Inc.

This is an automated notification. Please log in to the portal to vote.
"""
        
        # Try to use HTML template if available
        html_message = None
        try:
            context = {
                'recipient_name': recipient_name,
                'poll_title': poll.title,
                'poll_type': poll_type_display,
                'poll_description': poll.description,
                'deadline_text': deadline_text,
                'has_deadline': poll.ends_at is not None,
                'deadline_date': poll.ends_at,
                'portal_url': portal_url,
                'chapter_name': CHAPTER_NAME,
            }
            html_message = render_to_string('pages/emails/poll_notification.html', context)
        except Exception:
            # Fall back to plain text if template doesn't exist
            pass
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=sender_email,
            recipient_list=[recipient_user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Poll email notification sent to {recipient_user.email} for poll '{poll.title}'")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send poll email notification to {recipient_user.email}: {str(e)}")
        return False


def send_profile_comment_email_notification(comment, profile_owner, commenter, from_email=None):
    """
    Send an email notification when someone comments on a user's profile.
    
    Args:
        comment: ProfileComment model instance
        profile_owner: User model instance (owner of the profile)
        commenter: User model instance (person who made the comment)
        from_email: Optional custom sender email (defaults to CONTACT_EMAIL)
    
    Returns:
        True if email was sent successfully, False otherwise
    """
    # Check if profile owner has an email on file
    if not profile_owner.email:
        logger.info(f"No email on file for {profile_owner.username}, skipping profile comment email notification")
        return False
    
    try:
        # Use CONTACT_EMAIL as the sender
        sender_email = from_email or getattr(settings, 'CONTACT_EMAIL', 'contact@ngs1914.org')
        
        # Get display names
        owner_name = profile_owner.get_full_name() or profile_owner.username
        commenter_name = commenter.get_full_name() or commenter.username
        
        subject = f"[Nu Gamma Sigma] {commenter_name} commented on your profile"
        
        # Build the profile URL
        portal_url = getattr(settings, 'SITE_URL', 'https://ngs1914.org') + f'/portal/members/{profile_owner.username}/'
        
        # Truncate comment for preview
        comment_preview = comment.content[:300] + '...' if len(comment.content) > 300 else comment.content
        
        plain_message = f"""Hello {owner_name},

💬 NEW COMMENT ON YOUR PROFILE

{commenter_name} left a comment on your profile:

"{comment_preview}"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

View and reply to this comment:
{portal_url}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Blue Phi,
Nu Gamma Sigma Chapter
Phi Beta Sigma Fraternity, Inc.

This is an automated notification. Please log in to the portal to reply.
"""
        
        # Try to use HTML template if available
        html_message = None
        try:
            context = {
                'owner_name': owner_name,
                'commenter_name': commenter_name,
                'comment_content': comment.content,
                'comment_preview': comment_preview,
                'portal_url': portal_url,
                'chapter_name': CHAPTER_NAME,
            }
            html_message = render_to_string('pages/emails/profile_comment_notification.html', context)
        except Exception:
            # Fall back to plain text if template doesn't exist
            pass
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=sender_email,
            recipient_list=[profile_owner.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Profile comment email notification sent to {profile_owner.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send profile comment email notification to {profile_owner.email}: {str(e)}")
        return False