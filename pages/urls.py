"""
=============================================================================
URL ROUTING FOR PHI BETA SIGMA FRATERNITY CHAPTER WEBSITE
=============================================================================

This module defines all URL patterns for the chapter website application.

URL PATTERN ORGANIZATION:

1. PUBLIC PAGES (No authentication required)
   - '': Home page
   - 'about/': Chapter information
   - 'contact/': Contact form
   - 'events/': Event calendar
   - 'chapter-programs/': Programs overview
   - 'programs/[type]/': Individual program pages (business, social action, etc.)
   - 'chapter-leadership/': Leadership roster
   - 'login/', 'logout/', 'signup/': Authentication

2. PROGRAM MANAGEMENT (Photo editing/deletion)
   - 'programs/photo/<id>/edit/': Edit photo caption
   - 'programs/photo/<id>/delete/': Delete photo with confirmation

3. LEADERSHIP MANAGEMENT (Officer only)
   - 'leadership/add/', 'edit/<id>/', 'delete/<id>/': CRUD operations
   - 'leadership/upload-photo/<id>/': Upload leader profile photo
   - 'invitations/': Manage member invitation codes

4. MEMBER PORTAL (Login required)
   - 'portal/': Dashboard with announcements
   - 'portal/profile/': View and edit member profiles
   - 'portal/roster/': View all members (searchable)
   - 'portal/posts/': Create/manage wall posts
   - 'portal/messages/': Direct messaging between members
   - 'portal/announcements/': View chapter-wide announcements
   - 'portal/documents/': View and manage chapter documents
   - 'portal/photos/': Photo galleries and albums
   - 'portal/events/': Create and manage events

5. ATTENDANCE MANAGEMENT (Officer only)
   - 'portal/attendance/manage/': View/filter all attendance
   - 'portal/attendance/add/': Create new attendance record
   - 'portal/attendance/<id>/edit/': Edit attendance details
   - 'portal/attendance/<id>/delete/': Delete attendance record

6. DUES & PAYMENTS MANAGEMENT (Officer/Treasurer only)
   - 'portal/dues-and-payments/': Main dues management dashboard
   - 'portal/dues-and-payments/create-bill/': Create bill for members
   - 'portal/dues-and-payments/add/', 'edit/<id>/', 'delete/<id>/': Payment CRUD
   - 'portal/member-dues-summary/': View member-specific dues balance

7. STRIPE PAYMENT INTEGRATION (Treasurer only)
   - 'portal/stripe/config/': Configure Stripe API keys
   - 'portal/dues/<id>/pay/': Pay dues online via Stripe
   - 'portal/stripe/webhook/': Stripe webhook for payment updates
   - 'portal/payment-success/', 'payment-cancelled/': Payment outcome pages

8. SMS NOTIFICATIONS (Officer/Admin only)
   - 'portal/twilio/config/': Configure Twilio SMS settings
   - 'portal/sms/preferences/': Member SMS opt-in preferences
   - 'portal/sms/send-alert/': Send SMS announcements
   - 'portal/sms/logs/': View SMS delivery logs

9. BOUTIQUE / E-COMMERCE (Public browsing, login for checkout)
   - 'boutique/': Shop homepage
   - 'boutique/product/<id>/': Product detail page
   - 'boutique/add-to-cart/<id>/': Add item to shopping cart
   - 'boutique/cart/': View shopping cart
   - 'boutique/checkout/', 'payment/': Order processing
   - 'boutique/orders/': Order history

10. BOUTIQUE ADMIN (Officer only)
    - 'boutique/admin/import-products/': Bulk import CSV
    - 'boutique/admin/add-product/': Create new product
    - 'boutique/admin/edit-product/<id>/': Edit product details
    - 'boutique/admin/delete-product/<id>/': Delete product

PERMISSION NOTES:
- Public paths: No auth required
- @login_required: Member portal features
- @user_passes_test(is_officer): Officer management features
- @user_passes_test(lambda u: u.is_staff): Admin-only features

NAME CONVENTIONS:
- Snake_case for URL names (used in templates with {% url 'name' %})
- Hierarchical: 'portal_feature_action' structure
- Consistent naming: 'add_', 'edit_', 'delete_', 'view_', 'manage_' prefixes

=============================================================================
"""

from django.urls import path
from . import views

