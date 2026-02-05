# SonarQube Issues - Analysis and Fixes

## Issues Identified

### 1. **CRITICAL: Hardcoded Secret Key** ⚠️
**Severity:** Critical (Security Hotspot)  
**File:** `config/settings.py` (Line 26)  
**Issue:** SECRET_KEY is hardcoded with a default value in the code.

```python
# CURRENT (INSECURE):
SECRET_KEY = config('SECRET_KEY', default='django-insecure-q+bdk+^nw8te#(ja-nmw&2eidh(_t8jc%-8!=k0gqf7=!#5299')
```

**Risk:** If the `.env` file is not set, the application falls back to a hardcoded key that is visible in the repository.

**Fix:** Remove the default and enforce environment variable requirement.

---

### 2. **High: Integer Parsing without Validation** ⚠️
**Severity:** High (Code Smell)  
**File:** `pages/views.py` (Lines 106-107)  
**Issue:** Direct `int()` conversion of user input without error handling.

```python
# CURRENT (VULNERABLE):
year = int(request.GET.get('year', now.year))
month = int(request.GET.get('month', now.month))
```

**Risk:** Invalid integer values will cause a `ValueError` exception, leading to a 500 error.

**Fix:** Add try-except or use validation with default fallback.

---

### 3. **High: Open Redirect Vulnerability** ⚠️
**Severity:** High (Security Hotspot)  
**File:** `pages/views.py` (Line 352)  
**Issue:** The `next` parameter is not validated before redirect.

```python
# CURRENT (VULNERABLE):
next_url = request.GET.get('next', 'home')
```

**Risk:** An attacker can redirect users to malicious external websites (e.g., `?next=https://evil.com`).

**Fix:** Validate the redirect URL to ensure it's internal.

---

### 4. **Medium: Logger Configuration** ⚠️
**Severity:** Medium (Code Smell)  
**File:** `pages/views.py` (Line 75)  
**Issue:** Logger is defined after imports but before usage.

**Current:** Works but not ideal practice.

**Fix:** Define logger at the module level immediately after imports.

---

## Recommended Fixes (in order of priority)

### Fix #1: Remove Hardcoded SECRET_KEY Default
**File:** `config/settings.py`

Change this:
```python
SECRET_KEY = config('SECRET_KEY', default='django-insecure-q+bdk+^nw8te#(ja-nmw&2eidh(_t8jc%-8!=k0gqf7=!#5299')
```

To this:
```python
SECRET_KEY = config('SECRET_KEY')  # No default - must be in .env
```

---

### Fix #2: Add Safe Integer Parsing
**File:** `pages/views.py` (Lines 106-107)

Change this:
```python
year = int(request.GET.get('year', now.year))
month = int(request.GET.get('month', now.month))
```

To this:
```python
try:
    year = int(request.GET.get('year', now.year))
    month = int(request.GET.get('month', now.month))
    # Validate ranges
    if not (1 <= month <= 12):
        month = now.month
    if year < 1900 or year > 2100:
        year = now.year
except (ValueError, TypeError):
    year = now.year
    month = now.month
```

---

### Fix #3: Add Redirect Validation
**File:** `pages/views.py` (Line 352)

Add this helper function:
```python
from django.http import QueryDict
from urllib.parse import urlparse

def is_safe_redirect_url(url, allowed_hosts=None):
    """
    Check if the provided URL is safe for redirect.
    Only allows relative URLs or same-origin URLs.
    """
    if not url:
        return False
    
    # Parse the URL
    parsed = urlparse(url)
    
    # Only allow relative URLs (no scheme or netloc)
    if parsed.scheme or parsed.netloc:
        return False
    
    # Prevent protocol-relative URLs
    if url.startswith('//'):
        return False
    
    return True
```

Then change:
```python
next_url = request.GET.get('next', 'home')
```

To:
```python
next_url = request.GET.get('next', 'home')
if not is_safe_redirect_url(next_url):
    next_url = 'home'
```

---

## Additional Recommendations

### 1. Add SECURE_REDIRECT_HOST Setting
**File:** `config/settings.py`

Add to settings:
```python
SECURE_REDIRECT_HOST = config('SECURE_REDIRECT_HOST', default='localhost:8000')
```

### 2. Enable Django Security Middleware Settings
**File:** `config/settings.py`

Ensure these are set (for production):
```python
# Production security settings
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=False, cast=bool)
SECURE_HSTS_SECONDS = config('SECURE_HSTS_SECONDS', default=0, cast=int)
SECURE_HSTS_INCLUDE_SUBDOMAINS = config('SECURE_HSTS_INCLUDE_SUBDOMAINS', default=False, cast=bool)
SECURE_HSTS_PRELOAD = config('SECURE_HSTS_PRELOAD', default=False, cast=bool)
CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default=False, cast=bool)
SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=False, cast=bool)
```

### 3. Validate User Input in Contact Form
Already using Django forms which handle validation, but ensure:
- Email validation is enabled (Django does this by default)
- Message length is reasonable (add max_length to form field)

### 4. Add Request Parameter Validation
Create a utility module for common validations:

```python
# pages/validators.py
from django.core.exceptions import ValidationError

def validate_year(year):
    """Validate year is within reasonable range"""
    try:
        year_int = int(year)
        if not (1900 <= year_int <= 2100):
            raise ValidationError("Year must be between 1900 and 2100")
        return year_int
    except (ValueError, TypeError):
        raise ValidationError("Year must be a valid integer")

def validate_month(month):
    """Validate month is between 1 and 12"""
    try:
        month_int = int(month)
        if not (1 <= month_int <= 12):
            raise ValidationError("Month must be between 1 and 12")
        return month_int
    except (ValueError, TypeError):
        raise ValidationError("Month must be a valid integer")
```

---

## Summary of Changes

| Issue | Severity | File | Line(s) | Status |
|-------|----------|------|---------|--------|
| Hardcoded SECRET_KEY | CRITICAL | config/settings.py | 26 | Ready to fix |
| Integer parsing without validation | HIGH | pages/views.py | 106-107 | Ready to fix |
| Open redirect vulnerability | HIGH | pages/views.py | 352 | Ready to fix |
| Logger definition placement | MEDIUM | pages/views.py | 75 | Low priority |

---

## Implementation Priority

1. **First:** Fix hardcoded SECRET_KEY (CRITICAL)
2. **Second:** Add integer validation (HIGH)
3. **Third:** Add redirect validation (HIGH)
4. **Fourth:** Reorganize logger definition (MEDIUM)
5. **Fifth:** Add production security settings (MEDIUM)

---

## Testing Recommendations

After fixes:
1. Test calendar view with invalid year/month values: `/events/?year=abc&month=13`
2. Test login redirect with external URL: `/login/?next=https://google.com`
3. Test with .env file missing to verify SECRET_KEY handling
4. Run SonarQube analysis again to verify fixes

