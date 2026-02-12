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
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())


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
    
    # Custom applications
    'pages',                             # Main application with all views and models
    'django_filters',                    # Filtering for querysets
]

MIDDLEWARE = [
    # Security middleware stack - order matters!
    'django.middleware.security.SecurityMiddleware',              # General security headers
    'django.contrib.sessions.middleware.SessionMiddleware',       # Session support
    'django.middleware.common.CommonMiddleware',                  # Common utilities (URL rewriting)
    'django.middleware.csrf.CsrfViewMiddleware',                 # CSRF token protection
    'django.contrib.auth.middleware.AuthenticationMiddleware',    # User authentication
    'django.contrib.messages.middleware.MessageMiddleware',       # Messages (alerts/notifications)
    'django.middleware.clickjacking.XFrameOptionsMiddleware',    # Clickjacking protection
    'axes.middleware.AxesMiddleware',                            # Brute-force attack prevention
]

# Authentication backends (order matters - tried in sequence)
AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',                       # Axes brute-force protection
    'django.contrib.auth.backends.ModelBackend',                 # Default Django authentication
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
            ],
        },
    },
]

# WSGI application for production servers
WSGI_APPLICATION = 'config.wsgi.application'


# ====================== DATABASE CONFIGURATION ======================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',                   # SQLite for development
        'NAME': BASE_DIR / 'db.sqlite3',                          # Database file location
    }
}
# Production: Change to PostgreSQL
# 'default': {
#     'ENGINE': 'django.db.backends.postgresql',
#     'NAME': 'chapter_database',
#     'USER': 'chapter_user',
#     'PASSWORD': 'secure_password',
#     'HOST': 'localhost',
#     'PORT': '5432',
# }


# ====================== PASSWORD VALIDATION ======================

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
        # Prevents passwords too similar to username, email, etc.
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,  # Minimum 8 characters required
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
        # Prevents common passwords like 'password123', '12345678', etc.
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
        # Prevents all-numeric passwords
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

MEDIA_URL = '/media/'                                   # URL for media files
MEDIA_ROOT = BASE_DIR / 'media'                         # Location for uploaded user files


# ====================== LOGGING CONFIGURATION ======================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            # Detailed log format with timestamp, module, process, thread
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            # Simple format: Level, time, message
            'format': '{levelname} {asctime} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',   # Only log when DEBUG = False
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',    # Only log when DEBUG = True
        },
    },
    'handlers': {
        'console': {
            # Log to console/terminal
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            # Log warnings and errors to django.log file (rotating)
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'maxBytes': 1024 * 1024 * 5,                  # 5 MB per file
            'backupCount': 5,                             # Keep 5 backup files
            'formatter': 'verbose',
        },
        'security_file': {
            # Log security events (login attempts, attacks) to security.log
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'security.log',
            'maxBytes': 1024 * 1024 * 5,                  # 5 MB per file
            'backupCount': 10,                            # Keep 10 backup files
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            # General Django logging
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.security': {
            # Django security-related logging
            'handlers': ['security_file'],
            'level': 'WARNING',
            'propagate': False,
        },
        'pages': {
            # Application-specific logging
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'axes': {
            # Axes brute-force attempt logging
            'handlers': ['console', 'security_file'],
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
CONTACT_EMAIL = config('CONTACT_EMAIL', default='nugammasigma@example.com')           # Email for contact form submissions


# ====================== STRIPE PAYMENT CONFIGURATION ======================

# Stripe API keys for payment processing
# Development: Use test keys from https://dashboard.stripe.com/test/apikeys
# Production: Use live keys (keep secret!)
STRIPE_PUBLIC_KEY = config('STRIPE_PUBLIC_KEY', default='pk_test_placeholder')       # Stripe publishable key
STRIPE_SECRET_KEY = config('STRIPE_SECRET_KEY', default='sk_test_placeholder')       # Stripe secret key (keep secret!)





# ====================== LOGIN/LOGOUT CONFIGURATION ======================

LOGIN_URL = 'login'                    # Redirect unauthenticated users to login page
LOGIN_REDIRECT_URL = 'home'            # After successful login, redirect to home
LOGOUT_REDIRECT_URL = 'home'           # After logout, redirect to home

# ====================== DEFAULT FIELD CONFIGURATION ======================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'    # Use BigAutoField for primary keys (supports large IDs)

