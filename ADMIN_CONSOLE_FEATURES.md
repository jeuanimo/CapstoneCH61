# Admin Console & Site Configuration Features

## Overview
This document describes the comprehensive admin console features for managing site configuration, chapter history, and related content through the officer portal.

---

## 1. Site Configuration (✅ Completed)

### Expanded Configuration Model
The `SiteConfiguration` model now supports **36 configurable fields** organized into logical categories:

#### Branding (6 fields)
| Field | Description |
|-------|-------------|
| `site_name` | Chapter/site name displayed across the site |
| `chapter_name` | Full chapter name (e.g., "Chi Eta Chapter") |
| `tagline` | Site tagline/motto |
| `logo` | Main site logo |
| `favicon` | Browser tab icon |
| `footer_text` | Custom footer content |

#### Chapter Details (6 fields)
| Field | Description |
|-------|-------------|
| `chapter_president` | Current chapter president name |
| `charter_date` | Chapter founding date |
| `chapter_region` | Regional affiliation |
| `mailing_address` | Official mailing address |
| `city_state` | City and state |
| `service_areas` | Areas of community service |

#### About Content (4 fields)
| Field | Description |
|-------|-------------|
| `about_us_text` | Main about page content |
| `mission_statement` | Chapter mission statement |
| `chapter_legacy` | Historical legacy description |
| `pbs_hq_url` | Link to national headquarters |

#### Contact Information (3 fields)
| Field | Description |
|-------|-------------|
| `contact_email` | Public contact email |
| `phone_number` | Public phone number |
| `meeting_location` | Regular meeting location |
| `meeting_schedule` | Meeting schedule info |

#### SEO Settings (4 fields)
| Field | Description |
|-------|-------------|
| `meta_description` | Search engine description |
| `meta_keywords` | Search keywords |
| `og_image` | Social media share image |

#### Chatbot Settings (3 fields)
| Field | Description |
|-------|-------------|
| `chatbot_enabled` | Enable/disable chatbot |
| `chatbot_welcome_message` | Initial greeting message |
| `chatbot_rate_limit` | Messages per minute limit |

#### Theme Settings (3 fields)
| Field | Description |
|-------|-------------|
| `primary_color` | Primary brand color |
| `secondary_color` | Secondary brand color |
| `dark_mode_default` | Default to dark mode |

#### Feature Toggles (4 fields)
| Field | Description |
|-------|-------------|
| `show_boutique` | Show/hide boutique section |
| `show_events` | Show/hide events section |
| `maintenance_mode` | Enable maintenance mode |
| `maintenance_message` | Maintenance mode message |

### Tabbed Interface
The site configuration page uses a modern tabbed UI for easy navigation:
- **8 organized tabs** matching the field categories above
- **Tab persistence** via localStorage (remembers last active tab)
- **Responsive design** works on mobile devices
- **Dark mode support** throughout

### Access URL
```
/portal/admin/site-configuration/
```

---

## 2. Chapter History Management (✅ Completed)

### Overview
Officers can manage chapter history content through a dedicated admin interface with full CRUD operations.

### Access URL
```
/portal/admin/chapter-history/
```

### Section Types
- Introduction
- Founding Story
- Milestones & Achievements
- Leadership Legacy
- Community Service
- National Connection
- Custom Section

### Features

#### Manual Section Creation
- Title, content (supports HTML), section type
- Display order control
- Active/inactive toggle
- Optional image upload

#### CSV Import
Import multiple sections from CSV files with columns:
- `title` (required)
- `section_type` (default: custom)
- `content` (required)
- `display_order` (default: 0)
- `is_active` (default: true)

#### Document Import (TXT/DOCX)
- **Single Section Mode**: Import entire document as one section
- **Heading Parse Mode** (DOCX only): Automatically creates separate sections from Word document headings (Heading 1, Heading 2, etc.)
- Automatic title extraction from filename if not specified

#### CRUD Operations
| Operation | Description |
|-----------|-------------|
| **Create** | Add new sections manually or via import |
| **Read** | View all sections with metadata |
| **Update** | Edit any section's content and settings |
| **Delete** | Remove individual sections |
| **Duplicate** | Copy a section (created as inactive for review) |
| **Bulk Delete** | Select multiple sections to delete at once |
| **Clear All** | Remove all sections (with double confirmation) |

---

## 3. Backup & Restore System (✅ Completed)

### Overview
Automatic backup system protects against accidental data loss during imports and bulk operations.

### How It Works
1. **Auto-backup triggers**:
   - Before CSV import
   - Before TXT/DOCX document import
   - Before "Clear All" operation

2. **Backup Storage**:
   - Stored in `ChapterHistoryBackup` model
   - JSON serialization of all section data
   - Includes title, content, type, order, active status

3. **Backup Management**:
   - Last 10 backups retained (older auto-deleted)
   - Color-coded by type (blue = import, red = clear)
   - Shows section count and timestamp

### Restore Process
1. View available backups in "Backup & Restore" section
2. Click "Restore" on desired backup
3. Confirm restoration (warns about replacing current data)
4. All current sections replaced with backup data
5. Used backup is deleted after restoration

