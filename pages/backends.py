"""
Custom Authentication Backends for Phi Beta Sigma Chapter Website

This module provides custom authentication backends that extend Django's
default authentication capabilities.

AUTHENTICATION BACKENDS:
1. EmailBackend - Allows users to login with email + password
2. (Default ModelBackend handles username + password)

USAGE:
Users can login with either:
- Username (member_12345) + password
- Email (john.doe@example.com) + password

SECURITY NOTES:
- Email lookups are case-insensitive
- Multiple users with same email will fail authentication (security measure)
- Works with django-axes brute-force protection
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


User = get_user_model()


class EmailBackend(ModelBackend):
    """
    Custom authentication backend that allows users to login with email.
    
    This backend authenticates against the User model using email address
    instead of username. It's used in combination with Django's default
    ModelBackend to allow login with either username OR email.
    
    Example:
        # User can login with either:
        authenticate(request, username='member_12345', password='secret')  # Default
        authenticate(request, username='john@example.com', password='secret')  # This backend
    
    Security:
        - Email lookup is case-insensitive (john@Example.COM works)
        - If multiple users have the same email, authentication fails
        - Inactive users (is_active=False) are rejected
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate user by email address.
        
        Args:
            request: The HTTP request object
            username: Can be either username or email address
            password: The user's password
            **kwargs: Additional keyword arguments
            
        Returns:
            User object if authentication successful, None otherwise
        """
        if username is None or password is None:
            return None
        
        # Check if the username looks like an email (contains @)
        if '@' not in username:
            # Not an email, let the default ModelBackend handle it
            return None
        
        try:
            # Try to find user by email (case-insensitive)
            user = User.objects.get(email__iexact=username)
        except User.DoesNotExist:
            # No user with this email
            # Run the default password hasher to prevent timing attacks
            User().set_password(password)
            return None
        except User.MultipleObjectsReturned:
            # Multiple users with same email - security risk, deny access
            # Log this as it indicates a data integrity issue
            return None
        
        # Check password and user is active
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        
        return None
    
    def get_user(self, user_id):
        """
        Retrieve user by primary key.
        
        Args:
            user_id: The user's primary key
            
        Returns:
            User object if found and active, None otherwise
        """
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
        
        return user if self.user_can_authenticate(user) else None
