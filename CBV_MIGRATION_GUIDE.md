# CBV Migration Guide - Quick Reference

## Files Created

### 1. `pages/mixins.py` - Reusable Permission Mixins
Contains custom mixins for common permission patterns:
- `StaffRequiredMixin` - Restrict to admin/staff only
- `OfficerRequiredMixin` - Restrict to officers or staff  
- `MemberRequiredMixin` - Login required
- `FormValidMessagesMixin` - Show form errors as toast alerts
- `SuccessMessageMixin` - Display success messages
- `DeleteConfirmationMixin` - Deletion confirmation messages
- `ListFilterMixin` - Auto-apply search and filters
- `UserFormKwargsMixin` - Pass user to form
- `OwnershipRequiredMixin` - Check object ownership

### 2. `pages/cbv_examples.py` - Example View Conversions
Shows how to convert 8 different FBVs to CBVs with detailed comments.

---

## Quick Comparison: FBV vs CBV

### Before (FBV) - Current Code
```python
@login_required
@user_passes_test(lambda u: u.is_staff)
def create_member(request):
    """Create a new member profile (admin only)"""
    if request.method == 'POST':
        form = MemberProfileForm(request.POST, request.FILES)
        if form.is_valid():
            # ... lots of boilerplate ...
            messages.success(request, f"Successfully created {user.get_full_name()}!")
            return redirect('member_roster')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = MemberProfileForm()
    
    context = {'form': form, 'action': 'Create', 'title': 'Create Member Profile'}
    return render(request, 'pages/portal/member_form.html', context)
```

### After (CBV) - Cleaner & DRY
```python
class MemberCreateView(StaffRequiredMixin, SuccessMessageMixin, CreateView):
    model = MemberProfile
    form_class = MemberProfileForm
    template_name = 'pages/portal/member_form.html'
    success_url = reverse_lazy('member_roster')
    success_message = "Successfully created member profile!"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'Create'
        context['title'] = 'Create Member Profile'
        return context
```

**Benefits:**
- ✅ 50% less code
- ✅ Permissions handled by mixins
- ✅ No decorator soup  
- ✅ Reusable across views
- ✅ Easier to test
- ✅ Django's form handling built-in

---

## Migration Roadmap - Phase 1 (Member Management)

### Views to Migrate First (Simplest)
These are pure CRUD with no custom logic - easiest to convert.

| FBV | CBV | Difficulty |
|-----|-----|-----------|
| `member_roster` | `MemberListView` | ⭐ Easy |
| `create_member` | `MemberCreateView` | ⭐ Easy |
| `edit_member` | `MemberUpdateView` | ⭐ Easy |
| `delete_member` | `MemberDeleteView` | ⭐ Easy |

**Expected Result:** ~200 lines of FBV code → ~80 lines of CBV code

### How to Implement Phase 1

1. **Add to `pages/views.py`** (or create `pages/views_cbv.py`):
   ```python
   from .mixins import StaffRequiredMixin, SuccessMessageMixin
   from django.views.generic import CreateView, UpdateView, DeleteView, ListView
   
   class MemberListView(StaffRequiredMixin, ListView):
       # ... (copy from cbv_examples.py)
   ```

2. **Update `urls.py`** - Point to new CBVs:
   ```python
   from . import views
   
   urlpatterns = [
       path('roster/', views.MemberListView.as_view(), name='member_roster'),
       path('create/', views.MemberCreateView.as_view(), name='create_member'),
       # ... etc
   ]
   ```

3. **Test thoroughly:**
   - Check permissions work
   - Verify redirects
   - Test form submission
   - Confirm success messages

4. **Once working, remove old FBVs** from views.py

---

## Phase 2 Candidates (Medium Difficulty)

These have some custom logic but are still refactorable:

| View | Custom Logic | Strategy |
|------|-------------|----------|
| `AnnouncementListView` | List + filter | Use `ListFilterMixin` |
| `PhotoEditView` | Owner check | Use `OwnershipRequiredMixin` |
| `PhotoDeleteView` | Delete file + record | Override `delete()` method |
| `EventListView` | Filter by month | Custom queryset |

---

## Phase 3 - Keep as FBVs (Complex Logic)

These views have business logic best handled in FBVs for now:

- **`login_view`** - Custom auth + signup branching
- **`signup_view`** - Invitation code validation + user creation
- **`import_members`** - CSV processing
- **`program_*`** - Photo upload + event linking
- **`dues_and_payments`** - Bulk operations

**These can stay as FBVs** - they're too custom for generic CBVs.

---

