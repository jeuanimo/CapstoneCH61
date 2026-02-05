# Officer Permissions Setup Guide

## Problem Identified

The user **jeuan.mitchell** was logged in as a chapter officer but **did not have CRUD access** to administrative pages because the `is_officer` flag was set to `False` in their MemberProfile.

## Root Cause

Two issues were found:

1. **is_officer flag not set**: The user's MemberProfile had `is_officer = False`
2. **Permission decorator bug**: Permission checks were using incorrect related_name `memberprofile` instead of the correct `member_profile`

## Solution Applied

### 1. Granted Officer Privileges to jeuan.mitchell ✅
```bash
python manage.py shell
>>> from django.contrib.auth.models import User
>>> user = User.objects.get(username='jeuan.mitchell')
>>> user.member_profile.is_officer = True
>>> user.member_profile.save()
```

**Status: Updated** - `is_officer` is now `True`

### 2. Fixed Permission Decorators in views.py ✅
**Changed from:**
```python
@user_passes_test(lambda u: u.is_staff or (hasattr(u, 'memberprofile') and u.memberprofile.is_officer))
```

**Changed to:**
```python
@user_passes_test(lambda u: u.is_staff or (hasattr(u, 'member_profile') and u.member_profile.is_officer))
```

**Fixed 15 occurrences across:**
- add_leadership()
- edit_leadership()
- delete_leadership()
- delete_event()
- edit_product()
- delete_product()
- import_products()
- And all other admin/officer views

## Model Information

### MemberProfile Model
**File**: `pages/models.py`

**Field**: `is_officer`
- **Type**: BooleanField
- **Default**: False
- **Purpose**: Indicates if a member has admin/officer privileges

**Related Name**: `member_profile` (NOT `memberprofile`)
- Access user's profile: `user.member_profile`
- Check permission: `user.member_profile.is_officer`

### Permission Checking Pattern
```python
# Correct way to check officer status
is_officer = hasattr(user, 'member_profile') and user.member_profile.is_officer

# In decorators
@user_passes_test(lambda u: u.is_staff or (hasattr(u, 'member_profile') and u.member_profile.is_officer))
```

## Managing Officer Privileges

### Method 1: Django Admin (Recommended)
1. Go to `/admin/pages/memberprofile/`
2. Find the member
3. Check the "Is Officer" checkbox in the "Admin Privileges" section
4. Click Save

### Method 2: Management Script
Use the provided `manage_officers.py` script:

```bash
# Check officer status
python manage_officers.py --check username

# Grant officer privileges
python manage_officers.py --grant username

# Revoke officer privileges
python manage_officers.py --revoke username

# List all officers
python manage_officers.py --list
```

### Method 3: Django Shell
```bash
python manage.py shell
>>> from django.contrib.auth.models import User
>>> user = User.objects.get(username='username')
>>> user.member_profile.is_officer = True
>>> user.member_profile.save()
```

## Access Rights by Role

### Staff Members (`is_staff = True`)
- ✅ All administrative pages
- ✅ Product management
- ✅ Member management
- ✅ Event management
- ✅ Financial management

### Officers (`is_officer = True`)
- ✅ Product management (CRUD)
- ✅ CSV import
- ✅ Chapter leadership management (CRUD)
- ✅ Event management (CRUD)
- ❌ System settings
- ❌ User management
- ❌ Django admin access

### Regular Members (`is_staff = False`, `is_officer = False`)
- ✅ View public pages
- ✅ Access member portal
- ✅ View product listings
- ✅ Browse events and announcements
- ❌ CRUD operations
- ❌ Administrative functions

## Pages/URLs Requiring Officer Status

**Boutique Management:**
- `/pages/boutique/admin/add-product/` - Add new product
- `/pages/boutique/admin/edit-product/<id>/` - Edit product
- `/pages/boutique/admin/delete-product/<id>/` - Delete product
- `/pages/boutique/admin/import-products/` - Bulk import from CSV

**Chapter Leadership:**
- `/admin/chapter-leadership/add/` - Add officer
- `/admin/chapter-leadership/<id>/edit/` - Edit officer
- `/admin/chapter-leadership/<id>/delete/` - Delete officer

**Event Management:**
- `/admin/events/delete/<id>/` - Delete events

## Verification

✅ **jeuan.mitchell status**:
```
Username: jeuan.mitchell
Name: Jeuan Mitchell
Member Number: 3953LM
Status: financial_life_member
Is Officer: True ✓
```

✅ **Permission checks fixed**:
- All views now use correct `member_profile` related_name
- All decorators properly check for officer status
- Django system checks pass

## Next Steps

1. ✅ Clear browser cache and log back in
2. ✅ Test CRUD operations on boutique products
3. ✅ Test chapter leadership management
4. ✅ Test event management

## Troubleshooting

**Issue**: Still can't access admin pages after logging in
- **Solution**: Clear browser cache, cookies, and log out/log back in

**Issue**: "Permission denied" on specific page
- **Verify**: User has `is_officer = True` in admin
- **Check**: View decorator is checking correct field

**Issue**: Can't find member in admin
- **Try**: Go to `/admin/pages/memberprofile/` directly
- **Search**: By member number or name

---

**Last Updated**: February 5, 2026
**Fixed By**: System Update
**Status**: ✅ COMPLETE
