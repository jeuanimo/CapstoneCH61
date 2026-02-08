# 90-Day Member Removal Grace Period System

## Overview

This system allows administrators to mark members for removal who are not found in the International HQ member list, while giving those members a **90-day grace period** to resolve their status by either:
- Updating their status with International HQ
- Paying outstanding national and local dues

Members are notified on the portal dashboard about the countdown and encouraged to pay their dues.

---

## Features

### 1. **Admin Sync Interface**
- URL: `/portal/sync-members/`
- Access: Staff only
- Allows uploading of current HQ member list CSV
- Provides preview of changes before execution
- Marks members for removal instead of immediately deleting them

### 2. **90-Day Grace Period**
- Members marked for removal have exactly 90 days to resolve
- Dashboard shows countdown timer with days remaining
- Color-coded warning banner (red) for urgent visibility
- Clear call-to-action to pay dues

### 3. **Member Notifications**
- **Dashboard Banner**: Shows countdown if member is marked for removal
- **Dues Reminder**: Shows yellow warning if dues are unpaid
- Both appear on:
  - Member Portal Dashboard
  - Member Roster
  - Dues Payment page

### 4. **Admin Monitoring View**
- URL: `/portal/marked-members/`
- Access: Staff only
- Shows all members in grace period
- Categorizes by urgency (30+ days vs. <30 days)
- Easy identification of at-risk members

### 5. **Automatic Removal**
- Management command: `python manage.py remove_expired_members`
- Runs after 90 days automatically
- Can be scheduled with cron jobs or task scheduler
- Supports dry-run mode: `--dry-run` flag

---

## How It Works

### Step 1: Sync Members from HQ

1. Go to `/portal/sync-members/`
2. Export current member list from International HQ
3. Upload CSV file (must have `Member#` or `Member Number` column)
4. Click "Preview Changes" to see impact
5. Click "Execute Sync" to mark non-matching members

### Step 2: Members See Warning

- Member logs into portal
- Dashboard shows red warning banner with countdown
- Includes link to pay dues
- Warning also appears on:
  - Member Roster page
  - Dues Payment page

### Step 3: Members Can Resolve

#### Option A: Pay Dues
- Click "Pay Dues Now" button in banner
- Go to `/portal/dues-and-payments/`
- Pay outstanding national and local dues
- Once dues marked as current, member is no longer at risk

#### Option B: Update HQ
- Contact International HQ to update member status
- Request manual restoration by administrator

### Step 4: Auto-Removal After 90 Days

Run the management command:
```bash
python manage.py remove_expired_members
```

This will:
- Find all members past the 90-day deadline
- Permanently remove their accounts
- Log all removed members

To preview without making changes:
```bash
python manage.py remove_expired_members --dry-run
```

---

## Database Changes

### New Fields on MemberProfile

```python
marked_for_removal_date = DateTimeField()  # When marked for removal
removal_reason = CharField()                # Why they were marked (e.g., "Not in HQ list")
```

### New Methods on MemberProfile

```python
member.is_marked_for_removal()    # Returns True if marked
member.days_until_removal()        # Returns days remaining (0-90)
member.should_be_removed()         # Returns True if 90 days passed
```

---

## Admin Commands

### View Marked Members (Web)
```
/portal/marked-members/
```

### Remove Expired Members (Terminal)
```bash
# Preview changes
python manage.py remove_expired_members --dry-run

# Execute removal
python manage.py remove_expired_members
```

### Reset a Member (Manual)

1. Go to Django Admin: `/admin/pages/memberprofile/`
2. Find the member
3. Clear the `marked_for_removal_date` field
4. Save
5. Member will no longer be marked

---

## Member Experience

### Dashboard Alert (Red Warning)
```
⏰ Account Removal Notice
Your account will be removed in 45 days.

Reason: Not in HQ member list

💰 To restore access, please: Pay your national and local dues
```

### Dues Payment Alert (Yellow Warning)
```
💳 Dues Payment Needed
Your national and local dues are not current. Please update your payment status.

[Pay Dues Now]
```

---

## Timeline Example

**Day 0**: Admin runs sync, member marked for removal
- Email notification sent (optional - implement separately)
- Red warning appears on dashboard

**Day 30**: Member still not resolved
- Warning persists
- 60 days remaining shown

