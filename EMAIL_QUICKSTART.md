# Email System - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Verify Configuration (1 min)

Check your email backend in `config/settings.py`:

```python
# Should see one of these:
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # ✅ Development
# OR
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'  # Production
```

For development, **console backend** prints emails to your terminal - perfect for testing.

### Step 2: Start Django Server

```bash
python manage.py runserver
```

Keep this terminal window visible to see email output.

### Step 3: Create a Test Member (if needed)

1. Go to `/admin/pages/memberprofile/`
2. Create a member with:
   - Username: `testuser`
   - Email: `test@example.com`  (this is where emails are "sent")
   - Status: `financial`

### Step 4: Test Manual Member Marking

📧 **Test 1: Email on Manual Marking**

1. Go to member profile: `/portal/member/testuser/edit/`
2. Scroll down to "Officer Actions" section
3. Check: ☑️ "Mark Member as Non-Financial with 90-Day Countdown"
4. Click **Save**

**Expected Result**:
- Terminal shows email output with:
  - Subject: "Phi Beta Sigma - Dues Payment Required"
  - To: test@example.com
  - Days remaining countdown
  - Portal link

💡 **Terminal Output Example**:
```
Content-Type: text/plain; charset="utf-8"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit
Subject: Phi Beta Sigma - Dues Payment Required
From: noreply@nugammasigma.org
To: test@example.com

[HTML email content...]

Days Remaining: 90
[Portal link and officer contact info]
```

### Step 5: Test Officer Announcement

📧 **Test 2: Bulk Email to Members**

1. Go to: `/portal/email/send-members/`
2. Fill the form:
   ```
   Recipient Group: All Members
   Subject: Test Announcement
   Message: This is a test email from the chapter.
   Send Immediately: UNCHECKED
   ```
3. Click **Preview Email**

**Expected Result**:
- Shows: "Email will be sent to X member(s)"
- Sample email addresses displayed
- Back button to edit

4. Check **Send Immediately** and re-submit

**Expected Result**:
- Terminal shows email output
- Success message: "Email sent to X members"

### Step 6: Verify Dark Mode

If your chapter uses dark mode:

1. Toggle dark mode in footer
2. Visit: `/portal/email/send-members/`
3. Verify styling looks good

## 🧪 Testing Scenarios

### Scenario A: HQ Member Sync

1. Go to: `/admin/pages/memberprofile/sync/`
2. Upload sample HQ CSV
3. Check: **Members** appearing in "Marked for Removal" section
4. Verify: Email count matches marked members

### Scenario B: Multiple Recipients

1. Create 3-5 test members with emails
2. Go to: `/portal/email/send-members/`
3. Select "All Members"
4. Fill form and preview
5. Verify: Shows correct count and sample emails

### Scenario C: Filtered Recipients

1. Create mix of financial/non-financial members
2. Go to: `/portal/email/send-members/`
3. Test each recipient group filter:
   - "All Members" (all)
   - "Financial Members Only" (status='financial')
   - "Non-Financial Members" (status='non_financial')
   - "Officers Only" (is_staff=True)

## 📊 What to Look For

### Email Output
- ✅ Subject line correct
- ✅ To: address correct
- ✅ From: noreply@nugammasigma.org
- ✅ Content formatted properly
- ✅ Links working

### UI Form
- ✅ Form displays without errors
- ✅ All fields render
- ✅ Preview mode works
- ✅ Send mode works
- ✅ Dark mode styling correct

### Member Dashboard
- ✅ Non-financial members see warning banner
- ✅ Banner shows countdown timer
- ✅ Dashboard still accessible

### Documents Page
- ✅ Non-financial members redirected
- ✅ Error message explains dues requirement
- ✅ Financial members can access docs

## 🔧 Troubleshooting

### Email not appearing in terminal?

**Check these**:
1. EMAIL_BACKEND in settings.py is console backend
2. Django server terminal is visible
3. Scroll up in terminal (might be buffered)
4. Check Django logs for errors

### Form shows errors?

**Likely causes**:
1. Missing template file
   - Check: `templates/pages/portal/send_member_email.html` exists
2. Form not imported
   - Check: `pages/views.py` imports BulkEmailForm
3. URL route missing
   - Check: URL added to `pages/urls.py`

### Email template not rendering?

**Fallback works**:
- If HTML template missing, system uses plain text
- Plain text version still sends
- Check logs for template not found warning

### Members not showing in preview?

**Verify**:
1. Members exist in database
2. Members have email addresses
3. Member status matches filter
4. No errors in terminal

## 📋 Success Criteria

You'll know it's working when:

✅ Manual member marking sends email
✅ Email includes countdown (days remaining)
✅ Portal link in email
✅ Officer can send bulk announcements
✅ Preview shows recipient count
✅ Emails appear in console
✅ Dark mode renders correctly
✅ Mobile layout looks good

## 📚 Documentation

For more details:
- **Testing Guide**: `EMAIL_TESTING_GUIDE.md`
- **Complete System Docs**: `EMAIL_SYSTEM_COMPLETE.md`
- **Integration Checklist**: `EMAIL_INTEGRATION_CHECKLIST.md`

## 🎯 Next Steps After Testing

Once everything works:

1. **Configure Production Email**:
   ```bash
   export EMAIL_HOST_USER="your-email@gmail.com"
   export EMAIL_HOST_PASSWORD="app-password"
   ```

2. **Test with Real SMTP**:
   - Change `EMAIL_BACKEND` to `smtp.EmailBackend`
   - Try sending to real email account

3. **Monitor Logs**:
   - Check email sending logs
   - Verify member receives emails

4. **Add to Your Workflow**:
   - Use when syncing HQ member lists
   - Send announcements regularly
   - Monitor dues compliance

## 💡 Pro Tips

- **Preview Everything**: Always preview announcements before sending
- **Test Small**: Start with manual member marking before bulk emails
- **Check Logs**: Always check Django logs if something seems off
- **Document Sends**: Log who sent what and when (coming soon with audit log)
- **Test Dark Mode**: Make sure emails look good in all themes

## 🆘 Still Having Issues?

1. **Check Terminal**: Scroll up for email output
2. **Check Logs**: Look for Django error messages
3. **Verify Settings**: Ensure EMAIL_BACKEND configured
4. **Check Files**: Verify all email template files exist
5. **Reset Server**: Restart Django development server

## Quick Command Reference

```bash
# Start server (watch for email output)
python manage.py runserver

# Create test member
python manage.py shell
>>> from django.contrib.auth.models import User
>>> from pages.models import MemberProfile
>>> u = User.objects.create_user('test', 'test@example.com', 'password')
>>> m = MemberProfile.objects.create(user=u, status='financial')

# Check member
python manage.py shell
>>> from pages.models import MemberProfile
>>> m = MemberProfile.objects.get(user__username='test')
>>> m.user.email
'test@example.com'
```

## 📞 Support

If you encounter issues:
1. Check terminal for error messages
2. Review testing documentation
3. Verify file locations
4. Check settings configuration
5. Review logs for details

**You're all set! Start testing now.** 🚀

When ready to move to production, update EMAIL_BACKEND and configure SMTP credentials.
