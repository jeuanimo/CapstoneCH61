# Photo, Album, and Event Management Features

## Overview
This document describes the photo editing, album creation, and event creation features added to the member portal.

## Features Implemented

### 1. Photo Editing (✅ Completed)
Members can now edit photos they have uploaded.

**Access Control:**
- Only the photo uploader or staff can edit photos
- Edit button appears on photo detail page for authorized users

**Editable Fields:**
- Caption: Update or add photo description
- Tags: Comma-separated tags for photo categorization
- Album: Assign photo to an album
- Event: Link photo to a specific event

**User Flow:**
1. Navigate to photo detail page
2. Click "Edit" button (visible only to photo owner/staff)
3. Update photo details in the form
4. Click "Save Changes" to apply updates
5. Redirected back to photo detail page

**Files Modified:**
- `pages/forms_profile.py`: Added `EditPhotoForm` ModelForm
- `pages/views.py`: Added `edit_photo` view with permission checks
- `pages/urls.py`: Added route `/portal/photos/<id>/edit/`
- `templates/pages/portal/photo_detail.html`: Added Edit button
- `templates/pages/portal/edit_photo.html`: New template (created)

### 2. Album Creation (✅ Completed)
Members can create photo albums to organize their photos.

**Access Control:**
- Any logged-in member can create albums
- Album visibility controlled by "is_public" setting

**Album Fields:**
- Title: Album name (required, max 200 chars)
- Description: Album description (optional)
- Is Public: Toggle to make album visible to all members

**User Flow:**
1. Navigate to Photo Gallery
2. Click "New Album" button
3. Fill in album details
4. Check "Make this album visible to all members" if desired
5. Click "Create Album"
6. Redirected to photo gallery

**Files Modified:**
- `pages/forms_profile.py`: Added `CreateAlbumForm` ModelForm
- `pages/views.py`: Added `create_album` view
- `pages/urls.py`: Added route `/portal/albums/create/`
- `templates/pages/portal/photo_gallery.html`: Added "New Album" button
- `templates/pages/portal/create_album.html`: New template (created)

### 3. Event Creation (✅ Completed)
Officers can create events that appear on the calendar and can be used to organize photos.

**Access Control:**
- Only officers (ChapterLeadership members) or staff can create events
- Non-officers are redirected with error message

**Event Fields:**
- Title: Event name (required)
- Description: Event details (required)
- Start Date & Time: Event start (required, datetime-local input)
- End Date & Time: Event end (optional, datetime-local input)
- Location: Event location (optional)
- Image: Event promotional image (optional)

**User Flow:**
1. Navigate to Photo Gallery
2. Click "New Event" button (visible to all, but restricted on submission)
3. Fill in event details
4. Optionally add end date/time and promotional image
5. Click "Create Event"
6. Redirected to events page

**Files Modified:**
- `pages/forms_profile.py`: Added `CreateEventForm` ModelForm
- `pages/views.py`: Added `create_event` view with officer permission check
- `pages/urls.py`: Added route `/portal/events/create/`
- `templates/pages/portal/photo_gallery.html`: Added "New Event" button
- `templates/pages/portal/create_event.html`: New template (created)

## URL Routes Added

| Route | View | Permission | Purpose |
|-------|------|------------|---------|
| `/portal/photos/<id>/edit/` | `edit_photo` | Owner or Staff | Edit photo details |
| `/portal/albums/create/` | `create_album` | Any Member | Create new album |
| `/portal/events/create/` | `create_event` | Officer or Staff | Create new event |

## Form Validation

### EditPhotoForm
- All fields optional except those defined in model
- Album queryset filtered to public albums only
- Tags field accepts comma-separated values

### CreateAlbumForm
- Title: Required, max 200 characters
- Description: Optional
- Is Public: Boolean, defaults per model

### CreateEventForm
- Title and Description: Required
- Start Date: Required
- End Date: Optional (for multi-day events)
- Location: Optional
- Image: Optional file upload

## UI Integration

### Photo Detail Page Updates
- Added "Edit" button next to "Delete" button
- Edit button only visible to photo owner or staff
- Styled consistently with existing buttons

### Photo Gallery Updates
- Added button group with three actions:
  - Upload Photo (existing)
  - New Album (new)
  - New Event (new)
- Buttons styled with appropriate colors:
  - Primary (blue): Upload Photo
  - Info (light blue): New Album
  - Success (green): New Event

## Security & Permissions

### Photo Editing
```python
# Only owner or staff can edit
if photo.uploaded_by != request.user and not request.user.is_staff:
    messages.error(request, "You don't have permission to edit this photo.")
    return redirect('photo_detail', photo_id=photo.id)
```

### Event Creation
```python
# Check if user is an officer
is_officer = ChapterLeadership.objects.filter(
    email__iexact=request.user.email,
    is_active=True
).exists()

if not is_officer and not request.user.is_staff:
    messages.error(request, "Only officers can create events.")
    return redirect('portal_dashboard')
```

## User Experience Improvements

1. **Photo Management Workflow:**
   - Upload → View → Edit → Update (seamless flow)
   - Clear permission feedback messages
   - Preview photo while editing

2. **Album Organization:**
   - Easy album creation from photo gallery
   - Public/Private album controls
   - Albums appear in filter dropdown immediately

3. **Event Management:**
   - Officer-controlled event creation
   - Events available for photo tagging
   - Datetime picker for precise scheduling

## Technical Notes

### Model Dependencies
- `EditPhotoForm` uses `Photo` model (lines 395-420 in models.py)
- `CreateAlbumForm` uses `PhotoAlbum` model (lines 373-392 in models.py)
- `CreateEventForm` uses `Event` model

### Import Requirements
```python
# Added to forms_profile.py
from .models import MemberProfile, Announcement, Photo, PhotoAlbum, Event

# Added to views.py
from .forms_profile import (
    EditProfileForm, CreatePostForm, InvitationSignupForm,
    EditPhotoForm, CreateAlbumForm, CreateEventForm
)
```

### Template Inheritance
All new templates extend `base.html` and follow the existing styling:
- Bootstrap 5 cards with shadows
- Consistent form styling
- Icon usage with FontAwesome
- Dark mode compatible

## Testing Checklist

- [x] Photo editing form displays correctly
- [x] Photo editing saves changes successfully
- [x] Permission check prevents unauthorized editing
- [x] Album creation form displays correctly
- [x] Album creation saves successfully
- [x] Event creation form displays correctly
- [x] Event creation restricted to officers
- [x] All buttons visible in photo gallery
- [x] No import errors
- [x] Django check passes with no issues

## Future Enhancements

Potential improvements for future iterations:

1. **Album Editing:**
   - Allow album owners to edit album details
   - Add album deletion functionality

2. **Event Editing:**
   - Allow officers to edit event details
   - Add event deletion functionality

3. **Bulk Operations:**
   - Select multiple photos to add to album
   - Move photos between albums

4. **Enhanced Filtering:**
   - Filter by event on photo gallery
   - Combine album and event filters

5. **Photo Organization:**
   - Drag-and-drop photo reordering within albums
   - Set album cover photo

## Documentation References

- Photo Model: `pages/models.py` lines 395-420
- PhotoAlbum Model: `pages/models.py` lines 373-392
- Event Model: Referenced in Photo model
- Custom Template Filter: `pages/templatetags/custom_filters.py` (split filter)
