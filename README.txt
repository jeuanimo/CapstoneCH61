================================================================================
CAPSTONE CH61 PROJECT - SECURITY & DEVELOPMENT GUIDELINES
================================================================================

================================================================================
                        QUICK START - PROJECT SETUP
================================================================================

PREREQUISITES:
--------------
- Python 3.10 or higher
- pip (Python package manager)
- Git
- A text editor or IDE (VS Code recommended)

STEP 1: CLONE THE REPOSITORY
----------------------------
Open a terminal and run:

    git clone https://github.com/YOUR_USERNAME/CapstoneCH61.git
    cd CapstoneCH61

STEP 2: CREATE VIRTUAL ENVIRONMENT
----------------------------------
Create and activate a Python virtual environment:

    # Linux/macOS:
    python3 -m venv venv
    source venv/bin/activate

    # Windows (Command Prompt):
    python -m venv venv
    venv\Scripts\activate

    # Windows (PowerShell):
    python -m venv venv
    .\venv\Scripts\Activate.ps1

You should see (venv) at the beginning of your terminal prompt.

STEP 3: INSTALL DEPENDENCIES
----------------------------
Install all required packages:

    pip install -r requirements.txt

STEP 4: CREATE ENVIRONMENT FILE
-------------------------------
Create a .env file in the project root with your configuration:

    # Linux/macOS:
    touch .env

    # Windows:
    type nul > .env

Add the following content to .env (edit with your values):

    # Django Settings
    SECRET_KEY=your-secret-key-here-generate-a-random-one
    DEBUG=True
    ALLOWED_HOSTS=localhost,127.0.0.1

    # Database (SQLite is default, leave empty for development)
    DATABASE_URL=

    # Stripe Payment Keys (get from https://dashboard.stripe.com/test/apikeys)
    STRIPE_PUBLIC_KEY=pk_test_your_key_here
    STRIPE_SECRET_KEY=sk_test_your_key_here
    STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

    # Twilio SMS (optional - get from https://console.twilio.com)
    TWILIO_ACCOUNT_SID=your_account_sid
    TWILIO_AUTH_TOKEN=your_auth_token
    TWILIO_PHONE_NUMBER=+1234567890

    # Email Settings (optional - for email features)
    EMAIL_HOST=smtp.gmail.com
    EMAIL_PORT=587
    EMAIL_USE_TLS=True
    EMAIL_HOST_USER=your-email@gmail.com
    EMAIL_HOST_PASSWORD=your-app-password

To generate a secure SECRET_KEY, run:

    python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

STEP 5: RUN DATABASE MIGRATIONS
-------------------------------
Set up the database tables:

    python manage.py migrate

STEP 6: CREATE ADMIN SUPERUSER
------------------------------
Create an admin account to access the system:

    python manage.py createsuperuser

Follow the prompts to enter username, email, and password.

STEP 7: COLLECT STATIC FILES (Optional for Development)
-------------------------------------------------------
For production or if static files don't load:

    python manage.py collectstatic

STEP 8: RUN THE DEVELOPMENT SERVER
----------------------------------
Start the Django development server:

    python manage.py runserver

Open your browser and navigate to:
    - Main site: http://127.0.0.1:8000/
    - Admin panel: http://127.0.0.1:8000/admin/

STEP 9: LOGIN AND EXPLORE
-------------------------
1. Go to http://127.0.0.1:8000/admin/
2. Login with your superuser credentials
3. Create member profiles and test the features

================================================================================
                        COMMON COMMANDS REFERENCE
================================================================================

    # Activate virtual environment
    source venv/bin/activate          # Linux/macOS
    venv\Scripts\activate             # Windows

    # Start development server
    python manage.py runserver

    # Run on specific port
    python manage.py runserver 8080

    # Make database migrations after model changes
    python manage.py makemigrations
    python manage.py migrate

    # Create superuser
    python manage.py createsuperuser

    # Collect static files
    python manage.py collectstatic

    # Run tests
    python manage.py test

    # Check for issues
    python manage.py check

    # Security check for production
    python manage.py check --deploy

    # Open Django shell
    python manage.py shell

    # Deactivate virtual environment
    deactivate

================================================================================
                        TROUBLESHOOTING
================================================================================

ISSUE: "ModuleNotFoundError: No module named 'xyz'"
SOLUTION: Make sure virtual environment is activated and run:
    pip install -r requirements.txt

ISSUE: "OperationalError: no such table"
SOLUTION: Run migrations:
    python manage.py migrate

ISSUE: Static files not loading (CSS/images missing)
SOLUTION: Run collectstatic and check STATIC_URL in settings:
    python manage.py collectstatic