urlpatterns = [
    # PUBLIC PAGES
    path('', views.home_view, name='home'),           # Home page
    path('about/', views.about, name='about'),       # About page
    path('contact/', views.contact, name='contact'),   # Contact page
    path('events/', views.events, name='events'),     # Events & Service page
    path('chapter-programs/', views.chapter_programs, name='chapter_programs'),  # Chapter Programs page
    
    # PROGRAMS WITH PHOTOS
    path('programs/bigger-better-business/', views.program_business, name='program_business'),
    path('programs/social-action/', views.program_social_action, name='program_social_action'),
    path('programs/education/', views.program_education, name='program_education'),
    path('programs/sigma-beta-club/', views.program_sigma_beta, name='program_sigma_beta'),
    
    # PROGRAM PHOTO MANAGEMENT (Officer only)
    path('programs/photo/<int:photo_id>/edit/', views.edit_program_photo, name='edit_program_photo'),
    path('programs/photo/<int:photo_id>/delete/', views.delete_program_photo, name='delete_program_photo'),
    
    # CHAPTER LEADERSHIP
    path('chapter-leadership/', views.chapter_leadership, name='chapter_leadership'),  # Chapter Leadership page
    
    # AUTHENTICATION
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup_view, name='signup'),
    
    # LEADERSHIP MANAGEMENT (Officer only)
    path('leadership/add/', views.add_leadership, name='add_leadership'),
    path('leadership/edit/<int:pk>/', views.edit_leadership, name='edit_leadership'),
    path('leadership/delete/<int:pk>/', views.delete_leadership, name='delete_leadership'),
    path('leadership/upload-photo/<int:pk>/', views.upload_leader_photo, name='upload_leader_photo'),
    
    # INVITATION CODE MANAGEMENT (Officer only)
    path('invitations/', views.manage_invitations, name='manage_invitations'),
    path('invitations/create/', views.create_invitation, name='create_invitation'),
    path('invitations/delete/<int:pk>/', views.delete_invitation, name='delete_invitation'),
    path('invitations/generate/<int:pk>/', views.generate_member_invitation, name='generate_member_invitation'),
    
    # MEMBER PORTAL - MAIN SECTIONS (Login required)
    path('portal/', views.portal_dashboard, name='portal_dashboard'),
    
    # MEMBER ROSTER MANAGEMENT (Officer only)
    path('portal/roster/', views.MemberListView.as_view(), name='member_roster'),
    path('portal/roster/create/', views.MemberCreateView.as_view(), name='create_member'),
    path('portal/roster/edit/<int:pk>/', views.MemberUpdateView.as_view(), name='edit_member'),
    path('portal/roster/delete/<int:pk>/', views.MemberDeleteView.as_view(), name='delete_member'),
    path('portal/roster/import/', views.import_members, name='import_members'),
    path('portal/officers/import/', views.import_officers, name='import_officers'),
    
    # PROFILE AND POST MANAGEMENT (Login required)
    path('portal/profile/edit/', views.edit_own_profile, name='edit_own_profile'),
    path('portal/posts/create/', views.create_post, name='create_post'),
    path('portal/posts/my-posts/', views.my_posts, name='my_posts'),
    path('portal/posts/edit/<int:post_id>/', views.edit_post, name='edit_post'),
    path('portal/posts/delete/<int:post_id>/', views.delete_post, name='delete_post'),
    path('portal/profile/<str:username>/', views.member_profile, name='member_profile'),
    path('portal/comment/<int:comment_id>/like/', views.like_comment, name='like_comment'),
    
    # MEMBER PORTAL - COMMUNICATIONS (Login required)
    path('portal/dues/', views.dues_view, name='dues_view'),
    path('portal/announcements/', views.announcements_view, name='announcements_view'),
    path('portal/documents/', views.documents_view, name='documents_view'),
    path('portal/documents/officer-only/', views.officer_only_documents, name='officer_only_documents'),
    path('portal/messages/', views.messages_inbox, name='messages_inbox'),
    path('portal/messages/<int:message_id>/', views.message_detail, name='message_detail'),
    path('portal/messages/send/', views.send_message, name='send_message'),
    path('portal/messages/send/<str:recipient_username>/', views.send_message, name='send_message_to'),
    
    # ATTENDANCE MANAGEMENT (Officer only)
    path('portal/attendance/', views.attendance_view, name='attendance_view'),
    path('portal/attendance/manage/', views.manage_attendance, name='manage_attendance'),
    path('portal/attendance/add/', views.add_attendance, name='add_attendance'),
    path('portal/attendance/<int:pk>/edit/', views.edit_attendance, name='edit_attendance'),
    path('portal/attendance/<int:pk>/delete/', views.delete_attendance, name='delete_attendance'),
    
    # PHOTO MANAGEMENT (Login required)
    path('portal/photos/', views.photo_gallery, name='photo_gallery'),
    path('portal/photos/upload/', views.upload_photo, name='upload_photo'),
    path('portal/photos/<int:photo_id>/', views.photo_detail, name='photo_detail'),
    path('portal/photos/<int:photo_id>/edit/', views.edit_photo, name='edit_photo'),
    path('portal/photos/<int:photo_id>/like/', views.like_photo, name='like_photo'),
    path('portal/photos/<int:photo_id>/delete/', views.delete_photo, name='delete_photo'),
    path('portal/albums/create/', views.create_album, name='create_album'),
    
    # EVENT & DOCUMENT MANAGEMENT (Login required)
    path('portal/events/create/', views.create_event, name='create_event'),
    path('portal/events/<int:event_id>/edit/', views.edit_event, name='edit_event'),
    path('portal/events/<int:event_id>/delete/', views.delete_event, name='delete_event'),
    path('portal/events/<int:event_id>/rsvp/', views.rsvp_event, name='rsvp_event'),
    path('portal/documents/create/', views.create_document, name='create_document'),
    path('portal/documents/<int:document_id>/edit/', views.edit_document, name='edit_document'),
    path('portal/documents/<int:document_id>/delete/', views.delete_document, name='delete_document'),
    
    # DUES AND PAYMENTS MANAGEMENT (Officer/Treasurer only)
    path('portal/dues-and-payments/', views.DuesPaymentListView.as_view(), name='dues_and_payments'),
    path('portal/dues-and-payments/create-bill/', views.CreateBillView.as_view(), name='create_bill'),
    path('portal/dues-and-payments/add/', views.DuesPaymentCreateView.as_view(), name='add_dues_payment'),
    path('portal/dues-and-payments/edit/<int:pk>/', views.DuesPaymentUpdateView.as_view(), name='edit_dues_payment'),
    path('portal/dues-and-payments/delete/<int:pk>/', views.DuesPaymentDeleteView.as_view(), name='delete_dues_payment'),
    path('portal/dues-and-payments/bulk-delete/', views.bulk_delete_dues_payments, name='bulk_delete_dues_payments'),
    path('portal/member-dues-summary/', views.member_dues_summary, name='member_dues_summary'),
    
    # STRIPE PAYMENT INTEGRATION (Treasurer only)
    path('portal/stripe/config/', views.setup_stripe_config, name='stripe_config'),
    path('portal/dues/<int:payment_id>/pay/', views.pay_dues_online, name='pay_dues_online'),
    path('portal/stripe/webhook/', views.stripe_webhook, name='stripe_webhook'),
    path('portal/payment-success/<int:stripe_payment_id>/', views.payment_success, name='payment_success'),
    path('portal/payment-cancelled/<int:stripe_payment_id>/', views.payment_cancelled, name='payment_cancelled'),
    
    # MEMBER SYNCHRONIZATION (Admin only)
    path('portal/sync-members/', views.sync_members_with_hq, name='sync_members'),
    path('portal/marked-members/', views.view_marked_members, name='view_marked_members'),
    
    # TWILIO SMS INTEGRATION (Admin/Officer only)
    path('portal/twilio/config/', views.setup_twilio_config, name='twilio_config'),
    path('portal/sms/preferences/', views.update_sms_preferences, name='sms_preferences'),
    path('portal/sms/send-alert/', views.send_sms_alert, name='send_sms_alert'),
    path('portal/sms/logs/', views.view_sms_logs, name='view_sms_logs'),
    
    # EMAIL COMMUNICATION (Officer only)
    path('portal/email/send-members/', views.send_member_email, name='send_member_email'),
    
    # BOUTIQUE / SHOP - PUBLIC PAGES
    path('boutique/', views.shop_home, name='shop_home'),
    path('boutique/product/<int:pk>/', views.product_detail, name='product_detail'),
    
    # SHOPPING CART & CHECKOUT (Login required)
    path('boutique/add-to-cart/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('boutique/cart/', views.view_cart, name='view_cart'),
    path('boutique/cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('boutique/cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('boutique/checkout/', views.checkout, name='checkout'),
    path('boutique/payment/<int:order_id>/', views.payment, name='payment'),
    path('boutique/payment-success/<int:order_id>/', views.payment_success, name='payment_success'),
    path('boutique/orders/', views.order_history, name='order_history'),
    
    # BOUTIQUE ADMIN URLS (Officer/Staff only)
    path('boutique/admin/import-products/', views.import_products, name='import_products'),
    path('boutique/admin/add-product/', views.add_product, name='add_product'),
    path('boutique/admin/edit-product/<int:pk>/', views.edit_product, name='edit_product'),
    path('boutique/admin/delete-product/<int:pk>/', views.delete_product, name='delete_product'),
]
