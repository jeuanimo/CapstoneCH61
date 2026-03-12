"""
Security, Analytics and Privacy Middleware for Django
Implements bot blocking, page view tracking and GDPR cookie consent.
"""

import hashlib
import logging
import re
from django.http import HttpResponseNotFound
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)

# Constants
NOT_FOUND_MESSAGE = "Not Found"


class BlockBadPathsMiddleware(MiddlewareMixin):
    """
    Middleware to block common scanner/bot probe paths.
    
    Returns 404 (not 403) to give scanners less useful information.
    These paths are commonly probed by automated vulnerability scanners
    looking for WordPress, phpMyAdmin, exposed config files, etc.
    """
    
    # Paths that start with these prefixes are blocked
    BLOCKED_PREFIXES = (
        # WordPress/CMS probes
        "/wp-admin",
        "/wp-login",
        "/wp-includes",
        "/wp-content",
        "/wordpress",
        "/xmlrpc.php",
        "/wp-",
        
        # PHP admin tools
        "/phpmyadmin",
        "/phpMyAdmin",
        "/pma",
        "/myadmin",
        "/mysql",
        "/mysqladmin",
        "/adminer",
        
        # CGI/router exploits
        "/cgi-bin",
        "/cgi/",
        "/HNAP1",
        "/boaform",
        "/GponForm",
        "/goform",
        "/formLogin",
        "/currentsetting.htm",
        
        # Common CMS/framework paths
        "/vendor/",
        "/node_modules/",
        "/telescope/",
        "/elfinder/",
        "/filemanager/",
        "/ckfinder/",
        
        # Shells and backdoors
        "/shell",
        "/c99",
        "/r57",
        "/wso",
        "/alfa",
        "/webshell",
        
        # Config/backup probes
        "/.well-known/security.txt",
        "/backup",
        "/bak/",
        "/old/",
        "/temp/",
        "/tmp/",
        "/test/",
        "/debug/",
        
        # API probes for other platforms
        "/api/v1/",
        "/rest/",
        "/graphql",
        "/actuator",
        "/swagger",
        "/redoc",
    )
    
    # Exact paths that are blocked
    BLOCKED_EXACT = {
        # Config files
        "/.env",
        "/.env.local",
        "/.env.production",
        "/.env.backup",
        "/.git",
        "/.git/config",
        "/.git/HEAD",
        "/.gitignore",
        "/.svn",
        "/.hg",
        "/.htaccess",
        "/.htpasswd",
        "/.DS_Store",
        
        # Package manager files
        "/composer.json",
        "/composer.lock",
        "/package.json",
        "/package-lock.json",
        "/yarn.lock",
        "/Gemfile",
        "/Gemfile.lock",
        "/Pipfile",
        "/Pipfile.lock",
        
        # Build/deploy files (hide from production)
        "/requirements.txt",
        "/docker-compose.yml",
        "/docker-compose.yaml",
        "/Dockerfile",
        "/Makefile",
        "/Vagrantfile",
        
        # PHP installation files
        "/setup.php",
        "/install.php",
        "/config.php",
        "/configuration.php",
        "/info.php",
        "/phpinfo.php",
        "/i.php",
        "/test.php",
        
        # Database dumps
        "/dump.sql",
        "/database.sql",
        "/db.sql",
        "/backup.sql",
        
        # Other sensitive files
        "/web.config",
        "/server.xml",
        "/crossdomain.xml",
        "/clientaccesspolicy.xml",
        "/elmah.axd",
        "/trace.axd",
        "/.aws/credentials",
        "/id_rsa",
        "/id_dsa",
    }
    
    # File extensions that should never be served
    BLOCKED_EXTENSIONS = (
        ".php",
        ".asp",
        ".aspx",
        ".jsp",
        ".cgi",
        ".pl",
        ".py",  # Direct .py file access (Django handles routing)
        ".rb",
        ".sh",
        ".bash",
        ".bak",
        ".old",
        ".orig",
        ".swp",
        ".swo",
        ".log",
        ".sql",
        ".conf",
        ".cfg",
        ".ini",
        ".yml",
        ".yaml",
        ".toml",
        ".env",
    )
    
    def process_request(self, request):
        """Block bad paths before they hit the app."""
        path = request.path.lower()
        original_path = request.path
        
        # Check exact matches
        if original_path in self.BLOCKED_EXACT or path in self.BLOCKED_EXACT:
            logger.warning(f"Blocked probe: {original_path} from {self._get_client_ip(request)}")
            return HttpResponseNotFound(NOT_FOUND_MESSAGE)
        
        # Check prefix matches
        if path.startswith(self.BLOCKED_PREFIXES):
            logger.warning(f"Blocked probe: {original_path} from {self._get_client_ip(request)}")
            return HttpResponseNotFound(NOT_FOUND_MESSAGE)
        
        # Check blocked extensions (but allow static files)
        if not path.startswith('/static/') and not path.startswith('/media/'):
            for ext in self.BLOCKED_EXTENSIONS:
                if path.endswith(ext):
                    logger.warning(f"Blocked probe: {original_path} from {self._get_client_ip(request)}")
                    return HttpResponseNotFound(NOT_FOUND_MESSAGE)
        
        return None
    
    def _get_client_ip(self, request):
        """Get real client IP, handling proxy headers."""
        xff = request.META.get('HTTP_X_FORWARDED_FOR')
        if xff:
            return xff.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', 'unknown')