ISSUE: "Invalid HTTP_HOST header"
SOLUTION: Add the host to ALLOWED_HOSTS in .env:
    ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com

ISSUE: Stripe payments not working
SOLUTION: Ensure STRIPE_PUBLIC_KEY and STRIPE_SECRET_KEY are set in .env

ISSUE: Email features not working
SOLUTION: Configure EMAIL_* settings in .env with valid SMTP credentials

================================================================================
                        PROJECT STRUCTURE
================================================================================

    CapstoneCH61/
    ├── config/              # Django project settings
    │   ├── settings.py      # Main configuration
    │   ├── urls.py          # URL routing
    │   └── wsgi.py          # WSGI application
    ├── pages/               # Main Django application
    │   ├── models.py        # Database models
    │   ├── views.py         # View functions
    │   ├── forms.py         # Form definitions
    │   ├── urls.py          # App URL routing
    │   └── admin.py         # Admin configuration
    ├── templates/           # HTML templates
    ├── static/              # Static files (CSS, JS, images)
    ├── media/               # User-uploaded files
    ├── logs/                # Application logs
    ├── requirements.txt     # Python dependencies
    ├── manage.py            # Django management script
    ├── .env                 # Environment variables (create this)
    └── README.txt           # This file

================================================================================
                        TECHNOLOGY STACK
================================================================================

    Backend:
    - Django 4.2 (Python web framework)
    - SQLite (development) / PostgreSQL (production)
    - Gunicorn (production WSGI server)

    Frontend:
    - HTML5, CSS3, JavaScript
    - Bootstrap (responsive design)
    - Font Awesome (icons)

    Integrations:
    - Stripe (payment processing)
    - Twilio (SMS notifications)
    - Django SMTP (email)

    Security:
    - django-axes (brute force protection)
    - django-ratelimit (API rate limiting)
    - python-decouple (environment variables)

================================================================================
                        FEATURES
================================================================================

    Public Features:
    - Homepage, About, Contact pages
    - Chapter Leadership roster
    - Chapter Programs with photo galleries
    - Events calendar with ticket purchasing
    - Public chatbot

    Member Portal:
    - Dashboard with statistics
    - Member directory
    - Wall posts with comments/likes
    - Photo gallery with albums
    - Direct messaging
    - Profile management
    - Online dues payment (Stripe)

    Officer Features:
    - Member/Officer CRUD management
    - CSV import (officers, members, products)
    - Invitation code system
    - Attendance tracking
    - Email/SMS communications
    - HQ member synchronization

    Boutique Shop:
    - Product catalog
    - Shopping cart
    - Stripe checkout
    - Order history

================================================================================

PROJECT OVERVIEW:
-----------------
Django-based web application following OWASP Top 10 security standards and
secure coding practices for AI-assisted development.

SECURITY REQUIREMENTS (OWASP Top 10):
--------------------------------------

1. BROKEN ACCESS CONTROL
   - Implement proper authentication and authorization
   - Use Django's built-in permission system
   - Apply @login_required and permission_required decorators
   - Validate user permissions on every request
   - Principle of least privilege

2. CRYPTOGRAPHIC FAILURES
   - NEVER store sensitive data in plain text
   - Use Django's built-in password hashing (PBKDF2)
   - Encrypt sensitive data at rest and in transit
   - Use HTTPS in production (set SECURE_SSL_REDIRECT = True)
   - Secure session cookies (SESSION_COOKIE_SECURE = True)
   - Set CSRF_COOKIE_SECURE = True in production

3. INJECTION ATTACKS
   - ALWAYS use Django ORM (parameterized queries)
   - NEVER concatenate user input into raw SQL
   - Use .values() or .only() to limit query exposure
   - Validate and sanitize ALL user inputs
   - Use Django forms with proper validation

4. INSECURE DESIGN
   - Apply security by design principles
   - Implement rate limiting for API endpoints
   - Use Django's middleware for security headers
   - Plan for security from the start, not as an afterthought

5. SECURITY MISCONFIGURATION
   - Set DEBUG = False in production
   - Keep SECRET_KEY secure (use environment variables)
   - Set ALLOWED_HOSTS appropriately
   - Remove unnecessary apps from INSTALLED_APPS
   - Configure security middleware properly:
     * SecurityMiddleware
     * CsrfViewMiddleware
     * XFrameOptionsMiddleware
   - Regular dependency updates

6. VULNERABLE AND OUTDATED COMPONENTS
   - Keep Django and all packages updated
   - Run: pip list --outdated regularly
   - Review security advisories
   - Use requirements.txt for dependency tracking

