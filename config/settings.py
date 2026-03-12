"""
=============================================================================
DJANGO SETTINGS FOR PHI BETA SIGMA FRATERNITY CHAPTER WEBSITE
=============================================================================

This is the Django configuration file for the Nu Gamma Sigma chapter website.
All settings can be overridden via environment variables in the .env file.

CONFIGURATION SECTIONS:

1. BASIC SETTINGS
   - SECRET_KEY: For session/CSRF security (auto-generated for dev)
   - DEBUG: Set to False for production
   - ALLOWED_HOSTS: Domains allowed to serve this site

2. INSTALLED APPS
   - Django built-in: admin, auth, contenttypes, sessions, messages, staticfiles
   - Third-party: axes (login brute-force protection), django-filters
   - Custom: pages (main application)

3. MIDDLEWARE
   - Security, Session, CSRF, Auth, Messages, Clickjacking protection
   - Axes: Brute-force attack prevention
   - Order matters - don't rearrange without understanding impact

4. TEMPLATES
   - Uses Django template engine with Bootstrap support
   - Context processors: request, auth, messages (for user/messages in templates)

5. DATABASE
   - SQLite for development (db.sqlite3)
   - Can be changed to PostgreSQL for production (see .env)

6. AUTHENTICATION & SECURITY
   - Password validators: Minimum 8 characters, checks against common passwords
   - Axes: Locks account after 5 failed login attempts for 1 hour
   - CSRF protection enabled globally

7. EMAIL CONFIGURATION
   - Console backend for development (prints emails to console)
   - SMTP via Gmail for production (configure in .env)
   - Uses environment variables for sensitive credentials

8. MEDIA & STATIC FILES
   - Static files: CSS, JS, images in /static/ folder
   - Media files: User uploads in /media/ folder
   - Production: Collect static files with 'python manage.py collectstatic'

9. LOGGING
   - Console logging: Development info to terminal
   - File logging: Warnings and errors to django.log (5MB rotating)
   - Security logging: Security events to security.log
   - Axes logging: Login attempt tracking

10. LOGIN/LOGOUT REDIRECTS
    - LOGIN_URL: Redirect unauthenticated users to login page
    - LOGIN_REDIRECT_URL: After login, redirect to home (can be overridden per view)
    - LOGOUT_REDIRECT_URL: After logout, redirect to home

ENVIRONMENT VARIABLES (.env file):
    SECRET_KEY: Django secret key (auto-generated if not provided)
    DEBUG: True/False for debug mode
    ALLOWED_HOSTS: Comma-separated list of allowed domains
    EMAIL_BACKEND: Email service (console for dev, smtp for production)
    EMAIL_HOST: SMTP server address
    EMAIL_PORT: SMTP port (usually 587 for TLS)
    EMAIL_HOST_USER: Email account username
    EMAIL_HOST_PASSWORD: Email account password
    DEFAULT_FROM_EMAIL: Sender email address
    CONTACT_EMAIL: Email for contact form submissions

PRODUCTION CHECKLIST:
    [ ] Set DEBUG = False in .env
    [ ] Set SECRET_KEY in .env (strong, random value)
    [ ] Set ALLOWED_HOSTS to your domain
    [ ] Configure email backend (SMTP credentials)
    [ ] Use PostgreSQL instead of SQLite
    [ ] Enable HTTPS/SSL
    [ ] Set secure cookies (CSRF_COOKIE_SECURE, SESSION_COOKIE_SECURE)

=============================================================================
"""

from pathlib import Path
from decouple import config, Csv
import secrets
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Development-only secret key prefix (never used in production)
DEV_SECRET_KEY_PREFIX = 'django-insecure-dev-'

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# NOTE: For production, always set SECRET_KEY in .env file or environment variables.
# Development will auto-generate a temporary key if not provided.
SECRET_KEY = config('SECRET_KEY', default=None)
if not SECRET_KEY:
    # Auto-generate for development - don't use in production!
    SECRET_KEY = DEV_SECRET_KEY_PREFIX + secrets.token_hex(32)

# SECURITY WARNING: don't run with debug turned on in production!
# Set DEBUG = False in .env for production
DEBUG = config('DEBUG', default=True, cast=bool)

# Comma-separated list of allowed hosts (domains that can serve this app)
# Example: 'example.com,www.example.com,localhost,127.0.0.1'
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1,capstonech61.onrender.com,.onrender.com,ngs1914.org,www.ngs1914.org', cast=Csv())


# ====================== APPLICATION DEFINITION ======================

INSTALLED_APPS = [
    # Django built-in applications
    'django.contrib.admin',              # Admin interface
    'django.contrib.auth',               # User authentication
    'django.contrib.contenttypes',       # Content types for models
    'django.contrib.sessions',           # Session management
    'django.contrib.messages',           # User messages/notifications
    'django.contrib.staticfiles',        # Static file serving
    
    # Third-party applications
    'axes',                              # Brute-force login protection (must be after sessions)
    'cloudinary_storage',                # Cloudinary media storage (production)
    'cloudinary',                        # Cloudinary API
    
    # Custom applications
    'pages',                             # Main application with all views and models
    'django_filters',                    # Filtering for querysets
]