**Day 75**: Member's time is running out
- Page background of marked members shows urgent status
- Admin can see in `/portal/marked-members/` they're expiring soon

**Day 90**: Automatic removal triggered
- Management command runs (via cron or manual execution)
- Member account permanently deleted
- All associated data removed

---

## Configuration

### Customization Options

#### 1. Change Grace Period Length
Edit `pages/models.py` in `days_until_removal()` and `should_be_removed()` methods:
```python
GRACE_PERIOD_DAYS = 90  # Change this value
removal_deadline = self.marked_for_removal_date + timedelta(days=GRACE_PERIOD_DAYS)
```

#### 2. Change Warning Colors
Edit `member_notification_banner.html` to modify banner styling:
- Red (#ff6b6b) for removal notice
- Yellow (#ffc107) for dues notice

#### 3. Customize Banner Messages
Edit `member_notification_banner.html` to change warning text

#### 4. Automate Removal
Set up cron job to run weekly:
```bash
# Add to crontab
0 2 * * 0 cd /path/to/project && source venv/bin/activate && python manage.py remove_expired_members
```

---

## Permissions

| Role | Action |
|------|--------|
| **Admin** | Sync members, view marked members, run removal command, manually reset |
| **Officer** | View marked members, manually reset |
| **Member** | See warning banner, pay dues |
| **Public** | No access |

---

## CSV Format for HQ Export

Required columns (any of these names):
- `Member#` or `Member Number` or `MAJOR_KEY`

Example:
```csv
Member#,First Name,Last Name
12345,John,Smith
12346,Mary,Jones
```

---

## Troubleshooting

### Members Not Seeing Warning
- Check if `marked_for_removal_date` is set in database
- Verify Member relationship exists
- Clear browser cache

### Management Command Not Working
```bash
# Check for errors
python manage.py remove_expired_members --dry-run

# Check if members should be removed
python manage.py shell
>>> from pages.models import MemberProfile
>>> m = MemberProfile.objects.filter(marked_for_removal_date__isnull=False).first()
>>> m.should_be_removed()  # Should be True if 90+ days
>>> m.days_until_removal() # Should be 0 or negative
```

### Accidental Marking
- Go to Django Admin
- Edit MemberProfile
- Clear `marked_for_removal_date` field
- Save

---

## File Locations

- **View**: `/pages/views.py` - Functions `sync_members_with_hq`, `view_marked_members`
- **Form**: `/pages/forms_sync.py` - Class `MemberSyncForm`
- **Model**: `/pages/models.py` - Methods on `MemberProfile`
- **Template**: `/templates/pages/portal/sync_members.html`
- **Template**: `/templates/pages/portal/view_marked_members.html`
- **Template**: `/templates/pages/portal/member_notification_banner.html`
- **Command**: `/pages/management/commands/remove_expired_members.py`
- **Migration**: `/pages/migrations/0018_add_member_removal_tracking.py`

---

## API Integration Points

### Get Member Removal Status
```python
from pages.models import MemberProfile

member = MemberProfile.objects.get(user=request.user)

# Check if marked
if member.is_marked_for_removal():
    days_left = member.days_until_removal()
    reason = member.removal_reason
```

### Query Marked Members
```python
# All marked members
marked = MemberProfile.objects.filter(marked_for_removal_date__isnull=False)

# Expiring soon (< 30 days)
from datetime import timedelta
from django.utils import timezone

threshold = timezone.now() - timedelta(days=60)
expiring_soon = MemberProfile.objects.filter(
    marked_for_removal_date__lt=threshold
)
```

---

## Best Practices

1. **Always preview first** - Use preview button before executing sync
2. **Communicate clearly** - Email members before syncing
3. **Set expectations** - Announce the 90-day deadline
4. **Monitor weekly** - Check `/portal/marked-members/` regularly
5. **Document changes** - Log all sync operations
6. **Test procedures** - Run `--dry-run` before automated execution
7. **Backup data** - Backup database before running removal command

---

## Future Enhancements

- [ ] Email notifications when marked for removal
- [ ] Email reminder at 30 days before removal
- [ ] Bulk email to marked members
- [ ] Customizable grace period per action
- [ ] Audit trail of all syncs and removals
- [ ] Restore deleted members from backup
- [ ] Grade point adjustments for expelled/removed members