## Common CBV Patterns

### Pattern 1: List with Permissions + Filtering
```python
class MyListView(OfficerRequiredMixin, ListFilterMixin, ListView):
    model = MyModel
    search_fields = ['name', 'email']
    filter_fields = {'status': 'status'}
    paginate_by = 50
```

### Pattern 2: Create with Auto-Set Fields
```python
class MyCreateView(StaffRequiredMixin, SuccessMessageMixin, CreateView):
    model = MyModel
    form_class = MyForm
    success_message = "Created {name} successfully!"
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)
```

### Pattern 3: Update with Ownership Check
```python
class MyUpdateView(OwnershipRequiredMixin, SuccessMessageMixin, UpdateView):
    model = MyModel
    form_class = MyForm
    user_field = 'author'  # or 'created_by' or 'uploaded_by'
    success_message = "Updated {name} successfully!"
```

### Pattern 4: Delete with Side Effects
```python
class MyDeleteView(OwnershipRequiredMixin, DeleteConfirmationMixin, DeleteView):
    model = MyModel
    success_url = reverse_lazy('my_list')
    
    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        # Delete related files/data first
        if obj.image:
            obj.image.delete()
        # Then delete object
        return super().delete(request, *args, **kwargs)
```

---

## Testing Your Converted Views

### Unit Test Example
```python
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from pages.models import MemberProfile

class MemberCreateViewTest(TestCase):
    def setUp(self):
        self.staff_user = User.objects.create_user(
            username='admin', password='test', is_staff=True
        )
    
    def test_requires_staff(self):
        """Regular users cannot create members"""
        response = self.client.get(reverse('create_member'))
        self.assertEqual(response.status_code, 302)  # Redirect
    
    def test_staff_can_create(self):
        """Staff users can see form"""
        self.client.login(username='admin', password='test')
        response = self.client.get(reverse('create_member'))
        self.assertEqual(response.status_code, 200)
    
    def test_form_submission(self):
        """Form submission creates member"""
        self.client.login(username='admin', password='test')
        response = self.client.post(reverse('create_member'), {
            'username': 'newmember',
            'email': 'new@example.com',
            'first_name': 'New',
            'last_name': 'Member',
            'member_number': '12345',
            'status': 'financial',
        })
        self.assertEqual(response.status_code, 302)  # Redirect on success
        self.assertEqual(MemberProfile.objects.count(), 1)
```

---

## Implementation Checklist

### Step 1: Setup ✅
- [ ] Copy `pages/mixins.py` 
- [ ] Copy `pages/cbv_examples.py` (for reference)
- [ ] Review mixin docstrings

### Step 2: Convert Phase 1 Views
- [ ] Create `MemberListView`
- [ ] Create `MemberCreateView`
- [ ] Create `MemberUpdateView`
- [ ] Create `MemberDeleteView`
- [ ] Update `urls.py` to use new views
- [ ] Test all 4 views thoroughly

### Step 3: Remove Old Views
- [ ] Delete/comment out FBV versions
- [ ] Verify old URLs still work

### Step 4: Phase 2 Candidates
- [ ] Convert announcement views
- [ ] Convert photo views
- [ ] Convert event views

### Step 5: Update Tests
- [ ] Write tests for CBVs
- [ ] Update integration tests
- [ ] Full QA pass

---

## Troubleshooting

### Issue: Permissions not working
**Check:** Make sure mixin is first in inheritance order
```python
# ❌ Wrong
class MyView(ListView, StaffRequiredMixin): ...

# ✅ Correct  
class MyView(StaffRequiredMixin, ListView): ...
```

### Issue: Form isn't saving
**Check:** Are you calling `super().form_valid(form)`?
```python
def form_valid(self, form):
    form.instance.user = self.request.user
    return super().form_valid(form)  # ← Don't forget this
```

### Issue: Context variables missing
**Check:** Are you calling `super().get_context_data()`?
```python
def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)  # ← Gets all parent context
    context['my_var'] = 'value'
    return context
```

---

## Resources

- Django CBV Docs: https://docs.djangoproject.com/en/stable/topics/class-based-views/
- Classy Class-Based Views: https://ccbv.co/
- Django Mixins: https://docs.djangoproject.com/en/stable/ref/class-based-views/mixins/

---

## Ready to Start?

Begin with **Phase 1** - Member Management views. They're the simplest and will give you the most benefit (least code duplication).

Once those are working, you'll understand the patterns well enough to convert Phase 2 views quickly.

Save Phase 3 (complex business logic) for FBVs - they're fine as-is!