MIDDLEWARE = [
    # Security middleware stack - order matters!
    'pages.middleware.BlockBadPathsMiddleware',                   # Block bot probes FIRST before anything else
    'django.middleware.security.SecurityMiddleware',              # General security headers
    'whitenoise.middleware.WhiteNoiseMiddleware',                 # Serve static files in production
    'django.contrib.sessions.middleware.SessionMiddleware',       # Session support
    'django.middleware.common.CommonMiddleware',                  # Common utilities (URL rewriting)
    'django.middleware.csrf.CsrfViewMiddleware',                 # CSRF token protection
    'django.contrib.auth.middleware.AuthenticationMiddleware',    # User authentication
    'pages.middleware.LastSeenMiddleware',                        # Track member online status
    'pages.middleware.PrivateAreaSecurityHeadersMiddleware',      # Anti-scraping headers for portal
    'pages.middleware.RateLimitMiddleware',                       # Rate limit scraping attempts
    'django.contrib.messages.middleware.MessageMiddleware',       # Messages (alerts/notifications)
    'django.middleware.clickjacking.XFrameOptionsMiddleware',    # Clickjacking protection
    'axes.middleware.AxesMiddleware',                            # Brute-force attack prevention
    'pages.middleware.CookieConsentMiddleware',                   # GDPR cookie consent tracking
    'pages.middleware.AnalyticsMiddleware',                       # DIY analytics - tracks page views
]

# Authentication backends (order matters - tried in sequence)
AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',                       # Axes brute-force protection
    'pages.backends.EmailBackend',                               # Email login support (case-insensitive)
    'pages.backends.CaseInsensitiveModelBackend',                # Username login (case-insensitive)
]

# Root URL configuration
ROOT_URLCONF = 'config.urls'

# Template configuration
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],                         # Custom template directory
        'APP_DIRS': True,                                         # Look for templates in app folders
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',     # Add request object to templates
                'django.contrib.auth.context_processors.auth',    # Add user/auth info to templates
                'django.contrib.messages.context_processors.messages',  # Add messages to templates
                'pages.context_processors.cart_context',          # Add cart info to templates
                'pages.context_processors.site_config_context',   # Add site branding/config to templates
                'pages.context_processors.cookie_consent_context',  # Add GDPR cookie consent to templates
                'pages.context_processors.stripe_availability_context',  # Add Stripe availability check
                'pages.context_processors.unread_messages_context',  # Add unread messages count to templates
            ],
        },
    },
]

# WSGI application for production servers
WSGI_APPLICATION = 'config.wsgi.application'


# ====================== DATABASE CONFIGURATION ======================

# Use DATABASE_URL for production (PostgreSQL on Render)
# Falls back to SQLite for local development
DATABASE_URL = config('DATABASE_URL', default=None)

if DATABASE_URL:
    # Production: Use PostgreSQL from DATABASE_URL
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    # Development: Use SQLite
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# ====================== PASSWORD VALIDATION (OWASP TOP 10 COMPLIANT) ======================

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
        # Prevents passwords too similar to username, email, etc.
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
        # Prevents common passwords like 'password123', '12345678', etc.
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
        # Prevents all-numeric passwords
    },
    {
        # OWASP Password Complexity: uppercase, lowercase, digit, special char, min 12 chars
        'NAME': 'pages.validators.OWASPPasswordValidator',
        'OPTIONS': {
            'min_length': 12,  # OWASP recommends minimum 8, we use 12 for better security
        }
    },
    {
        # Prevent repeating characters (e.g., 'aaaa', '1111')
        'NAME': 'pages.validators.NoRepeatingCharactersValidator',
        'OPTIONS': {
            'max_repeats': 3,  # No more than 3 same characters in a row
        }
    },
    {
        # Prevent sequential characters (e.g., '1234', 'abcd', 'qwerty')
        'NAME': 'pages.validators.NoSequentialCharactersValidator',
        'OPTIONS': {
            'max_sequential': 4,  # No sequences of 4+ characters
        }
    },
]

# ====================== DJANGO AXES (BRUTE FORCE PROTECTION) ======================

AXES_FAILURE_LIMIT = 5                 # Lock account after 5 failed attempts
AXES_COOLOFF_TIME = 1                  # Lockout duration: 1 hour
AXES_RESET_ON_SUCCESS = True           # Reset failed attempts on successful login
AXES_LOCKOUT_TEMPLATE = None           # Use default error message
AXES_LOCKOUT_PARAMETERS = [['username', 'ip_address']]  # Track by username AND IP
AXES_VERBOSE = True                    # Enable detailed logging of attempts
AXES_ENABLE_ADMIN = True               # Allow staff to reset lockouts in Django admin


# ====================== INTERNATIONALIZATION ======================

LANGUAGE_CODE = 'en-us'                # Default language
TIME_ZONE = 'UTC'                      # Timezone for timestamps
USE_I18N = True                        # Enable internationalization
USE_TZ = True                          # Use timezone-aware datetimes


