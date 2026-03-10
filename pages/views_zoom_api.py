"""
Zoom Meeting SDK API Views

These views provide REST API endpoints for the Zoom Meeting SDK integration.
All secrets and token generation happen server-side - never exposed to frontend.

Endpoints:
- POST /api/zoom/sdk-signature/ - Generate SDK signature
- POST /api/zoom/host-zak/ - Get host ZAK token (admin only)
- POST /api/zoom/join-config/ - Get complete join configuration

Do not use deprecated Zoom Web SDK patterns. Use current Zoom Meeting SDK 
for Web with Component View and server-side signature generation.
"""

import json
import logging
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from .zoom_service import get_zoom_service, ZoomServiceError

logger = logging.getLogger(__name__)


def is_admin_or_officer(user):
    """Check if user is staff or has officer permissions."""
    if user.is_staff:
        return True
    if hasattr(user, 'member_profile') and user.member_profile:
        return user.member_profile.is_officer
    return False


def json_error_response(message, error_code=None, status=400):
    """Create a standardized JSON error response."""
    response = {
        'success': False,
        'error': message,
    }
    if error_code:
        response['error_code'] = error_code
    return JsonResponse(response, status=status)


@require_POST
@csrf_protect
@login_required
def zoom_sdk_signature(request):
    """
    Generate Meeting SDK signature.
    
    POST /api/zoom/sdk-signature/
    
    Request JSON:
        - meetingNumber: Zoom meeting ID
        - role: 0 for attendee, 1 for host
    
    Response JSON:
        - success: boolean
        - signature: JWT signature
        - sdkKey: Meeting SDK key
        - meetingNumber: Cleaned meeting number
        - role: Role used for signature
    """
    try:
        # Parse request body
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return json_error_response('Invalid JSON body', 'INVALID_JSON')
        
        # Validate required fields
        meeting_number = data.get('meetingNumber')
        role = data.get('role')
        
        if not meeting_number:
            return json_error_response('Meeting number is required', 'MISSING_MEETING_NUMBER')
        
        if role is None:
            return json_error_response('Role is required (0=attendee, 1=host)', 'MISSING_ROLE')
        
        try:
            role = int(role)
        except (TypeError, ValueError):
            return json_error_response('Role must be 0 or 1', 'INVALID_ROLE')
        
        if role not in [0, 1]:
            return json_error_response('Role must be 0 (attendee) or 1 (host)', 'INVALID_ROLE')
        
        # Host role requires additional permissions
        if role == 1 and not is_admin_or_officer(request.user):
            return json_error_response(
                'Host mode requires admin or officer permissions',
                'UNAUTHORIZED_HOST',
                status=403
            )
        
        # Generate signature
        zoom_service = get_zoom_service()
        signature = zoom_service.generate_sdk_signature(meeting_number, role)
        
        # Clean meeting number for response
        clean_meeting_number = str(meeting_number).replace(' ', '').replace('-', '')
        
        logger.info(
            f"SDK signature generated | "
            f"user: {request.user.username} | "
            f"role: {'host' if role == 1 else 'attendee'}"
        )
        
        return JsonResponse({
            'success': True,
            'signature': signature,
            'sdkKey': zoom_service.sdk_key,
            'meetingNumber': clean_meeting_number,
            'role': role,
        })
        
    except ZoomServiceError as e:
        logger.error(f"Zoom service error: {e.message} | code: {e.error_code}")
        return json_error_response(e.message, e.error_code)
    except Exception as e:
        logger.exception("Unexpected error in sdk_signature endpoint")
        return json_error_response('Internal server error', 'INTERNAL_ERROR', status=500)


@require_POST
@csrf_protect
@login_required
@user_passes_test(is_admin_or_officer)
def zoom_host_zak(request):
    """
    Get host ZAK token.
    
    POST /api/zoom/host-zak/
    
    This endpoint is restricted to admin/officer users only.
    ZAK is required for host to START a meeting via Meeting SDK.
    
    Response JSON:
        - success: boolean
        - zak: ZAK token
    """
    try:
        zoom_service = get_zoom_service()
        zak = zoom_service.get_host_zak()
        
        logger.info(f"ZAK token retrieved | user: {request.user.username}")
        
        return JsonResponse({
            'success': True,
            'zak': zak,
        })
        
    except ZoomServiceError as e:
        logger.error(f"ZAK retrieval error: {e.message} | code: {e.error_code}")
        return json_error_response(e.message, e.error_code)
    except Exception as e:
        logger.exception("Unexpected error in host_zak endpoint")
        return json_error_response('Internal server error', 'INTERNAL_ERROR', status=500)


