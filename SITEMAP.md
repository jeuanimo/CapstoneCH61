# Phi Beta Sigma Chapter Website - Sitemap

## Project Overview

This is a comprehensive fraternity chapter management and e-commerce platform built with Django. The site includes public-facing pages, member portal features, officer management tools, financial management, and an integrated boutique shop.

---

## 1. PUBLIC PAGES (No Authentication Required)

Accessible to all visitors without login.

```
Homepage
├── Home Page (/)
├── Chapter Information
│   ├── About Chapter (/about/)
│   ├── Chapter Leadership (/chapter-leadership/)
│   │   └── Shows current officers and leadership team
│   ├── Chapter Programs (/chapter-programs/)
│   │   ├── Bigger Better Business
│   │   │   └── Program photos & details
│   │   ├── Social Action
│   │   │   └── Program photos & details
│   │   ├── Education
│   │   │   └── Program photos & details
│   │   └── Sigma Beta Club
│   │       └── Program photos & details
│   ├── Contact Us (/contact/)
│   └── Events & Service (/events/)
└── Authentication
    ├── Login (/login/)
    ├── Signup (/signup/)
    └── Logout (/logout/)
```

### Public Page Features
- Chapter mission and history
- Officer roster with photos
- Program highlights and photo galleries
- Upcoming events calendar
- Contact form for inquiries
- Public signup/login

---

## 2. MEMBER PORTAL (Login Required)

Protected section for authenticated members.

### Dashboard (/portal/)
- Quick statistics and announcements
- Dues status summary
- Upcoming events
- Recent activity feed

### 2A. COMMUNITY FEATURES

#### Profile Management
```
Profile Management
├── My Profile (view/edit) (/portal/profile/edit/)
├── Member Roster (/portal/roster/)
│   └── Searchable directory of all members
├── Member Profile View (/portal/profile/<username>/)
│   └── View specific member details
└── Leadership Photo Upload (Officers only)
    └── Upload officer profile photos
```

#### Social Features
```
Social & Media
├── Wall Posts (/portal/posts/)
│   ├── Create Post (/portal/posts/create/)
│   ├── My Posts (/portal/posts/my-posts/)
│   ├── Edit Post (/portal/posts/edit/<id>/)
│   ├── Delete Post (/portal/posts/delete/<id>/)
│   └── Like Comments (/portal/comment/<id>/like/)
├── Photo Gallery (/portal/photos/)
│   ├── Upload Photo (/portal/photos/upload/)
│   ├── Photo Details (/portal/photos/<id>/)
│   ├── Edit Photo (/portal/photos/<id>/edit/)
│   ├── Like Photo (/portal/photos/<id>/like/)
│   ├── Delete Photo (/portal/photos/<id>/delete/)
│   └── Create Album (/portal/albums/create/)
└── Event Management (/portal/events/)
    ├── Create Event (/portal/events/create/)
    ├── Edit Event (/portal/events/<id>/edit/)
    ├── Delete Event (/portal/events/<id>/delete/)
    └── RSVP to Event (/portal/events/<id>/rsvp/)
```

### 2B. COMMUNICATIONS

```
Communications Center
├── Announcements (/portal/announcements/)
│   └── View chapter-wide announcements
├── Documents (/portal/documents/)
│   ├── View documents (restricted by status)
│   ├── Create Document (/portal/documents/create/) - Officers
│   ├── Edit Document (/portal/documents/<id>/edit/) - Officers
│   ├── Delete Document (/portal/documents/<id>/delete/) - Officers
│   └── Officer-Only Documents (/portal/documents/officer-only/)
├── Dues Status (/portal/dues/)
│   └── View personal dues balance and history
├── Direct Messages (/portal/messages/)
│   ├── Inbox (/portal/messages/)
│   ├── View Message (/portal/messages/<id>/)
│   ├── Send Message (/portal/messages/send/)
│   └── Send to Specific User (/portal/messages/send/<username>/)
└── Email System (/portal/email/)
    └── Send Announcements to Members (/portal/email/send-members/) - Officers
```

### 2C. OFFICER MANAGEMENT

Restricted to officers (is_staff=True).