# ====================== STATIC & MEDIA FILES ======================

STATIC_URL = 'static/'                                   # URL for static files
STATIC_ROOT = BASE_DIR / 'staticfiles'                  # Production static files collection location
STATICFILES_DIRS = [BASE_DIR / 'static']                # Development static files directories

# Whitenoise configuration for serving static files in production
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'                                   # URL for media files
MEDIA_ROOT = BASE_DIR / 'media'                         # Location for uploaded user files

# ====================== CLOUDINARY CONFIGURATION ======================
# Use Cloudinary for media storage in production (persistent across deploys)
# Set CLOUDINARY_URL in environment to enable: cloudinary://API_KEY:API_SECRET@CLOUD_NAME

CLOUDINARY_URL = config('CLOUDINARY_URL', default='')

# Only use Cloudinary if URL is properly set (starts with cloudinary://)
if CLOUDINARY_URL and CLOUDINARY_URL.startswith('cloudinary://'):
    # Production: Use Cloudinary for media storage
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
    
    # Parse Cloudinary URL into components
    import re
    cloudinary_match = re.match(r'cloudinary://([^:]+):([^@]+)@(.+)', CLOUDINARY_URL)
    if cloudinary_match:
        CLOUDINARY_STORAGE = {
            'CLOUD_NAME': cloudinary_match.group(3),
            'API_KEY': cloudinary_match.group(1),
            'API_SECRET': cloudinary_match.group(2),
        }
else:
    # Development/No Cloudinary: Use local file storage
    CLOUDINARY_URL = None  # Clear invalid value
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'


# ====================== LOGGING CONFIGURATION ======================

# Console-only logging (works everywhere, Render captures stdout)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {asctime} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',  # Suppress 404 "Not Found" logs - we handle these in BlockBadPathsMiddleware
            'propagate': False,
        },
        'django.security': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'pages': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'axes': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}

# ====================== LOGIN/LOGOUT CONFIGURATION ======================

LOGIN_URL = 'login'                    # Redirect unauthenticated users to login page
LOGIN_REDIRECT_URL = 'home'            # After successful login, redirect to home
LOGOUT_REDIRECT_URL = 'home'           # After logout, redirect to home

# ====================== DEFAULT FIELD CONFIGURATION ======================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'    # Use BigAutoField for primary keys (supports large IDs)

# ====================== EMAIL CONFIGURATION ======================

# Email backend - set via environment variable
# Development: 'django.core.mail.backends.console.EmailBackend' (prints to console)
# Production: 'django.core.mail.backends.smtp.EmailBackend' (sends via SMTP)
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')

# SMTP server configuration (for sending emails)
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')                  # SMTP server address
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)                     # SMTP port (587 for TLS)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)            # Use TLS encryption
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')                      # Email account username
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')              # Email account password

# From/To email addresses
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@nugammasigma.org')  # Default sender email
CONTACT_EMAIL = config('CONTACT_EMAIL', default='contact@ngs1914.org')           # Email for contact form submissions


# ====================== STRIPE PAYMENT CONFIGURATION ======================

# Stripe API keys for payment processing
# Development: Use test keys from https://dashboard.stripe.com/test/apikeys
# Production: Use live keys (keep secret!)
STRIPE_PUBLIC_KEY = config('STRIPE_PUBLIC_KEY', default='')       # Stripe publishable key
STRIPE_SECRET_KEY = config('STRIPE_SECRET_KEY', default='')       # Stripe secret key (keep secret!)
STRIPE_WEBHOOK_SECRET = config('STRIPE_WEBHOOK_SECRET', default='')  # Webhook endpoint secret


# ====================== PRODUCTION SECURITY SETTINGS ======================

# These settings are automatically enabled when DEBUG=False
if not DEBUG:
    # HTTPS/SSL Security
    SECURE_SSL_REDIRECT = True                     # Redirect HTTP to HTTPS
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')  # Trust proxy headers
    USE_X_FORWARDED_HOST = True                    # Trust X-Forwarded-Host header from Render
    
    # Cookie Security
    SESSION_COOKIE_SECURE = True                   # Only send session cookie over HTTPS
    CSRF_COOKIE_SECURE = True                      # Only send CSRF cookie over HTTPS
    
    # HSTS (HTTP Strict Transport Security)
    SECURE_HSTS_SECONDS = 31536000                 # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True          # Apply to subdomains
    SECURE_HSTS_PRELOAD = True                     # Allow browser preloading
    
    # Additional Security Headers
    SECURE_CONTENT_TYPE_NOSNIFF = True             # Prevent MIME-type sniffing
    SECURE_REFERRER_POLICY = 'same-origin'         # Prevent referrer leakage
    SECURE_BROWSER_XSS_FILTER = True               # Enable browser XSS filter
    X_FRAME_OPTIONS = 'DENY'                       # Prevent clickjacking
    
    # CSRF trusted origins for Render.com
    CSRF_TRUSTED_ORIGINS = config(
        'CSRF_TRUSTED_ORIGINS',
        default='',
        cast=Csv()
    )