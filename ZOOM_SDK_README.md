# Zoom Meeting SDK Integration

This document describes the Zoom Meeting SDK integration for embedded meetings in the chapter portal.

## Overview

The Zoom Meeting SDK allows members to join meetings directly within the website using Component View. Two modes are supported:

- **Attendee Mode**: Join existing meetings as a participant
- **Host Mode**: Start meetings with full host controls (requires ZAK token)

## Architecture

```
Frontend (Browser)                    Backend (Django)
┌─────────────────────┐              ┌─────────────────────┐
│                     │              │                     │
│  Zoom Meeting SDK   │   HTTPS      │  zoom_service.py    │
│  (Component View)   │◄────────────►│  - JWT signatures   │
│                     │              │  - OAuth tokens     │
│  zoom_test.js       │              │  - ZAK retrieval    │
│  - Join config      │              │                     │
│  - SDK init         │              │  views_zoom_api.py  │
│                     │              │  - API endpoints    │
└─────────────────────┘              └─────────────────────┘
```

## Key Concepts

### Meeting SDK Signature (JWT)
Server-side generated JWT token that authorizes a user to join a meeting. Contains:
- SDK Key
- Meeting Number
- Role (0=attendee, 1=host)
- Timestamps

### ZAK (Zoom Access Key)
Required for hosts to **start** a meeting via the SDK. Without ZAK, hosts can only join as attendees.

- Obtained via Server-to-Server OAuth API
- Unique per Zoom user
- Required starting March 2, 2026 for host mode

## Setup Guide

### 1. Create Zoom Meeting SDK App

