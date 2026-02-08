"""
=============================================================================
EXAMPLE CLASS-BASED VIEWS USING CUSTOM MIXINS
=============================================================================

This file demonstrates how to refactor the existing function-based views
to class-based views using the custom mixins.

Copy these patterns to progressively refactor your views.

NOTE: These are examples. Adjust to match your specific models and forms.

=============================================================================
"""

from django.views.generic import (
    CreateView, UpdateView, DeleteView, ListView, DetailView
)
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect

from .mixins import (
    StaffRequiredMixin, OfficerRequiredMixin, MemberRequiredMixin,
    SuccessMessageMixin, DeleteConfirmationMixin, 
    ListFilterMixin, UserFormKwargsMixin, OwnershipRequiredMixin
)
from .models import MemberProfile, Announcement, Photo
from .forms import MemberProfileForm


# ==================== MEMBER MANAGEMENT VIEWS ====================

class MemberListView(StaffRequiredMixin, ListFilterMixin, ListView):
    """
    List all members with search/filter support.
    
    Replaces: member_roster FBV
    
    Features:
    - Staff only access
    - Search by name or member number
    - Filter by status
    """
    model = MemberProfile
    template_name = 'pages/portal/roster.html'
    context_object_name = 'members'
    paginate_by = 50
    
    search_fields = ['user__first_name', 'user__last_name', 'member_number']
    filter_fields = {'status': 'status'}
    
    def get_queryset(self):
        """Get members ordered by last name"""
        queryset = super().get_queryset()
        return queryset.select_related('user').order_by('user__last_name')
    
    def get_context_data(self, **kwargs):
        """Add total count to context"""
        context = super().get_context_data(**kwargs)
        context['is_staff'] = self.request.user.is_staff
        context['total_members'] = self.get_queryset().count()
        return context


class MemberCreateView(StaffRequiredMixin, SuccessMessageMixin, CreateView):
    """
    Create a new member profile.
    
    Replaces: create_member FBV
    
    Features:
    - Staff only access
    - Auto-generates invitation code
    - Creates user account
    """
    model = MemberProfile
    form_class = MemberProfileForm
    template_name = 'pages/portal/member_form.html'
    success_url = reverse_lazy('member_roster')
    success_message = "Successfully created member profile for {first_name} {last_name}!"
    
    def get_context_data(self, **kwargs):
        """Add action to context for template"""
        context = super().get_context_data(**kwargs)
        context['action'] = 'Create'
        context['title'] = 'Create Member Profile'
        return context
    
    def form_valid(self, form):
        """
        Validate form and create user + member profile.
        
        Similar to the FBV but handled by Django's ModelForm.
        """
        response = super().form_valid(form)
        
        # Get the created member profile
        member_profile = self.object
        
        # TODO: Add custom logic here (leadership, invitations, etc.)
        # if form.cleaned_data.get('leadership_position'):
        #     # Create leadership record
        
        return response


class MemberUpdateView(StaffRequiredMixin, SuccessMessageMixin, UpdateView):
    """
    Edit an existing member profile.
    
    Replaces: edit_member FBV
    
    Features:
    - Staff only access
    - Updates user + profile
    - Manages leadership position
    """
    model = MemberProfile
    form_class = MemberProfileForm
    template_name = 'pages/portal/member_form.html'
    success_url = reverse_lazy('member_roster')
    success_message = "Successfully updated {user}'s profile!"
    
    def get_context_data(self, **kwargs):
        """Add action to context"""
        context = super().get_context_data(**kwargs)
        context['action'] = 'Edit'
        context['title'] = f'Edit {self.object.user.get_full_name()}'
        return context
    
    def form_valid(self, form):
        """Update user and profile together"""
        # Update user account
        user = self.object.user
        user.first_name = form.cleaned_data.get('first_name', '')
        user.last_name = form.cleaned_data.get('last_name', '')
        user.email = form.cleaned_data.get('email', '')
        user.save()
        
        return super().form_valid(form)


class MemberDeleteView(StaffRequiredMixin, DeleteConfirmationMixin, DeleteView):
    """
    Delete a member profile.
    
    Replaces: delete_member FBV
    
    Features:
    - Staff only access
    - Deletes user account too
    - Shows confirmation message
    """
    model = MemberProfile
    template_name = 'pages/portal/member_confirm_delete.html'
    success_url = reverse_lazy('member_roster')
    
    def delete(self, request, *args, **kwargs):
        """Delete user account along with profile"""
        member = self.get_object()
        user = member.user
        
        # Call parent delete
        response = super().delete(request, *args, **kwargs)
        
        # Also delete the user account
        user.delete()
        
        return response


# ==================== ANNOUNCEMENT VIEWS ====================

