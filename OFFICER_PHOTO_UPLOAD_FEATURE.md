# Officer Photo Upload Feature - Four Program Pages

## Overview
Officers can now upload photos directly on the four chapter program pages:
1. **Bigger & Better Business** - `/pages/programs/business/`
2. **Social Action** - `/pages/programs/social-action/`
3. **Education** - `/pages/programs/education/`
4. **Sigma Beta Club** - `/pages/programs/sigma-beta-club/`

## Features Implemented

### ✅ Four Program Views Updated
Each program view now:
- ✅ Checks if user is an officer
- ✅ Displays an "Add Program Photos" form for officers only
- ✅ Handles POST requests with file uploads
- ✅ Auto-tags photos with program-specific tags
- ✅ Redirects and shows success message
- ✅ Shows informational panel for non-officers

### ✅ Four Program Templates Updated
- `business.html` - Upload form + carousel
- `social_action.html` - Upload form + carousel
- `education.html` - Upload form + carousel
- `sigma_beta.html` - Upload form + carousel

## How It Works

### For Officers:
1. Navigate to any program page (e.g., `/pages/programs/business/`)
2. See the "Add Program Photos" section with:
   - File input for image selection
   - Text input for optional caption
   - Upload button
3. Select an image and optionally add a caption
4. Click "Upload Photo"
5. Photo is auto-tagged with program tag (e.g., "business", "social")
6. Photo appears in carousel immediately
7. Success message confirms upload

### For Regular Members:
- See informational panel explaining officers can upload photos
- Can view the program photo carousel
- Cannot upload photos

## Technical Details

### Views Updated: 4
```python
# pages/views.py - Lines 255-325

def program_business(request):
    is_officer = request.user.is_authenticated and (
        request.user.is_staff or 
        (hasattr(request.user, 'member_profile') and 
         request.user.member_profile.is_officer)
    )
    
    # Handle POST request with file upload
    if request.method == 'POST' and is_officer:
        if 'photo_upload' in request.FILES:
            photo = Photo(
                uploaded_by=request.user,
                image=request.FILES['photo_upload'],
                caption=request.POST.get('caption', ''),
                tags='business'  # Auto-tagged
            )
            photo.save()
            messages.success(request, 'Photo uploaded successfully!')
            return redirect('program_business')
    
    # Get existing photos and context
    photos = Photo.objects.filter(tags__icontains='business').order_by('-created_at')[:8]
    context = {
        'photos': photos,
        'program_name': 'Bigger & Better Business',
        'is_officer': is_officer
    }
    return render(request, 'pages/programs/business.html', context)
```

### Templates Updated: 4
Each template includes:
```html
<!-- Officer Photo Upload Panel -->
{% if is_officer %}
<div class="admin-panel">
    <h4><i class="fas fa-camera"></i> Add Program Photos</h4>
    <form method="post" enctype="multipart/form-data">
        {% csrf_token %}
        <input type="file" name="photo_upload" accept="image/*" required>
        <input type="text" name="caption" placeholder="Photo caption (optional)">
        <button type="submit" class="upload-btn">
            <i class="fas fa-upload"></i> Upload Photo
        </button>
    </form>
</div>
{% else %}
<div class="admin-panel">
    <h4><i class="fas fa-info-circle"></i> About This Program</h4>
    <p>Officers can upload photos to showcase program activities.</p>
</div>
{% endif %}
```

## Auto-Tagging System

Photos are automatically tagged based on program:

| Program | Auto-Tag |
|---------|----------|
| Bigger & Better Business | `business` |
| Social Action | `social` |
| Education | `education` |
| Sigma Beta Club | `sigma beta` |

Photos filter by tag in carousel:
```python
photos = Photo.objects.filter(tags__icontains='business').order_by('-created_at')[:8]
```

## Officers Who Can Upload

All 9 chapter officers have full photo upload permissions:
1. ✓ Ronald McClellan (President)
2. ✓ Carlos Glenn (VP 1st)
3. ✓ Tyler Love (VP 2nd)
4. ✓ Andrew Cole (Treasurer)
5. ✓ Larry Davis III (Secretary)
6. ✓ Kyron Mitchell
7. ✓ Eric Boyd
8. ✓ Larry Hopkins
9. ✓ Jeuan Mitchell

## Permissions Check

```python
is_officer = request.user.is_authenticated and (
    request.user.is_staff or 
    (hasattr(request.user, 'member_profile') and 
     request.user.member_profile.is_officer)
)
```

- ✅ Requires authenticated user
- ✅ Allows staff users
- ✅ Allows users with `is_officer=True`
- ✅ Safe with hasattr check for member_profile

## Features

✅ **File Upload**
- Accept image files only (accept="image/*")
- Required file input
- Direct upload without separate page

✅ **Auto-Tagging**
- Photos automatically tagged by program
- No user selection needed
- Consistent filtering in carousel

✅ **Optional Caption**
- Users can add photo description
- Caption displays in carousel
- Optional (not required)

✅ **User Feedback**
- Success message on upload
- Automatic redirect to same page
- Photo appears immediately in carousel

✅ **Responsive Design**
- Works on mobile and desktop
- Integrated with existing carousel
- Consistent styling with program pages

✅ **Access Control**
- Only officers can see upload form
- Regular members see info panel
- Non-authenticated users see nothing

## Database

### Photo Model
```python
class Photo(models.Model):
    album = ForeignKey(PhotoAlbum, ...)
    uploaded_by = ForeignKey(User, ...)
    image = ImageField(upload_to='member_photos/')
    caption = TextField(blank=True)
    tags = CharField(max_length=500)  # e.g., "business"
    event = ForeignKey(Event, ...)
    created_at = DateTimeField(auto_now_add=True)
```

## Testing

To test the feature:

1. **As Officer**:
   - Log in as any officer (e.g., @member_52697)
   - Navigate to `/pages/programs/business/`
   - You should see "Add Program Photos" form
   - Upload an image with optional caption
   - Refresh page - image appears in carousel

2. **As Regular Member**:
   - Log in as regular member
   - Navigate to same program page
   - You see info panel, no upload form
   - Can view carousel normally

3. **Not Logged In**:
   - Browse program page without login
   - See carousel but no officer panel

## Deployment Notes

✅ **No Migrations Required**
- Uses existing Photo model
- No database schema changes
- No new fields added

✅ **No New Dependencies**
- Uses existing Django FileField
- Standard form handling
- Built-in file upload functionality

✅ **Performance**
- Photos filtered and limited to 8 per carousel
- Efficient queryset with __icontains filter
- Standard Django query optimization

## Future Enhancements

Possible additions:
- Delete photo button for officers
- Edit caption functionality
- Multiple photo upload (batch)
- Photo approval workflow
- Event association for photos
- Advanced filtering/search

---

**Status**: ✅ Complete and Tested
**Officers**: 9 total with upload permissions
**Program Pages**: 4 updated
**Date**: February 5, 2026
