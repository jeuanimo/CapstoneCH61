"""
Custom permission decorators for access control
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import MemberProfile, ChapterLeadership
import logging

logger = logging.getLogger(__name__)


def is_officer_or_staff(user):
    """
    Check if a user is an officer or staff member.
    
    Args:
        user: Django User instance
    
    Returns:
        bool: True if user is staff or has officer member_profile
    """
    return user.is_staff or (hasattr(user, 'member_profile') and user.member_profile.is_officer)


def officer_required(view_func):
    """
    Decorator to restrict view access to chapter officers and staff only.
    Checks if user is in ChapterLeadership with is_active=True or is staff.
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        # Staff always have access
        if request.user.is_staff:
            return view_func(request, *args, **kwargs)
        
        # Check if user is an active officer
        try:
            is_officer = ChapterLeadership.objects.filter(
                email__iexact=request.user.email, 
                is_active=True
            ).exists()
            
            if is_officer:
                return view_func(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error checking officer status for {request.user.username}: {str(e)}")
        
        # Access denied
        logger.warning(f"Officer access denied for user: {request.user.username} to {view_func.__name__}")
        messages.error(request, "You must be a chapter officer to access this page.")
        return redirect('portal_dashboard')
    
    return wrapper


def financial_member_required(view_func):
    """
    Decorator to restrict view access to financial members only.
    Checks if user has MemberProfile with financial or financial_life_member status.
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        # Staff always have access
        if request.user.is_staff:
            return view_func(request, *args, **kwargs)
        
        try:
            member_profile = MemberProfile.objects.get(user=request.user)
            
            # Check if member is financial
            if member_profile.status in ['financial', 'financial_life_member']:
                return view_func(request, *args, **kwargs)
            
            # Access denied - not financial
            logger.warning(
                f"Financial member access denied for user: {request.user.username} "
                f"(status: {member_profile.status}) to {view_func.__name__}"
            )
            messages.error(
                request, 
                "You must be a financial member to access this page. Please update your dues."
            )
            return redirect('dues_view')
            
        except MemberProfile.DoesNotExist:
            logger.warning(f"No member profile found for user: {request.user.username}")
            messages.error(request, "Member profile not found. Please contact an administrator.")
            return redirect('portal_dashboard')
    
    return wrapper


def officer_or_financial_required(view_func):
    """
    Decorator to restrict access to either officers OR financial members.
    More permissive than requiring both.
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        # Staff always have access
        if request.user.is_staff:
            return view_func(request, *args, **kwargs)
        
        # Check if officer
        is_officer = ChapterLeadership.objects.filter(
            email__iexact=request.user.email, 
            is_active=True
        ).exists()
        
        if is_officer:
            return view_func(request, *args, **kwargs)
        
        # Check if financial member
        try:
            member_profile = MemberProfile.objects.get(user=request.user)
            if member_profile.status in ['financial', 'financial_life_member']:
                return view_func(request, *args, **kwargs)
        except MemberProfile.DoesNotExist:
            pass
        
        # Access denied
        logger.warning(
            f"Access denied for user: {request.user.username} "
            f"(not officer or financial) to {view_func.__name__}"
        )
        messages.error(request, "You must be an officer or financial member to access this page.")
        return redirect('portal_dashboard')
    
    return wrapper


def member_profile_required(view_func):
    """
    Decorator to ensure user has a MemberProfile.
    Useful for views that require member-specific data.
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        try:
            member_profile = MemberProfile.objects.get(user=request.user)
            # Attach member_profile to request for convenience
            request.member_profile = member_profile
            return view_func(request, *args, **kwargs)
        except MemberProfile.DoesNotExist:
            logger.warning(f"No member profile found for user: {request.user.username}")
            messages.error(request, "Member profile not found. Please contact an administrator.")
            return redirect('home')
    
    return wrapper