# Paths to exclude from tracking
EXCLUDED_PATHS = [
    r'^/static/',
    r'^/media/',
    r'^/admin/jsi18n/',
    r'^/favicon\.ico$',
    r'^/__debug__/',
    r'\.map$',
    r'\.css$',
    r'\.js$',
    r'\.png$',
    r'\.jpg$',
    r'\.jpeg$',
    r'\.gif$',
    r'\.svg$',
    r'\.ico$',
    r'\.woff',
    r'\.ttf$',
]

# Bot user agent patterns
BOT_PATTERNS = [
    r'bot', r'crawl', r'spider', r'slurp', r'search',
    r'wget', r'curl', r'python-requests', r'scrapy',
    r'headless', r'phantom', r'selenium',
]


def hash_ip(ip_address):
    """
    One-way hash of IP address for privacy.
    Cannot be reversed to get original IP.
    """
    if not ip_address:
        return ''
    # Add salt to prevent rainbow table attacks
    salt = 'pbs_analytics_salt_2026'
    return hashlib.sha256(f"{salt}{ip_address}".encode()).hexdigest()[:32]


def get_client_ip(request):
    """Get client IP address from request, handling proxies."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', '')
    return ip


def is_bot(user_agent):
    """Check if user agent appears to be a bot."""
    if not user_agent:
        return False
    ua_lower = user_agent.lower()
    return any(re.search(pattern, ua_lower) for pattern in BOT_PATTERNS)


def is_mobile(user_agent):
    """Check if user agent appears to be mobile."""
    if not user_agent:
        return False
    mobile_patterns = [
        r'mobile', r'android', r'iphone', r'ipad', r'ipod',
        r'blackberry', r'windows phone', r'opera mini', r'opera mobi'
    ]
    ua_lower = user_agent.lower()
    return any(re.search(pattern, ua_lower) for pattern in mobile_patterns)


def should_track(path):
    """Check if path should be tracked."""
    return not any(re.search(pattern, path) for pattern in EXCLUDED_PATHS)


class AnalyticsMiddleware(MiddlewareMixin):
    """
    Middleware to track page views for DIY analytics.
    Privacy-respecting: hashes IPs and respects cookie consent.
    """
    
    def process_response(self, request, response):
        """Track page view after response is generated."""
        # Only track GET requests with successful responses
        if request.method != 'GET':
            return response
        
        if response.status_code >= 400:
            return response
        
        # Skip excluded paths
        if not should_track(request.path):
            return response
        
        # Check cookie consent - only track if analytics cookies accepted
        # For now, we'll track essential analytics (page path + timestamp) always
        # but skip detailed tracking (IP, user agent) if no consent
        
        try:
            from pages.models import PageView, CookieConsent
            
            user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]
            is_bot_request = is_bot(user_agent)
            
            # Skip bot tracking to keep data clean
            if is_bot_request:
                return response
            
            # Check consent for detailed analytics
            session_key = request.session.session_key or ''
            has_analytics_consent = False
            
            if session_key:
                try:
                    consent = CookieConsent.objects.get(session_key=session_key)
                    has_analytics_consent = consent.analytics_cookies and consent.consent_given
                except CookieConsent.DoesNotExist:
                    pass
            
            # Create page view record
            page_view = PageView(
                path=request.path[:500],
                method=request.method,
                user=request.user if request.user.is_authenticated else None,
                response_code=response.status_code,
                is_bot=is_bot_request,
                is_mobile=is_mobile(user_agent),
            )
            
            # Only add detailed info if consent given
            if has_analytics_consent:
                page_view.session_key = session_key[:40] if session_key else ''
                page_view.referrer = request.META.get('HTTP_REFERER', '')[:500]
                page_view.user_agent = user_agent
                page_view.ip_hash = hash_ip(get_client_ip(request))
            
            page_view.save()
            
        except Exception as e:
            # Don't let analytics errors break the site
            logger.warning(f"Analytics tracking error: {e}")
        
        return response


class CookieConsentMiddleware(MiddlewareMixin):
    """
    Middleware to check and provide cookie consent status to templates.
    Adds 'cookie_consent' to request for template access.
    Handles session rotation on login by also checking user-linked consent.
    """
    
    def process_request(self, request):
        """Add cookie consent info to request."""
        request.cookie_consent = None
        request.show_cookie_banner = True
        
        # Ensure session exists
        if not request.session.session_key:
            request.session.save()
        
        session_key = request.session.session_key
        
        try:
            from pages.models import CookieConsent
            consent = None
            
            # First, check for user-linked consent (survives session rotation on login)
            if request.user.is_authenticated:
                consent = CookieConsent.objects.filter(
                    user=request.user, 
                    consent_given=True
                ).first()
                
                # If found, update session_key to current session for future lookups
                if consent and consent.session_key != session_key:
                    consent.session_key = session_key
                    consent.save(update_fields=['session_key', 'updated_at'])
            
            # Fall back to session-based consent lookup
            if not consent and session_key:
                try:
                    consent = CookieConsent.objects.get(session_key=session_key)
                    # Link to user if logged in but consent wasn't linked yet
                    if request.user.is_authenticated and consent.user is None:
                        consent.user = request.user
                        consent.save(update_fields=['user', 'updated_at'])
                except CookieConsent.DoesNotExist:
                    pass
            
            if consent:
                request.cookie_consent = consent
                request.show_cookie_banner = not consent.consent_given
                
        except Exception as e:
            logger.debug(f"CookieConsentMiddleware error: {e}")
        
        return None


class LastSeenMiddleware(MiddlewareMixin):
    """
    Middleware to track when authenticated members were last active.
    Updates last_seen field on MemberProfile for online status display.
    """
    
    def process_request(self, request):
        """Update last_seen for authenticated users with member profiles."""
        if request.user.is_authenticated:
            try:
                from django.utils import timezone
                from pages.models import MemberProfile
                
                # Only update every 60 seconds to reduce DB writes
                profile = getattr(request.user, 'member_profile', None)
                if profile:
                    now = timezone.now()
                    # Update if never seen or if more than 60 seconds since last update
                    if not profile.last_seen or (now - profile.last_seen).total_seconds() > 60:
                        MemberProfile.objects.filter(pk=profile.pk).update(last_seen=now)
            except Exception as e:
                logger.debug(f"LastSeenMiddleware error: {e}")
        
        return None


class PrivateAreaSecurityHeadersMiddleware(MiddlewareMixin):
    """
    Middleware to add anti-scraping and privacy headers to private member areas.
    
    Protects against:
    - Search engine indexing of private pages
    - Browser/proxy caching of sensitive data
    - Referrer leakage to external sites
    - Content type sniffing attacks
    
    Private areas include:
    - /portal/ - Member portal
    - /admin/ - Django admin
    - /account/ - Account management
    - /api/ - Any API endpoints
    """
    
    PRIVATE_PREFIXES = (
        '/portal/',
        '/admin/',
        '/account/',
        '/api/',
        '/members/',
    )
    
    def process_request(self, request):
        """Mark request as private area for template context."""
        request.is_private_area = request.path.startswith(self.PRIVATE_PREFIXES)
        return None
    
    def process_response(self, request, response):
        """Add security headers to private area responses."""
        if request.path.startswith(self.PRIVATE_PREFIXES):
            # Prevent search engines from indexing
            response['X-Robots-Tag'] = 'noindex, nofollow, noarchive, nosnippet'
            
            # Prevent caching of sensitive data
            response['Cache-Control'] = 'no-store, no-cache, must-revalidate, private, max-age=0'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
            
            # Prevent referrer leakage to external sites
            response['Referrer-Policy'] = 'same-origin'
            
            # Prevent MIME type sniffing
            response['X-Content-Type-Options'] = 'nosniff'
            
            # Additional security headers
            response['X-Frame-Options'] = 'DENY'  # Prevent embedding in frames
            response['X-Permitted-Cross-Domain-Policies'] = 'none'  # Block Flash/PDF cross-domain
            
        return response


class RateLimitMiddleware(MiddlewareMixin):
    """
    Basic rate limiting middleware to slow down aggressive scrapers.
    Uses session-based tracking for authenticated users.
    
    Note: Login brute-force is handled by django-axes middleware.
    For WAF-level protection, consider Cloudflare in front of Render.
    """
    
    # Rate limits: {path_prefix: (max_requests, time_window_seconds)}
    RATE_LIMITS = {
        # Member data endpoints
        '/portal/members/': (60, 60),           # 60 requests per minute for member directory
        '/portal/contact-directory/': (30, 60), # 30 requests per minute for contacts
        '/api/': (100, 60),                     # 100 API calls per minute
        
        # Auth endpoints (backup to axes)
        '/login': (10, 60),                     # 10 login attempts per minute
        '/accounts/login/': (10, 60),           # 10 login attempts per minute
        '/accounts/password_reset/': (5, 300),  # 5 password resets per 5 minutes
        '/signup': (5, 60),                     # 5 signup attempts per minute
        
        # Export/download endpoints
        '/portal/export': (10, 60),             # 10 exports per minute
        '/portal/download': (20, 60),           # 20 downloads per minute
        
        # Search endpoints
        '/portal/search': (30, 60),             # 30 searches per minute
    }
    
    def _get_rate_key(self, prefix):
        """Generate session key for rate limit tracking."""
        return f'rate_limit_{prefix.replace("/", "_")}'
    
    def _get_user_identifier(self, request):
        """Get user identifier for logging."""
        if request.user.is_authenticated:
            return request.user.username
        return 'anonymous'
    
    def _create_rate_limit_response(self, window):
        """Create 429 rate limit exceeded response."""
        from django.http import HttpResponse
        response = HttpResponse(
            "Too many requests. Please slow down.",
            status=429,
            content_type='text/plain'
        )
        response['Retry-After'] = str(window)
        return response
    
    def _check_rate_limit(self, request, prefix, max_requests, window):
        """Check rate limit for a specific path prefix. Returns response if exceeded."""
        import time
        
        rate_key = self._get_rate_key(prefix)
        
        if rate_key not in request.session:
            request.session[rate_key] = {'count': 0, 'window_start': time.time()}
        
        tracker = request.session[rate_key]
        current_time = time.time()
        
        if current_time - tracker['window_start'] > window:
            tracker['count'] = 0
            tracker['window_start'] = current_time
        
        tracker['count'] += 1
        request.session[rate_key] = tracker
        request.session.modified = True
        
        if tracker['count'] > max_requests:
            user_id = self._get_user_identifier(request)
            logger.warning(f"Rate limit exceeded for {request.path} by {user_id}")
            return self._create_rate_limit_response(window)
        
        return None
    
    def process_request(self, request):
        """Check and enforce rate limits."""
        for prefix, (max_requests, window) in self.RATE_LIMITS.items():
            if request.path.startswith(prefix):
                return self._check_rate_limit(request, prefix, max_requests, window)
        
        return None
