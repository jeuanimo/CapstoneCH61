"""
=============================================================================
DJANGO CLASS-BASED VIEW MIXINS
=============================================================================

Custom mixins for handling authentication, permissions, and common patterns
across the chapter website.

MIXINS:
- StaffRequiredMixin: Restrict access to staff/admin users
- OfficerRequiredMixin: Restrict access to officers or staff
- MemberRequiredMixin: Restrict access to authenticated members
- FormValidMessagesMixin: Display form validation errors as messages
- SuccessMessageMixin: Display success messages on form submission

=============================================================================
"""

from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect
from django.http import HttpResponseForbidden
import logging

logger = logging.getLogger(__name__)


class StaffRequiredMixin(UserPassesTestMixin):
    """
    Restrict access to staff/admin users only.
    
    Usage:
        class MyAdminView(StaffRequiredMixin, CreateView):
            ...
    """
    
    def test_func(self):
        """Test if user is staff"""
        return self.request.user.is_staff
    
    def handle_no_permission(self):
        """Redirect unauthorized users"""
        if self.request.user.is_authenticated:
            logger.warning(
                f"Unauthorized staff access attempt by {self.request.user.username} "
                f"to {self.request.path}"
            )
            messages.error(self.request, "You do not have permission to access this page.")
            return redirect('home')
        return redirect('login')


class OfficerRequiredMixin(UserPassesTestMixin):
    """
    Restrict access to officers or staff.
    
    Checks:
    1. User is staff, OR
    2. User has a member_profile and is_officer=True
    
    Usage:
        class ManageAnnouncementsView(OfficerRequiredMixin, ListView):
            ...
    """
    
    def test_func(self):
        """Test if user is officer or staff"""
        if self.request.user.is_staff:
            return True
        
        if hasattr(self.request.user, 'member_profile'):
            return self.request.user.member_profile.is_officer
        
        return False
    
    def handle_no_permission(self):
        """Redirect unauthorized users"""
        if self.request.user.is_authenticated:
            logger.warning(
                f"Unauthorized officer access attempt by {self.request.user.username} "
                f"to {self.request.path}"
            )
            messages.error(self.request, "You do not have permission to access this page.")
            return redirect('home')
        return redirect('login')


class MemberRequiredMixin(LoginRequiredMixin):
    """
    Restrict access to authenticated members only.
    
    This is just an alias for LoginRequiredMixin but with clearer naming
    for member-specific views.
    
    Usage:
        class MemberProfileView(MemberRequiredMixin, DetailView):
            ...
    """
    login_url = 'login'
    redirect_field_name = 'next'


class FormValidMessagesMixin:
    """
    Display form validation errors as Django messages instead of inline.
    
    Useful when you want to show validation errors in a toast/alert
    instead of next to form fields.
    
    Usage:
        class MyFormView(FormValidMessagesMixin, CreateView):
            ...
    """
    
    def form_invalid(self, form):
        """Display form errors as messages"""
        for field, errors in form.errors.items():
            for error in errors:
                # Format field name for display
                field_name = field.replace('_', ' ').title() if field != '__all__' else 'Error'
                messages.error(self.request, f"{field_name}: {error}")
        
        return super().form_invalid(form)


class SuccessMessageMixin:
    """
    Display a success message after form submission.
    
    Set 'success_message' class attribute with {field} placeholders
    that will be filled from the form instance.
    
    Usage:
        class CreateMemberView(SuccessMessageMixin, CreateView):
            success_message = "Member {first_name} {last_name} created successfully!"
            ...
    
    Note: Django's built-in SuccessMessageMixin exists, but this version
    is compatible with our logging approach.
    """
    success_message = None
    
    def form_valid(self, form):
        """Display success message and log action"""
        response = super().form_valid(form)
        
        if self.success_message:
            message = self.success_message.format(**form.cleaned_data)
            messages.success(self.request, message)
            
            # Log the action
            logger.info(
                f"{self.__class__.__name__} executed by {self.request.user.username}: {message}"
            )
        
        return response


class DeleteConfirmationMixin:
    """
    Display a confirmation message when deleting an object.
    
    Usage:
        class DeleteMemberView(DeleteConfirmationMixin, DeleteView):
            model = MemberProfile
            success_url = reverse_lazy('member_roster')
            ...
    """
    
    def delete(self, request, *args, **kwargs):
        """Display confirmation and log deletion"""
        obj = self.get_object()
        obj_str = str(obj)
        
        response = super().delete(request, *args, **kwargs)
        
        messages.success(request, f"Successfully deleted {obj_str}.")
        logger.info(f"{self.__class__.__name__} deleted by {request.user.username}: {obj_str}")
        
        return response


class ListFilterMixin:
    """
    Support filtering and searching in ListView.
    
    Expects 'search_fields' to be defined as a list of model field names.
    Expects 'filter_fields' to be defined as a dict of lookups.
    
    Usage:
        class MemberListView(ListFilterMixin, ListView):
            model = MemberProfile
            search_fields = ['user__first_name', 'user__last_name', 'member_number']
            filter_fields = {'status': 'status'}  # GET param: status=financial
            
            def get_queryset(self):
                # This is called automatically and applies filters
                ...
    """
    search_fields = []
    filter_fields = {}
    
    def get_queryset(self):
        """Apply search and filters to queryset"""
        queryset = super().get_queryset()
        
        # Apply search
        search_query = self.request.GET.get('search', '').strip()
        if search_query and self.search_fields:
            from django.db.models import Q
            q_objects = Q()
            for field in self.search_fields:
                q_objects |= Q(**{f'{field}__icontains': search_query})
            queryset = queryset.filter(q_objects)
        
        # Apply filters
        for get_param, field_lookup in self.filter_fields.items():
            filter_value = self.request.GET.get(get_param, '').strip()
            if filter_value:
                queryset = queryset.filter(**{field_lookup: filter_value})
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """Add search/filter values to template context"""
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        # Add all filter values
        for get_param in self.filter_fields.keys():
            context[f'{get_param}_filter'] = self.request.GET.get(get_param, '')
        return context


class UserFormKwargsMixin:
    """
    Automatically pass request.user to form kwargs.
    
    Useful when forms need access to the current user.
    
    Usage:
        class EditProfileView(UserFormKwargsMixin, UpdateView):
            form_class = EditProfileForm
            ...
    """
    
    def get_form_kwargs(self):
        """Add user to form kwargs"""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class OwnershipRequiredMixin(UserPassesTestMixin):
    """
    Restrict access to object owners or staff.
    
    Expects model to have a 'user' or 'created_by' field.
    
    Usage:
        class EditPhotoView(OwnershipRequiredMixin, UpdateView):
            model = Photo
            # Automatically checks if user owns the photo
            user_field = 'uploaded_by'  # Default: 'user'
            ...
    """
    user_field = 'user'
    
    def test_func(self):
        """Check if user owns object or is staff"""
        obj = self.get_object()
        
        # Staff can always access
        if self.request.user.is_staff:
            return True
        
        # Check ownership
        owner = getattr(obj, self.user_field, None)
        return owner == self.request.user
    
    def handle_no_permission(self):
        """Deny access with message"""
        logger.warning(
            f"Unauthorized ownership access attempt by {self.request.user.username} "
            f"to {self.request.path}"
        )
        messages.error(self.request, "You do not have permission to access this resource.")
        return redirect('home')
