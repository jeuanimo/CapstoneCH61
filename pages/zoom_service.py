"""
Zoom Meeting SDK Service Module

This module handles all Zoom API interactions including:
- Meeting SDK signature generation (server-side)
- OAuth token management
- ZAK (Zoom Access Key) retrieval for host mode

IMPORTANT ZOOM CONCEPTS:
------------------------
- Role 0 = Attendee/Participant: Can join meetings but not start them
- Role 1 = Host: Can start meetings, requires ZAK token

ZAK (Zoom Access Key):
- Required for host to START a meeting via Meeting SDK
- Must be retrieved from Zoom API using OAuth
- Specific to the host user

Do not use deprecated Zoom Web SDK patterns. Use current Zoom Meeting SDK 
for Web with Component View and server-side signature generation.
"""

import os
import time
import json
import base64
import hmac
import hashlib
import logging
import requests
from datetime import datetime, timedelta
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


class ZoomServiceError(Exception):
    """Custom exception for Zoom service errors."""
    def __init__(self, message, error_code=None, details=None):
        self.message = message
        self.error_code = error_code
        self.details = details
        super().__init__(self.message)


class ZoomService:
    """
    Service class for Zoom Meeting SDK operations.
    
    All secrets are kept server-side. This class handles:
    1. SDK signature generation for Meeting SDK
    2. OAuth access token retrieval
    3. ZAK token retrieval for host mode
    """
    
    # Zoom API endpoints
    ZOOM_OAUTH_TOKEN_URL = "https://zoom.us/oauth/token"
    ZOOM_API_BASE_URL = "https://api.zoom.us/v2"
    
    def __init__(self):
        """
        Initialize Zoom service with credentials from environment or database.
        
        Required environment variables:
        - ZOOM_MEETING_SDK_KEY: Client ID from Meeting SDK app
        - ZOOM_MEETING_SDK_SECRET: Client Secret from Meeting SDK app
        - ZOOM_OAUTH_CLIENT_ID: OAuth app Client ID (can be same as SDK)
        - ZOOM_OAUTH_CLIENT_SECRET: OAuth app Client Secret
        - ZOOM_OAUTH_ACCOUNT_ID: Account ID for Server-to-Server OAuth
        """
        self.sdk_key = os.environ.get('ZOOM_MEETING_SDK_KEY', '')
        self.sdk_secret = os.environ.get('ZOOM_MEETING_SDK_SECRET', '')
        self.oauth_client_id = os.environ.get('ZOOM_OAUTH_CLIENT_ID', '')
        self.oauth_client_secret = os.environ.get('ZOOM_OAUTH_CLIENT_SECRET', '')
        self.oauth_account_id = os.environ.get('ZOOM_OAUTH_ACCOUNT_ID', '')
        
        # Try to load from database if env vars not set
        if not self.sdk_key or not self.sdk_secret:
            self._load_from_database()
    
    def _load_from_database(self):
        """Load Zoom credentials from database configuration."""
        try:
            from .models import ZoomConfiguration
            config = ZoomConfiguration.objects.filter(is_active=True).first()
            if config:
                self.sdk_key = config.sdk_key or self.sdk_key
                self.sdk_secret = config.sdk_secret or self.sdk_secret
                self.oauth_client_id = config.oauth_client_id or self.oauth_client_id
                self.oauth_client_secret = config.oauth_client_secret or self.oauth_client_secret
                self.oauth_account_id = config.oauth_account_id or self.oauth_account_id
        except Exception as e:
            logger.warning(f"Could not load Zoom config from database: {e}")
    
    def _mask_meeting_number(self, meeting_number):
        """Mask meeting number for logging (show only last 4 digits)."""
        num_str = str(meeting_number)
        if len(num_str) > 4:
            return '*' * (len(num_str) - 4) + num_str[-4:]
        return num_str
    
    def _mask_token(self, token, visible_chars=4):
        """Mask token for logging."""
        if not token:
            return 'None'
        if len(token) > visible_chars * 2:
            return token[:visible_chars] + '...' + token[-visible_chars:]
        return '***'
    
    def validate_credentials(self):
        """Validate that required credentials are present."""
        missing = []
        if not self.sdk_key:
            missing.append('ZOOM_MEETING_SDK_KEY')
        if not self.sdk_secret:
            missing.append('ZOOM_MEETING_SDK_SECRET')
        
        if missing:
            raise ZoomServiceError(
                f"Missing required Zoom credentials: {', '.join(missing)}",
                error_code='MISSING_CREDENTIALS'
            )
        return True
    
    def generate_sdk_signature(self, meeting_number, role):
        """
        Generate JWT signature for Zoom Meeting SDK.
        
        This signature is required to authenticate with Zoom Meeting SDK.
        The signature is generated server-side to keep the SDK secret secure.
        
        Args:
            meeting_number (str|int): The Zoom meeting ID
            role (int): 0 for attendee/participant, 1 for host
                - Role 0: User can JOIN an existing meeting
                - Role 1: User can START a meeting (requires ZAK token too)
        
        Returns:
            str: JWT signature for the Meeting SDK
        
        Raises:
            ZoomServiceError: If credentials are missing or generation fails
        """
        self.validate_credentials()
        
        # Clean and validate meeting number
        meeting_number = str(meeting_number).replace(' ', '').replace('-', '')
        if not meeting_number.isdigit():
            raise ZoomServiceError(
                "Invalid meeting number format",
                error_code='INVALID_MEETING_NUMBER'
            )
        
        # Validate role
        if role not in [0, 1]:
            raise ZoomServiceError(
                "Role must be 0 (attendee) or 1 (host)",
                error_code='INVALID_ROLE'
            )
        
        try:
            # Current time and expiration (2 hours)
            iat = int(time.time())
            exp = iat + 60 * 60 * 2  # 2 hours from now
            
            # JWT Header
            header = {
                "alg": "HS256",
                "typ": "JWT"
            }
            
            # JWT Payload - Zoom Meeting SDK specific structure
            payload = {
                "sdkKey": self.sdk_key,
                "appKey": self.sdk_key,  # Some SDK versions use appKey
                "mn": meeting_number,
                "role": role,
                "iat": iat,
                "exp": exp,
                "tokenExp": exp
            }
            
            # Base64url encode (without padding)
            def base64url_encode(data):
                if isinstance(data, str):
                    data = data.encode('utf-8')
                return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')
            
            # Encode header and payload
            header_encoded = base64url_encode(json.dumps(header, separators=(',', ':')))
            payload_encoded = base64url_encode(json.dumps(payload, separators=(',', ':')))
            
            # Create signature
            message = f"{header_encoded}.{payload_encoded}"
            signature = hmac.new(
                self.sdk_secret.encode('utf-8'),
                message.encode('utf-8'),
                hashlib.sha256
            ).digest()
            signature_encoded = base64url_encode(signature)
            
            # Complete JWT
            jwt_token = f"{header_encoded}.{payload_encoded}.{signature_encoded}"
            
            # Log success (without sensitive data)
            logger.info(
                f"SDK signature generated | "
                f"meeting: {self._mask_meeting_number(meeting_number)} | "
                f"role: {'host' if role == 1 else 'attendee'} | "
                f"exp: {datetime.fromtimestamp(exp).isoformat()}"
            )
            
            return jwt_token
            
        except Exception as e:
            logger.error(f"Signature generation failed: {str(e)}")
            raise ZoomServiceError(
                "Failed to generate SDK signature",
                error_code='SIGNATURE_GENERATION_FAILED',
                details=str(e)
            )
    
    def get_oauth_access_token(self):
        """
        Get OAuth access token using Server-to-Server OAuth flow.
        
        This token is used to call Zoom REST APIs (like getting ZAK).
        Tokens are cached to avoid unnecessary API calls.
        
        Returns:
            str: OAuth access token
        
        Raises:
            ZoomServiceError: If token retrieval fails
        """
        # Check cache first
        cache_key = 'zoom_oauth_access_token'
        cached_token = cache.get(cache_key)
        if cached_token:
            logger.debug("Using cached OAuth access token")
            return cached_token
        
        # Validate OAuth credentials
        if not self.oauth_client_id or not self.oauth_client_secret:
            raise ZoomServiceError(
                "OAuth credentials not configured",
                error_code='MISSING_OAUTH_CREDENTIALS'
            )
        
        try:
            # Server-to-Server OAuth token request
            auth_string = base64.b64encode(
                f"{self.oauth_client_id}:{self.oauth_client_secret}".encode()
            ).decode()
            
            headers = {
                "Authorization": f"Basic {auth_string}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            # For Server-to-Server OAuth
            data = {
                "grant_type": "account_credentials",
                "account_id": self.oauth_account_id
            }
            
            response = requests.post(
                self.ZOOM_OAUTH_TOKEN_URL,
                headers=headers,
                data=data,
                timeout=30
            )
            
            if response.status_code != 200:
                logger.error(
                    f"OAuth token request failed | "
                    f"status: {response.status_code} | "
                    f"response: {response.text[:200]}"
                )
                raise ZoomServiceError(
                    "Failed to obtain OAuth access token",
                    error_code='OAUTH_TOKEN_FAILED',
                    details=f"Status: {response.status_code}"
                )
            
            token_data = response.json()
            access_token = token_data.get('access_token')
            expires_in = token_data.get('expires_in', 3600)
            
            if not access_token:
                raise ZoomServiceError(
                    "No access token in OAuth response",
                    error_code='OAUTH_NO_TOKEN'
                )
            
            # Cache token (with 5 minute buffer before expiry)
            cache_timeout = max(expires_in - 300, 60)
            cache.set(cache_key, access_token, cache_timeout)
            
            logger.info(
                f"OAuth access token obtained | "
                f"expires_in: {expires_in}s | "
                f"cached_for: {cache_timeout}s"
            )
            
            return access_token
            
        except requests.RequestException as e:
            logger.error(f"OAuth request failed: {str(e)}")
            raise ZoomServiceError(
                "Network error during OAuth token request",
                error_code='OAUTH_NETWORK_ERROR',
                details=str(e)
            )
    
    def get_host_zak(self, user_id='me'):
        """
        Get ZAK (Zoom Access Key) for the host user.
        
        ZAK is REQUIRED for a host to START a meeting via Meeting SDK.
        Without ZAK, the host can only JOIN as a participant.
        
        The ZAK token:
        - Is specific to a user
        - Expires after some time
        - Must be passed to Meeting SDK for host start
        
        Args:
            user_id (str): Zoom user ID or 'me' for the authenticated user
        
        Returns:
            str: ZAK token for the host
        
        Raises:
            ZoomServiceError: If ZAK retrieval fails
        """
        # Get OAuth token first
        access_token = self.get_oauth_access_token()
        
        try:
            # Call Zoom API to get user's ZAK
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            # Get user's ZAK token
            zak_url = f"{self.ZOOM_API_BASE_URL}/users/{user_id}/token"
            params = {"type": "zak"}
            
            response = requests.get(
                zak_url,
                headers=headers,
                params=params,
                timeout=30
            )
            
            if response.status_code == 401:
                # Clear cached token and retry once
                cache.delete('zoom_oauth_access_token')
                logger.warning("OAuth token expired, retrying...")
                access_token = self.get_oauth_access_token()
                headers["Authorization"] = f"Bearer {access_token}"
                response = requests.get(
                    zak_url,
                    headers=headers,
                    params=params,
                    timeout=30
                )
            
            if response.status_code != 200:
                logger.error(
                    f"ZAK retrieval failed | "
                    f"status: {response.status_code} | "
                    f"user_id: {user_id}"
                )
                raise ZoomServiceError(
                    "Failed to retrieve host ZAK token",
                    error_code='ZAK_RETRIEVAL_FAILED',
                    details=f"Status: {response.status_code}"
                )
            
            zak_data = response.json()
            zak_token = zak_data.get('token')
            
            if not zak_token:
                raise ZoomServiceError(
                    "No ZAK token in API response",
                    error_code='ZAK_NOT_FOUND'
                )
            
            logger.info(
                f"ZAK token retrieved | "
                f"user_id: {user_id} | "
                f"token_preview: {self._mask_token(zak_token)}"
            )
            
            return zak_token
            
        except requests.RequestException as e:
            logger.error(f"ZAK request failed: {str(e)}")
            raise ZoomServiceError(
                "Network error during ZAK retrieval",
                error_code='ZAK_NETWORK_ERROR',
                details=str(e)
            )
    
    def get_join_config(self, meeting_number, password, display_name, email, mode='attendee'):
        """
        Get complete configuration for joining/starting a Zoom meeting.
        
        This is the main method to call from views. It handles:
        - Signature generation with appropriate role
        - ZAK retrieval for host mode
        - Packaging all data needed by the frontend SDK
        
        Args:
            meeting_number (str|int): Zoom meeting ID
            password (str): Meeting password
            display_name (str): User's display name in meeting
            email (str): User's email address
            mode (str): 'attendee' or 'host'
        
        Returns:
            dict: Configuration for Meeting SDK join():
                - sdkKey: Meeting SDK key
                - signature: JWT signature
                - meetingNumber: Cleaned meeting number
                - password: Meeting password
                - userName: Display name
                - userEmail: Email
                - zak: ZAK token (only for host mode)
        
        Raises:
            ZoomServiceError: If configuration generation fails
        """
        # Validate mode
        mode = mode.lower()
        if mode not in ['attendee', 'host']:
            raise ZoomServiceError(
                "Mode must be 'attendee' or 'host'",
                error_code='INVALID_MODE'
            )
        
        # Clean meeting number
        meeting_number = str(meeting_number).replace(' ', '').replace('-', '')
        
        # Determine role based on mode
        # Role 0 = Attendee: Can join meetings
        # Role 1 = Host: Can start meetings (requires ZAK)
        role = 1 if mode == 'host' else 0
        
        # Generate SDK signature
        signature = self.generate_sdk_signature(meeting_number, role)
        
        # Build response
        config = {
            'sdkKey': self.sdk_key,
            'signature': signature,
            'meetingNumber': meeting_number,
            'password': password or '',
            'userName': display_name,
            'userEmail': email,
        }
        
        # For host mode, get ZAK token
        if mode == 'host':
            try:
                zak = self.get_host_zak()
                config['zak'] = zak
            except ZoomServiceError as e:
                logger.error(f"Failed to get ZAK for host mode: {e.message}")
                raise ZoomServiceError(
                    "Host mode requires ZAK token which could not be retrieved. "
                    "Please check OAuth configuration.",
                    error_code='HOST_ZAK_REQUIRED',
                    details=e.details
                )
        
        logger.info(
            f"Join config generated | "
            f"meeting: {self._mask_meeting_number(meeting_number)} | "
            f"mode: {mode} | "
            f"has_zak: {'zak' in config}"
        )
        
        return config


# Singleton instance for convenience
_zoom_service = None

def get_zoom_service():
    """Get or create the Zoom service singleton."""
    global _zoom_service
    if _zoom_service is None:
        _zoom_service = ZoomService()
    return _zoom_service