1. Go to [Zoom Marketplace](https://marketplace.zoom.us/)
2. Click "Develop" > "Build App"
3. Select "Meeting SDK" app type
4. Note the **SDK Key** and **SDK Secret**

### 2. Create Server-to-Server OAuth App (for Host Mode)

Host mode is optional but recommended for officers who need to start meetings.

1. Go to [Zoom Marketplace](https://marketplace.zoom.us/)
2. Click "Develop" > "Build App"
3. Select "Server-to-Server OAuth"
4. Add scopes: `user:read:admin` (for ZAK token)
5. Note the **Account ID**, **Client ID**, and **Client Secret**

### 3. Configure Django

#### Option A: Environment Variables (Recommended for Production)

Add to `.env` file:

```bash
# Meeting SDK Credentials
ZOOM_MEETING_SDK_KEY=your-sdk-key
ZOOM_MEETING_SDK_SECRET=your-sdk-secret

# Server-to-Server OAuth (for Host Mode)
ZOOM_OAUTH_ACCOUNT_ID=your-account-id
ZOOM_OAUTH_CLIENT_ID=your-oauth-client-id
ZOOM_OAUTH_CLIENT_SECRET=your-oauth-client-secret
```

#### Option B: Database Configuration (Admin Panel)

1. Go to Django Admin > Pages > Zoom Configuration
2. Enter Meeting SDK credentials
3. Enter OAuth credentials (for Host Mode)
4. Set "Is Active" to True

### 4. Run Database Migration

```bash
python manage.py migrate pages
```

## API Endpoints

### POST `/api/zoom/sdk-signature/`
Generate SDK signature for joining a meeting.

**Request:**
```json
{
    "meetingNumber": "123456789",
    "role": 0
}
```

**Response:**
```json
{
    "success": true,
    "signature": "eyJ...",
    "sdkKey": "abc..."
}
```

### POST `/api/zoom/host-zak/`
Get ZAK token for host mode (admin/officer only).

**Request:**
```json
{
    "hostEmail": "host@example.com"
}
```

**Response:**
```json
{
    "success": true,
    "zak": "eyJ..."
}
```

### POST `/api/zoom/join-config/`
Get complete join configuration (signature + optional ZAK).

**Request:**
```json
{
    "meetingNumber": "123456789",
    "password": "optional",
    "displayName": "John Doe",
    "email": "john@example.com",
    "mode": "attendee"  // or "host"
}
```

**Response:**
```json
{
    "success": true,
    "sdkKey": "abc...",
    "signature": "eyJ...",
    "meetingNumber": "123456789",
    "password": "",
    "userName": "John Doe",
    "userEmail": "john@example.com",
    "role": 0,
    "zak": null  // Present if host mode
}
```

### GET `/api/zoom/config-status/`
Check if Zoom SDK is configured.

**Response:**
```json
{
    "success": true,
    "configured": true,
    "has_oauth_credentials": true
}
```

### GET `/zoom/test-join/`
Test page for joining/starting meetings.

## Frontend Integration

### Basic Join Flow (Attendee)

```javascript
// 1. Get join configuration from server
const response = await fetch('/api/zoom/join-config/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
    },
    body: JSON.stringify({
        meetingNumber: '123456789',
        password: 'abc123',
        displayName: 'John Doe',
        email: 'john@example.com',
        mode: 'attendee'
    })
});

const config = await response.json();

// 2. Initialize Zoom SDK
const client = ZoomMtgEmbedded.createClient();
await client.init({
    zoomAppRoot: document.getElementById('zoomContainer'),
    language: 'en-US'
});

// 3. Join the meeting
await client.join({
    sdkKey: config.sdkKey,
    signature: config.signature,
    meetingNumber: config.meetingNumber,
    password: config.password,
    userName: config.userName,
    userEmail: config.userEmail
});
```

### Host Flow (with ZAK)

```javascript
// Same as above, but with mode='host' and include ZAK
const config = await getJoinConfig(meetingNumber, password, name, email, 'host');

await client.join({
    sdkKey: config.sdkKey,
    signature: config.signature,
    meetingNumber: config.meetingNumber,
    password: config.password,
    userName: config.userName,
    userEmail: config.userEmail,
    zak: config.zak  // Required for host to START meeting
});
```

## SDK Resources

Include these scripts in your HTML (Component View):

```html
<script src="https://source.zoom.us/3.1.6/lib/vendor/react.min.js"></script>
<script src="https://source.zoom.us/3.1.6/lib/vendor/react-dom.min.js"></script>
<script src="https://source.zoom.us/3.1.6/lib/vendor/redux.min.js"></script>
<script src="https://source.zoom.us/3.1.6/lib/vendor/redux-thunk.min.js"></script>
<script src="https://source.zoom.us/3.1.6/lib/vendor/lodash.min.js"></script>
<script src="https://source.zoom.us/3.1.6/zoom-meeting-embedded-3.1.6.min.js"></script>
```

## Security Considerations

1. **Never expose secrets in frontend code** - All signature generation happens server-side
2. **CSRF protection** - All POST endpoints require CSRF token
3. **Authentication required** - Users must be logged in
4. **Host mode restricted** - Only admins/officers can request ZAK tokens
5. **Credentials stored securely** - Use environment variables or encrypted database fields

## Troubleshooting

### "Invalid signature" error
- Check that SDK Key and Secret are correct
- Ensure clock is synchronized (JWT uses timestamps)
- Verify meeting number is correct

### "ZAK token required" error
- OAuth credentials not configured
- User email doesn't match a Zoom user
- Server-to-Server OAuth app needs `user:read:admin` scope

### Meeting loads but won't start
- Host mode requires valid ZAK token
- Check that OAuth credentials are configured
- Verify the host email matches a licensed Zoom user

### CORS errors
- SDK must be loaded from allowed origins
- Check Django CORS settings if using different domain

## Files Reference

| File | Purpose |
|------|---------|
| `pages/zoom_service.py` | Core service for signatures, OAuth, ZAK |
| `pages/views_zoom_api.py` | API endpoints |
| `pages/urls.py` | URL routing |
| `templates/pages/portal/zoom/test_join.html` | Test page |
| `pages/models.py` (ZoomConfiguration) | Credential storage |

## Version Information

- **Zoom Meeting SDK**: 3.1.6
- **Integration Style**: Component View
- **Authentication**: Server-side JWT signatures
- **Host Mode**: ZAK via Server-to-Server OAuth
