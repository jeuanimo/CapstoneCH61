# Officer Photo Management Feature - Edit & Delete

## Overview

Officers can now **edit and delete** photos they've uploaded to the four program pages:
- Bigger & Better Business
- Social Action
- Education  
- Sigma Beta Club

This completes the photo management workflow, allowing officers to maintain and update program photo galleries.

## Features

### Edit Photo Caption
- Officers can click the **edit button** (pencil icon) on their photos
- Opens a dedicated edit form where the caption can be modified
- Includes photo preview for reference
- Changes are saved immediately upon submission
- User is redirected back to the program page

### Delete Photo
- Officers can click the **delete button** (trash icon) on their photos
- Opens a confirmation page showing photo details
- Prevents accidental deletions with explicit confirmation
- Displays photo preview and metadata (uploader, date)
- Once confirmed, photo is permanently removed

### Permission Controls
- Only officers who uploaded a photo can edit/delete it
- Staff users (admins) can edit/delete any photo
- Unauthorized users see error message and are redirected
- Edit/delete buttons only appear for authorized users

## Implementation Details

### New View Functions

#### `edit_program_photo(request, photo_id)`
**Location:** [pages/views.py](pages/views.py#L372)
- Handles GET requests to show edit form
- Handles POST requests to update caption
- Validates user permissions (upload or staff)
- Saves changes and redirects to appropriate program page
- Auto-detects program type from photo tags

#### `delete_program_photo(request, photo_id)`
**Location:** [pages/views.py](pages/views.py#L408)
- Handles GET requests to show confirmation page
- Handles POST requests to delete photo
- Validates user permissions (upload or staff)
- Deletes photo file and database record
- Auto-detects program type from photo tags
- Redirects to appropriate program page

### URL Routes

**New routes added to** [pages/urls.py](pages/urls.py#L13-L14):

```python
path('programs/photo/<int:photo_id>/edit/', views.edit_program_photo, name='edit_program_photo'),
path('programs/photo/<int:photo_id>/delete/', views.delete_program_photo, name='delete_program_photo'),
```

### UI Components

#### Edit/Delete Buttons on Carousel
**Updated templates:**
- [business.html](templates/pages/programs/business.html)
- [social_action.html](templates/pages/programs/social_action.html)
- [education.html](templates/pages/programs/education.html)
- [sigma_beta.html](templates/pages/programs/sigma_beta.html)

**Location in templates:** Photo carousel section (lines 467-480 approx)

**Display:**
- Edit button (pencil icon) - styled with primary color
- Delete button (trash icon) - styled with danger color on hover
- Buttons positioned in top-right corner of carousel image
- Only visible to officers who uploaded the photo
- Uses Font Awesome icons

**CSS Styles:**
```css
.photo-actions {
    position: absolute;
    top: 10px;
    right: 10px;
    display: flex;
    gap: 0.5rem;
    z-index: 10;
}

.photo-action-btn {
    background: rgba(22, 79, 144, 0.9);
    padding: 0.5rem 0.75rem;
    border-radius: 4px;
    cursor: pointer;
    transition: background 0.3s ease;
}

.photo-action-btn.delete-btn:hover {
    background: #d32f2f;
}
```

### Templates

#### Edit Photo Template
**File:** [edit_program_photo.html](templates/pages/edit_program_photo.html)

Features:
- Page heading with icon
- Photo preview (max-height: 300px)
- Textarea for caption editing
- Save and Cancel buttons
- Styled consistently with existing UI
- Dark mode support
- Responsive design

#### Delete Confirmation Template  
**File:** [delete_program_photo.html](templates/pages/delete_program_photo.html)

Features:
- Page heading with danger color
- Warning banner with explanation
- Photo preview
- Photo metadata display:
  - Caption
  - Uploaded by
  - Date uploaded
- Confirmation buttons (Yes/No)
- Styled consistently with existing UI
- Dark mode support
- Responsive design

## Permission Model

### Who Can Edit/Delete?
```python
is_officer = request.user.is_authenticated and (
    request.user.is_staff or 
    (hasattr(request.user, 'member_profile') and 
     request.user.member_profile.is_officer)
)

# Ownership check
if photo.uploaded_by != request.user and not request.user.is_staff:
    # Unauthorized - show error
    messages.error(request, "You can only edit/delete your own photos.")
    # Redirect to program page
```

### Permission Levels
- **Admins (is_staff):** Can edit/delete any photo
- **Officers:** Can only edit/delete their own photos
- **Regular members:** No edit/delete access

## Program Detection

Photos are automatically associated with programs via tags. Detection logic:

```python
if 'business' in photo.tags.lower():
    redirect_view = 'program_business'
elif 'social' in photo.tags.lower() and 'action' in photo.tags.lower():
    redirect_view = 'program_social_action'
elif 'education' in photo.tags.lower():
    redirect_view = 'program_education'
elif 'sigma beta' in photo.tags.lower() or 'club' in photo.tags.lower():
    redirect_view = 'program_sigma_beta'
```

Tags are set automatically when photo is uploaded (from upload forms).

## Usage Flow

### Editing a Photo Caption

1. Officer views program page
2. Hovers over photo in carousel
3. Sees edit button (pencil icon)
4. Clicks edit button
5. Redirected to edit form page
6. Updates caption text
7. Clicks "Save Changes"
8. Redirected back to program page
9. Success message: "Photo caption updated successfully!"

### Deleting a Photo

1. Officer views program page
2. Hovers over photo in carousel
3. Sees delete button (trash icon)
4. Clicks delete button
5. Redirected to confirmation page
6. Reviews photo and metadata
7. Clicks "Yes, Delete Photo"
8. Redirected back to program page
9. Success message: "Photo deleted successfully!"

## Testing

### Test Cases

1. **Edit Own Photo**
   - Login as officer who uploaded photo
   - Navigate to program page
   - Click edit button
   - Update caption
   - Submit and verify redirect
   - Verify caption updated on carousel

2. **Delete Own Photo**
   - Login as officer who uploaded photo
   - Navigate to program page
   - Click delete button
   - Verify confirmation page shows correct photo
   - Confirm deletion
   - Verify photo removed from carousel

3. **Unauthorized Edit**
   - Login as different officer
   - Try to access edit URL for another's photo
   - Verify error message: "You can only edit your own photos"
   - Verify redirected to program page

4. **Unauthorized Delete**
   - Login as different officer
   - Try to access delete URL for another's photo
   - Verify error message: "You can only delete your own photos"
   - Verify redirected to program page

5. **Admin Override**
   - Login as admin (is_staff)
   - Navigate to program page with any officer's photo
   - Verify edit/delete buttons visible
   - Edit photo successfully
   - Delete photo successfully

6. **Non-Officer Access**
   - Login as regular member
   - Navigate to program page
   - Verify no edit/delete buttons visible on any photos

7. **Program Detection**
   - Upload photo to each program page
   - Edit/delete photo
   - Verify redirects back to correct program page

## Database

### Photo Model Fields Used
- `id` - Primary key, used in URL parameters
- `image` - ImageField, deleted when photo deleted
- `caption` - TextField, updated during edit
- `tags` - CharField, used for program detection
- `uploaded_by` - ForeignKey(User), for permission check
- `created_at` - DateTimeField, displayed in delete confirmation

### No New Migrations Needed
- Uses existing Photo model from [pages/models.py](pages/models.py#L455)
- No database schema changes required

## Error Handling

### Permission Denied
- User sees: "You can only edit/delete your own photos."
- User redirected to program page
- Used when user tries to edit/delete another's photo

### Photo Not Found
- Django returns 404 error
- User sees standard 404 page
- Occurs if photo ID doesn't exist

### Missing Required Fields
- Validation by form fields
- Edit form requires valid caption
- Delete always proceeds if confirmed

## Messages

### Success Messages
- **Edit:** "Photo caption updated successfully!"
- **Delete:** "Photo deleted successfully!"

### Error Messages
- **Permission:** "You can only edit/delete your own photos."
- **Not Found:** Django 404 page

## Dark Mode Support

Both new templates include dark mode CSS support:
- Background colors adapt
- Text colors have proper contrast
- Buttons maintain visibility
- Forms remain readable

Example:
```css
body.dark-mode .edit-photo-container {
    background: #1a2a4a;
}

body.dark-mode .form-group label {
    color: #e0e0e0;
}
```

## Responsive Design

Templates are fully responsive:
- Desktop: Full-width forms
- Tablet: Adjusted padding and spacing
- Mobile: Single-column layout, full-width buttons

## Integration Points

### Existing Features
- Uses existing Photo model (no schema changes)
- Integrates with existing permission system
- Uses existing messaging framework
- Works with existing dark mode support
- Follows existing URL naming conventions

### Related Features
- Photo upload (program pages) - ✅ Working
- Photo gallery (portal) - Uses different photo views
- Officer permissions - ✅ Validated before each operation
- Program pages - ✅ Program detection from tags

## File Changes Summary

### New Files (2)
- `templates/pages/edit_program_photo.html` - Edit form page
- `templates/pages/delete_program_photo.html` - Delete confirmation page

### Modified Files (6)
- `pages/views.py` - Added edit_program_photo() and delete_program_photo()
- `pages/urls.py` - Added 2 URL routes
- `templates/pages/programs/business.html` - Added edit/delete buttons and CSS
- `templates/pages/programs/social_action.html` - Added edit/delete buttons and CSS
- `templates/pages/programs/education.html` - Added edit/delete buttons and CSS
- `templates/pages/programs/sigma_beta.html` - Added edit/delete buttons and CSS

### Unchanged Files
- `pages/models.py` - Photo model unchanged
- `config/` - URL config unchanged (uses pages.urls)
- All other app files - No changes needed

## Deployment Checklist

- ✅ No database migrations needed
- ✅ Django system check passes
- ✅ All templates created
- ✅ All URL routes added
- ✅ All views implemented
- ✅ Permission validation included
- ✅ Dark mode support included
- ✅ Responsive design verified
- ✅ Error handling implemented
- ✅ User messages configured

Ready for production deployment!

## Future Enhancements

Possible future improvements:
- Batch delete multiple photos
- Reorder photos in carousel
- Add tags/categories within captions
- Photo comments/reactions
- Bulk edit captions
- Photo cropping/adjustment before upload
- Auto-tagging with AI
- Photo expiration dates

