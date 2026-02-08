# Email Notification System - Testing Guide

## System Overview

The email notification system includes:
- **Dues Reminder Emails**: Auto-sent when members marked non-financial
- **Officer Announcement Emails**: Sent via `/portal/email/send-members/`
- **Payment Confirmation Emails**: Framework for payment receipt confirmations

## Email Templates Created

### 1. `dues_reminder.html`
- Displays member name and countdown (days remaining)
- Includes portal link for dues payment
- Shows deadline date
- Professional styling with chapter branding

### 2. `announcement.html`
- Displays announcement title and content
- Portal link included
- Flexible for event announcements
- Support for RSVP links (future)

### 3. `payment_confirmation.html`
- Payment details and amount
- Transaction ID (optional)
- Membership status restoration message
- Next steps for member

## Testing in Development

### Step 1: Verify Email Backend is Console

Check `config/settings.py`:
```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

This prints emails to terminal instead of sending.

### Step 2: Test Manual Member Marking

1. Go to member profile edit page
2. Check "Mark Member as Non-Financial with 90-Day Countdown"
3. Save
4. Watch terminal for email output
5. Email should display:
   - Subject: "Phi Beta Sigma - Dues Payment Required"
   - Member name
   - Days remaining (countdown)
   - Portal link

**Expected Console Output:**
```
Content-Type: text/plain; charset="utf-8"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit
Subject: Phi Beta Sigma - Dues Payment Required
From: noreply@nugammasigma.org
To: member@example.com
Date: [timestamp]
Message-ID: [id]

[HTML and plain text content]
```

### Step 3: Test HQ CSV Sync

1. Go to admin panel → Sync Members with HQ
2. Upload HQ CSV with members
3. Members NOT on list should be marked non-financial
4. Terminal should show email for each marked member
5. Verify email count in success message

### Step 4: Test Bulk Announcement

1. Go to `/portal/email/send-members/`
2. Fill form:
   - Recipient Group: "All Members"
   - Subject: "Test Announcement"
   - Message: "This is a test"
   - send_immediately: UNCHECKED
3. Click "Preview Email"
4. Verify:
   - Recipient count shows
   - Sample emails shown (first 10)
   - Can see back button
5. Fill form again and check "send_immediately": CHECKED
6. Submit
7. Watch terminal for email(s)

## HTML Template Testing

The system includes graceful fallback to plain text. To verify HTML:

### Method 1: Check Console Output
The console backend prints full MIME structure including HTML.

### Method 2: Use EmailLog Model (Future)
When email audit log is implemented, you can view sent emails with preview.

## Development Email Backend Setup

### Console Backend (Current - Development)
```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```
- Prints to terminal/console
- Perfect for development
- No actual emails sent

### File Backend (Alternative - Development)
```python
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = '/tmp/app-messages'
```
- Saves emails to files
- Check `/tmp/app-messages/` directory
- Each email saved as separate file

### SMTP Backend (Production)
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
```

## Troubleshooting

### Email Not Appearing in Console

1. Check `EMAIL_BACKEND` in settings.py
2. Verify `DEBUG = True` in development
3. Check logs for errors:
   ```bash
   tail -f logs/django.log
   ```
4. Verify member has email address in profile

### Templates Not Found

If you see plain text instead of HTML:
- Verify template files exist:
  - `templates/pages/emails/dues_reminder.html`
  - `templates/pages/emails/announcement.html`
  - `templates/pages/emails/payment_confirmation.html`
- Check template path in email functions
- Verify Django template loader configuration

### Member Email Appears Blank

- Check MemberProfile.user.email is set
- Verify User model has email field
- Check for special characters in email

## Next Steps for Production

### 1. Configure SMTP
Set environment variables:
```bash
export EMAIL_HOST_USER="your-email@gmail.com"
export EMAIL_HOST_PASSWORD="app-specific-password"
export CONTACT_EMAIL="officers@nugammasigma.org"
export SITE_URL="https://nugammasigma.org"
```

### 2. Create Email Audit Log
Optional: Track all sent emails for compliance/testing
```python
class EmailLog(models.Model):
    recipient = models.EmailField()
    subject = models.CharField(max_length=255)
    message_type = models.CharField(choices=[
        ('dues_reminder', 'Dues Reminder'),
        ('announcement', 'Announcement'),
        ('payment_confirmation', 'Payment Confirmation'),
    ])
    sent_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(choices=[
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ])
    error_message = models.TextField(blank=True)
```

### 3. Set Up Email Scheduling (Django Celery + RabbitMQ)
Optional: Send emails asynchronously to prevent delays

### 4. Add Unsubscribe Links
Optional: Allow members to opt-out of announcements

## Email Function Reference

### send_dues_reminder_email(member_profile)
Sends dues payment reminder
- Called automatically when member marked non-financial
- Includes countdown in days
- HTML template with styling

### send_announcement_email(title, content, recipient_emails)
Sends bulk announcement
- Takes title and HTML content
- List of recipient emails
- Officer-initiated

### send_payment_confirmation_email(member_profile, payment_amount, payment_date, transaction_id=None)
Sends payment receipt
- Called after dues payment processed
- Includes amount, date, optional transaction ID
- Framework ready for integration

### send_bulk_email_to_members(member_profiles, subject, message, bcc=True)
Core bulk email sender
- Filters by member status
- BCC option for privacy
- Returns count of emails sent

## Template Context Variables

### Dues Reminder Email
- `member_name`: Full name or username
- `days_remaining`: Days until removal (integer)
- `deadline_date`: Deadline date
- `portal_url`: Link to dues payment page
- `contact_email`: Officer contact email

### Announcement Email
- `title`: Announcement title
- `content_html`: HTML content
- `announcement_date`: Date sent
- `portal_url`: Link to chapter portal
- `contact_email`: Officer contact email

### Payment Confirmation Email
- `member_name`: Full name or username
- `payment_amount`: Amount paid (float)
- `payment_date`: Date of payment
- `transaction_id`: Optional transaction reference
- `portal_url`: Link to member profile
- `contact_email`: Officer contact email

## Support & Questions

For implementation details, see:
- `pages/email_utils.py` - Email utility functions
- `templates/pages/emails/` - Email templates
- `templates/pages/portal/send_member_email.html` - Announcement form UI