class AnnouncementListView(OfficerRequiredMixin, ListFilterMixin, ListView):
    """
    List all announcements.
    
    Features:
    - Officer/staff only
    - Search by title
    - Filter by active status
    """
    model = Announcement
    template_name = 'pages/portal/manage_announcements.html'
    context_object_name = 'announcements'
    paginate_by = 25
    
    search_fields = ['title', 'content']
    filter_fields = {'is_active': 'is_active'}
    
    def get_queryset(self):
        """Get announcements ordered by date"""
        return super().get_queryset().order_by('-is_pinned', '-publish_date')


class AnnouncementCreateView(OfficerRequiredMixin, SuccessMessageMixin, CreateView):
    """
    Create a new announcement.
    
    Features:
    - Officer/staff only
    - Auto-sets publisher
    - Success message
    """
    model = Announcement
    fields = ['title', 'content', 'is_active', 'is_pinned']
    template_name = 'pages/portal/announcement_form.html'
    success_url = reverse_lazy('manage_announcements')
    success_message = "Announcement '{title}' created successfully!"
    
    def form_valid(self, form):
        """Set publisher before saving"""
        form.instance.published_by = self.request.user
        return super().form_valid(form)


# ==================== PHOTO VIEWS ====================

class PhotoEditView(OwnershipRequiredMixin, SuccessMessageMixin, UpdateView):
    """
    Edit a photo's caption/metadata.
    
    Replaces: edit_program_photo FBV
    
    Features:
    - Only owner or staff can edit
    - Auto-checks ownership
    - Success message
    """
    model = Photo
    fields = ['caption', 'tags']
    template_name = 'pages/edit_photo.html'
    success_url = reverse_lazy('photo_gallery')
    success_message = "Photo caption updated successfully!"
    
    # Specify which field contains the owner
    user_field = 'uploaded_by'


class PhotoDeleteView(OwnershipRequiredMixin, DeleteConfirmationMixin, DeleteView):
    """
    Delete a photo.
    
    Replaces: delete_program_photo FBV
    
    Features:
    - Only owner or staff can delete
    - Delete image file too
    - Confirmation message
    """
    model = Photo
    template_name = 'pages/photo_confirm_delete.html'
    success_url = reverse_lazy('photo_gallery')
    
    user_field = 'uploaded_by'
    
    def delete(self, request, *args, **kwargs):
        """Delete image file before deleting record"""
        photo = self.get_object()
        
        # Delete the image file
        if photo.image:
            photo.image.delete()
        
        # Delete the database record
        return super().delete(request, *args, **kwargs)


# ==================== URL PATTERNS EXAMPLE ====================

"""
Update your urls.py to use these CBVs:

from django.urls import path
from . import views

urlpatterns = [
    # Member Management (replacing FBVs)
    path('admin/members/', views.MemberListView.as_view(), name='member_roster'),
    path('admin/members/create/', views.MemberCreateView.as_view(), name='create_member'),
    path('admin/members/<int:pk>/edit/', views.MemberUpdateView.as_view(), name='edit_member'),
    path('admin/members/<int:pk>/delete/', views.MemberDeleteView.as_view(), name='delete_member'),
    
    # Announcements
    path('admin/announcements/', views.AnnouncementListView.as_view(), name='manage_announcements'),
    path('admin/announcements/create/', views.AnnouncementCreateView.as_view(), name='create_announcement'),
    
    # Photos
    path('photo/<int:pk>/edit/', views.PhotoEditView.as_view(), name='edit_photo'),
    path('photo/<int:pk>/delete/', views.PhotoDeleteView.as_view(), name='delete_photo'),
]
"""


# ==================== MIGRATION TIPS ====================

"""
HOW TO MIGRATE YOUR EXISTING FBVs:

1. Start with simple CRUD views:
   - member_roster → MemberListView
   - create_member → MemberCreateView
   - edit_member → MemberUpdateView
   - delete_member → MemberDeleteView

2. Keep complex views as FBVs:
   - signup_view (custom logic with multiple models)
   - import_members (CSV processing)
   - login_view (custom authentication)

3. Use a gradual approach:
   - Don't refactor everything at once
   - Test each converted view thoroughly
   - Keep old views in comments until new ones work

4. Common patterns:

   OLD FBV PATTERN                CBV EQUIVALENT
   ─────────────────────────────  ──────────────────────────────
   @login_required                LoginRequiredMixin
   @user_passes_test(...)         OfficerRequiredMixin, StaffRequiredMixin
   
   form = MyForm()                get_form_class()
   if form.is_valid():            form_valid()
   return redirect(...)           success_url
   
   context = {...}                get_context_data()
   return render(...)             (automatic)
   
   for field, errors:             FormValidMessagesMixin
     messages.error()

5. Testing:
   - Test that redirects work correctly
   - Test permissions are enforced
   - Test forms process correctly
   - Verify success messages appear
"""