### Backup Model Fields
| Field | Description |
|-------|-------------|
| `name` | Auto-generated descriptive name |
| `backup_type` | pre_import, pre_clear, or manual |
| `data` | JSON array of section data |
| `section_count` | Number of sections in backup |
| `created_at` | Timestamp |
| `created_by` | User who triggered backup |

---

## 4. Files Modified/Created

### Models
- `pages/models.py`:
  - Extended `SiteConfiguration` with 26 new fields
  - Added `ChapterHistoryBackup` model

### Forms
- `pages/forms.py`:
  - Extended `SiteConfigurationForm`
  - Added `ChapterHistoryDocumentForm`
  - Added `ChapterHistoryCSVForm`

### Views
- `pages/views.py`:
  - `site_configuration()` - Tabbed config editor
  - `manage_chapter_history()` - History CRUD
  - `edit_history_section()` - Section editor
  - `_create_history_backup()` - Backup creation
  - `_handle_history_restore()` - Restore handler
  - `_handle_history_document_import()` - Document parser
  - `_handle_history_csv_import()` - CSV parser
  - `_handle_history_duplicate_section()` - Duplicator
  - `_handle_history_bulk_delete()` - Bulk delete
  - `_handle_history_clear_all()` - Clear all

### Templates
- `templates/pages/portal/site_configuration.html` - Tabbed config UI
- `templates/pages/portal/manage_history.html` - History management
- `templates/pages/portal/edit_history_section.html` - Section editor
- `templates/pages/chapter_history.html` - Public history page
- `templates/pages/about.html` - Uses site_config values
- `templates/pages/home.html` - Uses site_config values
- `templates/base.html` - SEO meta tags from config
- `templates/pages/chatbot_widget.html` - Configurable welcome

### Migrations
- `0029_extend_site_configuration.py` - Site config expansion
- `0030_history_backup_model.py` - Backup model

### Requirements
- `python-docx>=1.1.0` - Word document parsing

---

## 5. Security Features

- **Login Required**: All admin functions require authentication
- **Officer/Staff Check**: Only officers or staff can access
- **CSRF Protection**: All forms use Django CSRF tokens
- **Confirmation Dialogs**: Destructive actions require confirmation
- **Double Confirmation**: Clear All requires two confirmations
- **Automatic Backups**: Data protected before destructive operations

---

## 6. URL Reference

| URL | Purpose | Permission |
|-----|---------|------------|
| `/portal/admin/site-configuration/` | Site settings | Officer/Staff |
| `/portal/admin/chapter-history/` | History management | Officer/Staff |
| `/portal/admin/chapter-history/edit/<id>/` | Edit section | Officer/Staff |
| `/pages/history/` | Public history page | Public |
| `/pages/about/` | About page (uses config) | Public |

---

## 6. Virtual Meetings & Polls (✅ Completed)

### Overview
Multi-platform virtual meeting system with integrated voting/polling functionality. Supports embedded meetings (Zoom) and external platforms (Google Meet, Microsoft Teams, Webex, etc.).

### Access URLs
```
/portal/meetings/                   # Member: View scheduled meetings
/portal/meetings/manage/            # Officer: Manage meetings
/portal/meetings/create/            # Officer: Create new meeting
/portal/zoom-config/                # Officer: Configure Zoom SDK
/portal/polls/                      # Member: View active polls
/portal/polls/manage/               # Officer: Manage polls
```

### Supported Platforms

| Platform | Type | Feature |
|----------|------|---------|
| Zoom (Embedded) | Native | Meeting embedded directly on page with polls sidebar |
| Google Meet | External Link | Opens in new tab, polls remain on site |
| Microsoft Teams | External Link | Opens in new tab, polls remain on site |
| Cisco Webex | External Link | Opens in new tab, polls remain on site |
| Other | External Link | Any meeting URL supported |

### Meeting Model Fields

| Field | Description |
|-------|-------------|
| `title` | Meeting title/name |
| `description` | Meeting agenda/description |
| `platform` | Meeting platform (zoom, google_meet, teams, webex, other) |
| `meeting_number` | Zoom Meeting ID (for embedded Zoom only) |
| `meeting_password` | Meeting password (optional) |
| `meeting_url` | External meeting link (Google Meet, Teams, etc.) |
| `host` | Meeting host (user) |
| `event` | Optional linked Event |
| `scheduled_time` | Date and time of meeting |
| `duration_minutes` | Expected duration |
| `status` | scheduled, in_progress, completed, cancelled |
| `members_only` | Restrict to logged-in members |
| `financial_only` | Restrict to financial members |

### Poll/Voting Model Fields

| Field | Description |
|-------|-------------|
| `title` | Poll question/title |
| `description` | Additional context |
| `poll_type` | yes_no, multiple_choice, single_choice |
| `meeting` | Optional linked meeting |
| `is_anonymous` | Hide voter identities |
| `show_results_during` | Show live results while voting |
| `allow_multiple` | Allow selecting multiple options |
| `max_selections` | Limit selections if multiple allowed |
| `financial_only` | Restrict to financial members |
| `starts_at`, `ends_at` | Voting window |
| `is_active` | Poll visibility |

