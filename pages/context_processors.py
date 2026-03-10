"""
Context Processors for Pages App
Provides global template context variables
"""

from django.conf import settings
from .models import Cart, SiteConfiguration, StripeConfiguration


def cart_context(request):
    """
    Add cart information to all templates.
    Returns cart item count for both authenticated and anonymous users.
    """
    cart_count = 0
    
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            cart_count = cart.get_total_items()
        except Cart.DoesNotExist:
            pass
    else:
        # Check for session-based cart for anonymous users
        session_key = request.session.session_key
        if session_key:
            try:
                cart = Cart.objects.get(session_key=session_key, user__isnull=True)
                cart_count = cart.get_total_items()
            except Cart.DoesNotExist:
                pass
    
    return {
        'cart_item_count': cart_count,
    }


def site_config_context(_request):
    """
    Add site configuration to all templates.
    Provides branding info (logos, chapter name, social links, etc.)
    """
    try:
        config = SiteConfiguration.get_config()
        return {
            'site_config': config,
        }
    except Exception:
        # Return empty dict if there's any issue loading config
        return {
            'site_config': None,
        }


def stripe_availability_context(_request):
    """
    Check if Stripe is configured and available for payments.
    Checks both environment variables and database configuration.
    """
    stripe_available = False
    stripe_test_mode = True
    
    # Check environment variables first
    env_public_key = getattr(settings, 'STRIPE_PUBLIC_KEY', '')
    env_secret_key = getattr(settings, 'STRIPE_SECRET_KEY', '')
    
    if env_public_key and env_secret_key:
        stripe_available = True
        stripe_test_mode = env_public_key.startswith('pk_test_')
    else:
        # Check database configuration
        try:
            config = StripeConfiguration.objects.filter(is_active=True).first()
            if config and config.stripe_publishable_key and config.stripe_secret_key:
                stripe_available = True
                stripe_test_mode = config.is_test_mode
        except Exception:
            pass
    
    return {
        'stripe_available': stripe_available,
        'stripe_test_mode': stripe_test_mode,
    }


def cookie_consent_context(request):
    """
    Add cookie consent status to all templates.
    Shows banner for users who haven't given consent.
    """
    return {
        'show_cookie_banner': getattr(request, 'show_cookie_banner', True),
        'cookie_consent': getattr(request, 'cookie_consent', None),
    }