#### Leadership Management
```
Leadership Management
├── Add Officer (/leadership/add/)
├── Edit Officer (/leadership/edit/<id>/)
├── Delete Officer (/leadership/delete/<id>/)
└── Upload Leader Photo (/leadership/upload-photo/<id>/)
```

#### Member Management
```
Member Management
├── Member List (/portal/roster/)
├── Create Member (/portal/roster/create/)
├── Edit Member (/portal/roster/edit/<id>/)
├── Delete Member (/portal/roster/delete/<id>/)
├── Import Members (CSV) (/portal/roster/import/)
└── Import Officers (CSV) (/portal/officers/import/)
```

#### Invitation Codes
```
Invitation Management
├── Manage Invitations (/invitations/)
├── Create Invitation Code (/invitations/create/)
├── Delete Invitation (/invitations/delete/<id>/)
└── Generate Member Invitation (/invitations/generate/<id>/)
```

#### Attendance Tracking
```
Attendance Management
├── View Attendance (/portal/attendance/)
├── Manage Attendance (/portal/attendance/manage/)
├── Add Attendance Record (/portal/attendance/add/)
├── Edit Attendance (/portal/attendance/<id>/edit/)
└── Delete Attendance (/portal/attendance/<id>/delete/)
```

#### Member Synchronization
```
HQ Member Sync (Admin)
├── Sync Members from HQ CSV (/portal/sync-members/)
│   └── Auto-marks non-compliant members
│   └── Sends dues reminder emails
│   └── Monitors sync history
└── View Marked Members (/portal/marked-members/)
    └── Tracks members marked for removal
    └── Shows countdown status
```

### 2D. TREASURER / FINANCE MANAGEMENT

Restricted to treasurer/officers with financial permissions.

#### Dues & Payments Management
```
Dues & Payments
├── Dues List (/portal/dues-and-payments/)
├── View Member Dues Summary (/portal/member-dues-summary/)
├── Create Bill (/portal/dues-and-payments/create-bill/)
├── Add Payment (/portal/dues-and-payments/add/)
├── Edit Payment (/portal/dues-and-payments/edit/<id>/)
├── Delete Payment (/portal/dues-and-payments/delete/<id>/)
└── Bulk Delete Payments (/portal/dues-and-payments/bulk-delete/)
```

#### Online Payment (Stripe Integration)
```
Online Payment Processing
├── Configure Stripe (/portal/stripe/config/)
│   └── Add/update Stripe API keys
├── Pay Dues Online (/portal/dues/<id>/pay/)
│   └── Stripe payment form
├── Stripe Webhook (/portal/stripe/webhook/)
│   └── Payment confirmation hooks
├── Payment Success (/portal/payment-success/<id>/)
│   └── Confirmation page
└── Payment Cancelled (/portal/payment-cancelled/<id>/)
    └── Cancellation page
```

### 2E. SMS NOTIFICATION SYSTEM

Reserved for admin/officers with SMS permissions.

```
SMS Notifications (Twilio)
├── Configure SMS (/portal/twilio/config/)
│   └── Add Twilio credentials
├── SMS Preferences (/portal/sms/preferences/)
│   └── Member opt-in/opt-out
├── Send SMS Alert (/portal/sms/send-alert/)
│   └── Broadcast text messages
└── SMS Logs (/portal/sms/logs/)
    └── View delivery history
```

### 2F. EMAIL COMMUNICATION SYSTEM

Reserved for officers.

```
Email System
└── Send Member Emails (/portal/email/send-members/)
    ├── Recipients by group (all/financial/non-financial/officers)
    ├── Compose announcements
    ├── Preview before sending
    └── Auto-sends dues reminders when members marked
```

---

## 3. BOUTIQUE SHOP (E-Commerce)

Public browsing with login required for checkout.

### Shop Frontend (Public)
```
Boutique Shop
├── Shop Home (/boutique/)
│   └── Browse all products
├── Product Details (/boutique/product/<id>/)
│   └── View product info, prices, images
├── Shopping Cart Management (/boutique/cart/)
│   ├── Add to Cart (/boutique/add-to-cart/<id>/)
│   ├── View Cart (/boutique/cart/)
│   ├── Update Item Quantity (/boutique/cart/update/<id>/)
│   └── Remove from Cart (/boutique/cart/remove/<id>/)
├── Checkout Process (/boutique/checkout/)
│   ├── Enter shipping/billing
│   ├── Process Payment (/boutique/payment/<id>/)
│   └── Payment Success (/boutique/payment-success/<id>/)
└── Order History (/boutique/orders/)
    └── View past orders
```

