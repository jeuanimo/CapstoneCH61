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
