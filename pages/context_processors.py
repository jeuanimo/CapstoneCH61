"""
Context Processors for Pages App
Provides global template context variables
"""

from django.conf import settings
# Lazy imports moved inside functions to prevent import errors


def cart_context(request):
    """
    Add cart information to all templates.
    Returns cart item count for both authenticated and anonymous users.
    """
    cart_count = 0
    
    try:
        from .models import Cart
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
    except Exception:
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
        from .models import SiteConfiguration
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
    
    try:
        # Check environment variables first
        env_public_key = getattr(settings, 'STRIPE_PUBLIC_KEY', '')
        env_secret_key = getattr(settings, 'STRIPE_SECRET_KEY', '')
        
        if env_public_key and env_secret_key:
            stripe_available = True
            stripe_test_mode = env_public_key.startswith('pk_test_')
        else:
            # Check database configuration
            from .models import StripeConfiguration
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
    Shows banner if user hasn't given consent yet.
    """
    return {
        'show_cookie_banner': getattr(request, 'show_cookie_banner', True),
        'cookie_consent': getattr(request, 'cookie_consent', None),
    }


def unread_messages_context(request):
    """
    Add unread message count to all templates.
    Shows notification badge for authenticated users.
    """
    unread_count = 0
    
    if request.user.is_authenticated:
        try:
            from .models import Message
            unread_count = Message.objects.filter(
                recipient=request.user,
                is_read=False
            ).exclude(status='DE').count()
        except Exception:
            pass
    
    return {
        'unread_messages_count': unread_count,
    }