### Shop Administration (Officers/Staff)
```
Shop Admin
├── Import Products (/boutique/admin/import-products/)
│   └── Bulk upload from CSV with images
├── Add Product (/boutique/admin/add-product/)
│   └── Create new product
├── Edit Product (/boutique/admin/edit-product/<id>/)
│   └── Update product details
└── Delete Product (/boutique/admin/delete-product/<id>/)
    └── Remove product from shop
```

---

## ACCESS CONTROL & PERMISSIONS

### Public Access (No Login Required)
- All "/" pages (home, about, contact, events, programs, leadership)
- Login, Signup, Logout
- Boutique shop browsing

### Member Access (Login Required)
- Portal dashboard
- Profile viewing
- Announcements
- Document viewing (if financial status allows)
- Message center
- Photo gallery
- Event details
- Post/comment creation

### Officer Access (is_staff=True)
- All member features +
- Member management (create, edit, delete)
- Leadership management
- Attendance tracking
- Invitation code creation
- Document management
- HQ member sync
- SMS sending
- Email communication
- Shop administration
- Dues/payment viewing

### Treasurer Access
- All officer features +
- Dues & payments detailed management
- Stripe configuration
- Payment processing
- Financial reports
- Member dues summaries

### Staff/Admin Access
- All features
- User administration
- System configuration
- Backup & maintenance

---

## KEY FEATURES BY SECTION

### Member Portal Features
- ✅ Dashboard with quick stats
- ✅ Searchable member directory
- ✅ Wall posts with comments & likes
- ✅ Photo galleries with albums
- ✅ Direct messaging between members
- ✅ Event creation and RSVP tracking
- ✅ Attendance tracking
- ✅ Dues status tracking
- ✅ Document repository with access control

### Financial Features
- ✅ Dues bill creation
- ✅ Payment tracking
- ✅ Stripe online payment integration
- ✅ Member dues summaries
- ✅ Payment confirmation emails
- ✅ Automatic payment reconciliation

### Communication Features
- ✅ Announcements system
- ✅ Direct messaging
- ✅ SMS alerts (Twilio)
- ✅ Email notifications (dues reminders, announcements)
- ✅ Email preview before sending
- ✅ Bulk announcement system

### Leadership Features
- ✅ Officer roster with photos
- ✅ Officer profile management
- ✅ Officer invitation codes
- ✅ Member invitation system

### Boutique Shop Features
- ✅ Product catalog
- ✅ Shopping cart
- ✅ Checkout process
- ✅ Stripe payment
- ✅ Order history
- ✅ Bulk product import (CSV)
- ✅ Product image support

### Member Compliance Features
- ✅ HQ member list synchronization
- ✅ Auto-mark non-compliant members
- ✅ 90-day grace period countdown
- ✅ Document access restriction
- ✅ Email reminders for dues

---

## TOTAL PAGE COUNT

- **Public Pages**: ~10
- **Authentication**: 3
- **Member Portal**: ~40+
  - Dashboard: 1
  - Community: 8
  - Communications: 10
  - Management: 20+
  - Finance: 15+
  - SMS/Email: 6+
- **Boutique**: ~20+
  - Frontend: 10
  - Admin: 10

**Total: 80+ pages/endpoints**

---

## TECHNOLOGY STACK

- **Backend**: Django (Python)
- **Database**: SQLite (development) / PostgreSQL (production)
- **Frontend**: HTML, CSS, Bootstrap
- **Payment**: Stripe API
- **SMS**: Twilio API
- **Email**: Django SMTP, HTML templates

---

## NOTES

- All forms include validation and error handling
- All pages are responsive and mobile-friendly
- Dark mode CSS included throughout
- Email system uses HTML templates with plain-text fallbacks
- SMS system respects member preferences
- Payment system includes confirmation and error handling
- All sensitive operations logged for audit trail
- File uploads (photos, documents, CSV) with validation