### Access Control

| Role | Permissions |
|------|-------------|
| **Staff** | Full access: create/edit/delete meetings/polls, configure Zoom |
| **Officers** | Full access: create/edit/delete meetings/polls, configure Zoom |
| **Financial Members** | Join meetings, vote in all polls |
| **Non-Financial Members** | Join non-restricted meetings, vote in non-restricted polls |

### Key Features

#### Meeting Management
- **Create meetings** with any supported platform
- **Platform-aware forms**: Dynamic fields based on selected platform
- **Access restrictions**: Members-only, financial-only options
- **Meeting lifecycle**: scheduled → in_progress → completed
- **Link to events**: Optional association with chapter events

#### Zoom Integration
- **Embedded SDK**: Zoom meetings display directly within the website
- **Signature generation**: Automatic JWT signature for SDK authentication
- **Host controls**: Start/end meeting buttons for hosts
- **SDK Configuration**: Separate admin page for SDK credentials

#### External Platform Support
- **External link button**: Opens Google Meet/Teams/etc. in new tab
- **Platform icons**: Visual identification of meeting platform
- **Persistent polls**: Polls remain accessible while meeting opens externally

#### Polling System
- **Anonymous/recorded voting**: Configurable privacy per poll
- **Live results**: Optional real-time result display
- **Meeting-linked polls**: Associate polls with specific meetings
- **Multiple choice support**: Single or multiple option selection
- **Voting window**: Set start/end times for polls
- **Voter tracking**: View who voted (for non-anonymous polls)

### Templates

| Template | Description |
|----------|-------------|
| `zoom/meeting_list.html` | Public meeting list with platform badges |
| `zoom/manage_meetings.html` | Officer meeting management dashboard |
| `zoom/meeting_form.html` | Create/edit meeting (platform-aware) |
| `zoom/join_meeting.html` | Meeting room (embedded or external) |
| `zoom/zoom_config.html` | Zoom SDK configuration |
| `polls/poll_list.html` | Active polls listing |
| `polls/manage_polls.html` | Officer poll management |
| `polls/poll_form.html` | Create/edit poll with options |
| `polls/view_poll.html` | Vote and view results |
| `polls/poll_voters.html` | View poll participants |

### Zoom SDK Setup

1. **Create Zoom Marketplace App**:
   - Visit [marketplace.zoom.us](https://marketplace.zoom.us)
   - Create a "Meeting SDK" app (not OAuth)
   - Get SDK Key and SDK Secret

2. **Configure in Site**:
   - Navigate to `/portal/zoom-config/`
   - Enter SDK Key and SDK Secret
   - Mark as Active

3. **Create Embedded Meeting**:
   - Create meeting with Platform = "Zoom (Embedded)"
   - Enter the Zoom Meeting ID
   - Optionally enter password

---

## 7. Quick Start Guide

### Configure Site Settings
1. Log in as officer or staff
2. Navigate to Admin Console → Site Configuration
3. Use tabs to navigate between setting categories
4. Update values and click "Save Configuration"

### Manage Chapter History
1. Navigate to Admin Console → Chapter History
2. **Add Content**:
   - Use form to add individual sections, OR
   - Import CSV for bulk sections, OR
   - Import TXT/DOCX documents
3. **Edit Content**: Click edit icon on any section
4. **Delete Content**: Use individual delete, bulk delete, or clear all
5. **Restore**: If needed, restore from automatic backups

### Manage Virtual Meetings
1. Navigate to Meetings MGMT in officer menu
2. **Configure Zoom** (optional): Set up SDK credentials
3. **Create Meeting**:
   - Select platform (Zoom/Google Meet/Teams/etc.)
   - For Zoom: Enter Meeting ID for embedded, or URL for link
   - For others: Enter meeting URL
4. **Start Meeting**: Click play button when ready
5. **Create Polls**: Add polls linked to meetings for live voting

### Import Documents
1. Go to "Import from Document" section
2. Select TXT or DOCX file
3. Enter section title (or leave blank to use filename)
4. Choose section type
5. Select import mode:
   - **Single section**: Entire document as one section
   - **Parse headings**: Split DOCX by Word headings
6. Click "Import Document"

---

## 8. Troubleshooting

| Issue | Solution |
|-------|----------|
| Can't access admin pages | Ensure user is officer or staff |
| DOCX import fails | Install python-docx: `pip install python-docx` |
| Headings not detected | Ensure DOCX uses Word Heading styles |
| Lost data after import | Use Backup & Restore section to revert |
| Settings not saving | Check for validation errors on form |
| Configuration not showing | Run migrations: `python manage.py migrate` |
| Zoom meeting won't load | Verify SDK Key/Secret in Zoom Config |
| "Zoom not configured" error | Go to /portal/zoom-config/ and add credentials |
| Meeting URL validation fails | Ensure full URL including https:// |
| Poll not showing | Check is_active=True and voting window dates |
