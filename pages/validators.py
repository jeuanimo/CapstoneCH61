"""
Custom Password Validators for OWASP Top 10 Compliance

This module provides password validators that enforce OWASP Application Security 
Verification Standard (ASVS) password requirements.

OWASP Password Requirements Implemented:
- Minimum 12 characters (OWASP recommends 8-64, we use 12 for stronger security)
- At least one uppercase letter
- At least one lowercase letter
- At least one digit
- At least one special character
- Not commonly used passwords (handled by Django's CommonPasswordValidator)
- Not similar to user attributes (handled by Django's UserAttributeSimilarityValidator)

References:
- OWASP ASVS v4.0: https://owasp.org/www-project-application-security-verification-standard/
- OWASP Password Guidelines: https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html
"""

import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class OWASPPasswordValidator:
    """
    Validates passwords against OWASP security guidelines.
    
    Enforces:
    - Minimum length of 12 characters
    - At least one uppercase letter (A-Z)
    - At least one lowercase letter (a-z)
    - At least one digit (0-9)
    - At least one special character (!@#$%^&*(),.?":{}|<>)
    
    This validator should be used in combination with Django's built-in validators:
    - UserAttributeSimilarityValidator (prevents passwords similar to username/email)
    - CommonPasswordValidator (prevents common passwords like 'password123')
    """
    
    def __init__(self, min_length=12):
        self.min_length = min_length
    
    def validate(self, password, user=None):
        """
        Validate a password against OWASP complexity requirements.
        
        Args:
            password: The password string to validate
            user: The user object (optional, not used here)
            
        Raises:
            ValidationError: If password doesn't meet requirements
        """
        errors = []
        
        # Check minimum length
        if len(password) < self.min_length:
            errors.append(
                _("Password must be at least %(min_length)d characters long.") % 
                {'min_length': self.min_length}
            )
        
        # Check for uppercase letter
        if not re.search(r'[A-Z]', password):
            errors.append(_("Password must contain at least one uppercase letter (A-Z)."))
        
        # Check for lowercase letter
        if not re.search(r'[a-z]', password):
            errors.append(_("Password must contain at least one lowercase letter (a-z)."))
        
        # Check for digit
        if not re.search(r'\d', password):
            errors.append(_("Password must contain at least one digit (0-9)."))
        
        # Check for special character
        if not re.search(r'[!@#$%^&*(),.?":{}|<>\[\]\\;\'`~_+=/-]', password):
            errors.append(_("Password must contain at least one special character (!@#$%^&*(),.?\":{}|<>)."))
        
        if errors:
            raise ValidationError(errors)
    
    def get_help_text(self):
        """
        Return help text describing the password requirements.
        """
        return _(
            "Your password must be at least %(min_length)d characters long and include: "
            "one uppercase letter, one lowercase letter, one digit, and one special character."
        ) % {'min_length': self.min_length}


class NoRepeatingCharactersValidator:
    """
    Validates that passwords don't contain too many repeating characters.
    
    This prevents passwords like 'AAAAAAaaaa1!' which technically meet
    complexity requirements but are weak.
    """
    
    def __init__(self, max_repeats=3):
        self.max_repeats = max_repeats
    
    def validate(self, password, user=None):
        """
        Check for excessive repeating characters.
        
        Args:
            password: The password string to validate
            user: The user object (optional, not used)
            
        Raises:
            ValidationError: If password has too many repeating characters
        """
        # Check for same character repeated more than max_repeats times
        pattern = r'(.)\1{' + str(self.max_repeats) + r',}'
        if re.search(pattern, password):
            raise ValidationError(
                _("Password cannot contain more than %(max_repeats)d repeating characters in a row.") %
                {'max_repeats': self.max_repeats}
            )
    
    def get_help_text(self):
        """
        Return help text.
        """
        return _(
            "Your password cannot have more than %(max_repeats)d of the same character in a row."
        ) % {'max_repeats': self.max_repeats}


class NoSequentialCharactersValidator:
    """
    Validates that passwords don't contain sequential characters.
    
    Prevents passwords containing sequences like '123456', 'abcdef', or 'qwerty'.
    """
    
    SEQUENCES = [
        '0123456789',                    # Numeric sequence
        'abcdefghijklmnopqrstuvwxyz',   # Alphabetic sequence
        'qwertyuiop',                    # Keyboard row 1
        'asdfghjkl',                     # Keyboard row 2
        'zxcvbnm',                       # Keyboard row 3
    ]
    
    def __init__(self, max_sequential=4):
        self.max_sequential = max_sequential
    
    def validate(self, password, user=None):
        """
        Check for sequential character patterns.
        
        Args:
            password: The password string to validate
            user: The user object (optional, not used)
            
        Raises:
            ValidationError: If password contains sequential characters
        """
        password_lower = password.lower()
        
        for sequence in self.SEQUENCES:
            # Check forward sequences
            for i in range(len(sequence) - self.max_sequential + 1):
                if sequence[i:i + self.max_sequential] in password_lower:
                    raise ValidationError(
                        _("Password cannot contain %(max_sequential)d or more sequential characters "
                          "(like '1234', 'abcd', or 'qwerty').") %
                        {'max_sequential': self.max_sequential}
                    )
            
            # Check reverse sequences
            reversed_seq = sequence[::-1]
            for i in range(len(reversed_seq) - self.max_sequential + 1):
                if reversed_seq[i:i + self.max_sequential] in password_lower:
                    raise ValidationError(
                        _("Password cannot contain %(max_sequential)d or more sequential characters "
                          "(like '4321', 'dcba').") %
                        {'max_sequential': self.max_sequential}
                    )
    
    def get_help_text(self):
        """
        Return help text.
        """
        return _(
            "Your password cannot contain %(max_sequential)d or more sequential characters "
            "(like '1234', 'abcd', or keyboard patterns like 'qwerty')."
        ) % {'max_sequential': self.max_sequential}
