"""
Analytics and Privacy Middleware for Django
Implements DIY page view tracking and GDPR cookie consent.
"""

import hashlib
import logging
import re
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)

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