@require_POST
@csrf_protect
@login_required
def zoom_join_config(request):
    """
    Get complete join configuration for Meeting SDK.
    
    POST /api/zoom/join-config/
    
    Request JSON:
        - meetingNumber: Zoom meeting ID
        - password: Meeting password
        - displayName: User's display name
        - email: User's email
        - mode: 'attendee' or 'host'
    
    Response JSON (attendee mode):
        - success: boolean  
        - sdkKey: Meeting SDK key
        - signature: JWT signature
        - meetingNumber: Cleaned meeting number
        - password: Meeting password
        - userName: Display name
        - userEmail: Email
    
    Response JSON (host mode):
        - All of the above plus:
        - zak: ZAK token for host start
    """
    try:
        # Parse request body
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return json_error_response('Invalid JSON body', 'INVALID_JSON')
        
        # Extract and validate fields
        meeting_number = data.get('meetingNumber')
        password = data.get('password', '')
        display_name = data.get('displayName')
        email = data.get('email')
        mode = data.get('mode', 'attendee').lower()
        
        # Validate required fields
        if not meeting_number:
            return json_error_response('Meeting number is required', 'MISSING_MEETING_NUMBER')
        
        if not display_name:
            return json_error_response('Display name is required', 'MISSING_DISPLAY_NAME')
        
        if not email:
            return json_error_response('Email is required', 'MISSING_EMAIL')
        
        if mode not in ['attendee', 'host']:
            return json_error_response("Mode must be 'attendee' or 'host'", 'INVALID_MODE')
        
        # Host mode requires additional permissions
        if mode == 'host' and not is_admin_or_officer(request.user):
            return json_error_response(
                'Host mode requires admin or officer permissions',
                'UNAUTHORIZED_HOST',
                status=403
            )
        
        # Get join configuration from service
        zoom_service = get_zoom_service()
        config = zoom_service.get_join_config(
            meeting_number=meeting_number,
            password=password,
            display_name=display_name,
            email=email,
            mode=mode
        )
        
        logger.info(
            f"Join config generated | "
            f"user: {request.user.username} | "
            f"mode: {mode}"
        )
        
        return JsonResponse({
            'success': True,
            **config
        })
        
    except ZoomServiceError as e:
        logger.error(f"Join config error: {e.message} | code: {e.error_code}")
        return json_error_response(e.message, e.error_code)
    except Exception as e:
        logger.exception("Unexpected error in join_config endpoint")
        return json_error_response('Internal server error', 'INTERNAL_ERROR', status=500)


@login_required
def zoom_test_join(request):
    """
    Render the Zoom Meeting SDK test page.
    
    GET /zoom/test-join/
    
    This page allows testing of:
    - Attendee join mode
    - Host start mode (with ZAK)
    - Error handling
    """
    # Get user's display name and email
    if hasattr(request.user, 'member_profile') and request.user.member_profile:
        display_name = request.user.member_profile.get_full_name() or request.user.username
    else:
        display_name = request.user.get_full_name() or request.user.username
    
    context = {
        'display_name': display_name,
        'email': request.user.email,
        'is_admin_or_officer': is_admin_or_officer(request.user),
    }
    
    return render(request, 'pages/portal/zoom/test_join.html', context)


@require_GET
@login_required
def zoom_config_status(request):
    """
    Check Zoom configuration status.
    
    GET /api/zoom/config-status/
    
    Response JSON:
        - configured: boolean - whether Zoom is configured
        - has_sdk_credentials: boolean
        - has_oauth_credentials: boolean
    """
    try:
        zoom_service = get_zoom_service()
        
        has_sdk = bool(zoom_service.sdk_key and zoom_service.sdk_secret)
        has_oauth = bool(
            zoom_service.oauth_client_id and 
            zoom_service.oauth_client_secret and 
            zoom_service.oauth_account_id
        )
        
        return JsonResponse({
            'success': True,
            'configured': has_sdk,
            'has_sdk_credentials': has_sdk,
            'has_oauth_credentials': has_oauth,
        })
        
    except Exception as e:
        logger.exception("Error checking Zoom config status")
        return json_error_response('Internal server error', 'INTERNAL_ERROR', status=500)