7. IDENTIFICATION AND AUTHENTICATION FAILURES
   - Use Django's authentication system
   - Implement strong password requirements
   - Add password complexity validation
   - Implement account lockout after failed attempts
   - Use multi-factor authentication where appropriate
   - Secure password reset mechanisms

8. SOFTWARE AND DATA INTEGRITY FAILURES
   - Verify all dependencies (check package signatures)
   - Use pip freeze > requirements.txt
   - Implement proper logging
   - Validate deserialized data
   - Use Django's signed cookies when needed

9. SECURITY LOGGING AND MONITORING FAILURES
   - Log all authentication attempts
   - Log access control failures
   - Monitor for suspicious activities
   - NEVER log sensitive data (passwords, tokens, etc.)
   - Configure Django logging properly
   - Regular log reviews

10. SERVER-SIDE REQUEST FORGERY (SSRF)
    - Validate and sanitize all URLs
    - Use allowlists for external requests
    - Implement network segmentation
    - Validate redirect URLs

DJANGO-SPECIFIC SECURITY SETTINGS:
-----------------------------------

Development Settings (settings.py):
- DEBUG = True (dev only)
- SECRET_KEY = 'secure-random-key'
- ALLOWED_HOSTS = []

Production Settings Required:
- DEBUG = False
- SECRET_KEY from environment variable
- ALLOWED_HOSTS = ['yourdomain.com']
- SECURE_SSL_REDIRECT = True
- SESSION_COOKIE_SECURE = True
- CSRF_COOKIE_SECURE = True
- SECURE_BROWSER_XSS_FILTER = True
- SECURE_CONTENT_TYPE_NOSNIFF = True
- X_FRAME_OPTIONS = 'DENY'
- SECURE_HSTS_SECONDS = 31536000
- SECURE_HSTS_INCLUDE_SUBDOMAINS = True
- SECURE_HSTS_PRELOAD = True

SECURE CODING PRACTICES:
------------------------

1. Input Validation:
   - Validate ALL user inputs
   - Use Django forms and serializers
   - Implement server-side validation (never trust client-side)
   - Whitelist acceptable inputs

2. Output Encoding:
   - Django templates auto-escape by default
   - Use |safe filter ONLY when absolutely necessary
   - Be cautious with mark_safe()

3. Error Handling:
   - Use custom error pages (404, 500)
   - NEVER expose stack traces in production
   - Log errors securely
   - Provide user-friendly error messages

4. File Uploads:
   - Validate file types and sizes
   - Use FileField with validators
   - Store uploads outside web root when possible
   - Scan uploads for malware if applicable

5. API Security:
   - Use Django REST Framework properly
   - Implement authentication (Token, JWT)
   - Apply rate limiting
   - Use proper CORS configuration
   - Validate all request data

REACT FRONTEND SECURITY (if applicable):
----------------------------------------
- Sanitize user inputs before rendering
- Use Content Security Policy (CSP)
- Avoid dangerouslySetInnerHTML
- Validate data received from API
- Store tokens securely (httpOnly cookies preferred)
- Implement XSS protection

AI DEVELOPMENT GUIDELINES:
--------------------------
- Always request security context at session start
- Follow documented security patterns
- Never bypass security controls for convenience
- Ask for clarification when security implications are unclear
- Implement defense in depth
- Code review all AI-generated code

DEVELOPMENT WORKFLOW:
--------------------
1. Activate virtual environment: source venv/bin/activate
2. Install dependencies: pip install -r requirements.txt
3. Run migrations: python manage.py migrate
4. Create superuser: python manage.py createsuperuser
5. Run server: python manage.py runserver
6. Run tests: python manage.py test
7. Check security: python manage.py check --deploy

PRE-DEPLOYMENT CHECKLIST:
-------------------------
[ ] DEBUG = False
[ ] SECRET_KEY from environment
[ ] ALLOWED_HOSTS configured
[ ] All security middleware enabled
[ ] SSL/TLS certificates configured
[ ] Database credentials secured
[ ] Static files collected
[ ] Migrations applied
[ ] Security headers configured
[ ] CORS properly configured
[ ] Rate limiting implemented
[ ] Logging configured
[ ] Error pages customized
[ ] Dependencies updated
[ ] Security audit completed

REFERENCES:
-----------
- OWASP Top 10: https://owasp.org/www-project-top-ten/
- Django Security: https://docs.djangoproject.com/en/stable/topics/security/
- Security Documents: See /docs folder for detailed guides

================================================================================
IMPORTANT: Review this document at the start of each development session
================================================================================
