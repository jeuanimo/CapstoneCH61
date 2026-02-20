"""
Context Processors for Pages App
Provides global template context variables
"""

from .models import Cart, SiteConfiguration


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


def site_config_context(request):
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
