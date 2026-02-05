from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),           # Home page
    path('about/', views.about, name='about'),       # About page
    path('contact/', views.contact, name='contact'),   # Contact page
    path('events/', views.events, name='events'),     # Events & Service page
    path('chapter-programs/', views.chapter_programs, name='chapter_programs'),  # Chapter Programs page
    path('programs/bigger-better-business/', views.program_business, name='program_business'),
    path('programs/social-action/', views.program_social_action, name='program_social_action'),
    path('programs/education/', views.program_education, name='program_education'),
    path('programs/sigma-beta-club/', views.program_sigma_beta, name='program_sigma_beta'),
    path('programs/photo/<int:photo_id>/edit/', views.edit_program_photo, name='edit_program_photo'),
    path('programs/photo/<int:photo_id>/delete/', views.delete_program_photo, name='delete_program_photo'),
    path('chapter-leadership/', views.chapter_leadership, name='chapter_leadership'),  # Chapter Leadership page
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup_view, name='signup'),
    path('leadership/add/', views.add_leadership, name='add_leadership'),
    path('leadership/edit/<int:pk>/', views.edit_leadership, name='edit_leadership'),
    path('leadership/delete/<int:pk>/', views.delete_leadership, name='delete_leadership'),
    path('leadership/upload-photo/<int:pk>/', views.upload_leader_photo, name='upload_leader_photo'),
    
    # Invitation Code Management
    path('invitations/', views.manage_invitations, name='manage_invitations'),
    path('invitations/create/', views.create_invitation, name='create_invitation'),
    path('invitations/delete/<int:pk>/', views.delete_invitation, name='delete_invitation'),
    path('invitations/generate/<int:pk>/', views.generate_member_invitation, name='generate_member_invitation'),
    
    # Member Portal URLs
    path('portal/', views.portal_dashboard, name='portal_dashboard'),
    path('portal/roster/', views.member_roster, name='member_roster'),
    path('portal/roster/create/', views.create_member, name='create_member'),
    path('portal/roster/edit/<int:pk>/', views.edit_member, name='edit_member'),
    path('portal/roster/delete/<int:pk>/', views.delete_member, name='delete_member'),
    path('portal/roster/import/', views.import_members, name='import_members'),
    path('portal/officers/import/', views.import_officers, name='import_officers'),
    
    # Profile and Post Management (must come before member_profile to avoid conflicts)
    path('portal/profile/edit/', views.edit_own_profile, name='edit_own_profile'),
    path('portal/posts/create/', views.create_post, name='create_post'),
    path('portal/posts/my-posts/', views.my_posts, name='my_posts'),
    path('portal/posts/edit/<int:post_id>/', views.edit_post, name='edit_post'),
    path('portal/posts/delete/<int:post_id>/', views.delete_post, name='delete_post'),
    
    path('portal/profile/<str:username>/', views.member_profile, name='member_profile'),
    path('portal/comment/<int:comment_id>/like/', views.like_comment, name='like_comment'),
    path('portal/dues/', views.dues_view, name='dues_view'),
    path('portal/announcements/', views.announcements_view, name='announcements_view'),
    path('portal/documents/', views.documents_view, name='documents_view'),
    path('portal/messages/', views.messages_inbox, name='messages_inbox'),
    path('portal/messages/<int:message_id>/', views.message_detail, name='message_detail'),
    path('portal/messages/send/', views.send_message, name='send_message'),
    path('portal/messages/send/<str:recipient_username>/', views.send_message, name='send_message_to'),
    path('portal/attendance/', views.attendance_view, name='attendance_view'),
    path('portal/attendance/manage/', views.manage_attendance, name='manage_attendance'),
    path('portal/attendance/add/', views.add_attendance, name='add_attendance'),
    path('portal/attendance/<int:pk>/edit/', views.edit_attendance, name='edit_attendance'),
    path('portal/attendance/<int:pk>/delete/', views.delete_attendance, name='delete_attendance'),
    path('portal/photos/', views.photo_gallery, name='photo_gallery'),
    path('portal/photos/upload/', views.upload_photo, name='upload_photo'),
    path('portal/photos/<int:photo_id>/', views.photo_detail, name='photo_detail'),
    path('portal/photos/<int:photo_id>/edit/', views.edit_photo, name='edit_photo'),
    path('portal/photos/<int:photo_id>/like/', views.like_photo, name='like_photo'),
    path('portal/photos/<int:photo_id>/delete/', views.delete_photo, name='delete_photo'),
    path('portal/albums/create/', views.create_album, name='create_album'),
    path('portal/events/create/', views.create_event, name='create_event'),
    path('portal/events/<int:event_id>/edit/', views.edit_event, name='edit_event'),
    path('portal/events/<int:event_id>/delete/', views.delete_event, name='delete_event'),
    path('portal/documents/create/', views.create_document, name='create_document'),
    path('portal/documents/<int:document_id>/edit/', views.edit_document, name='edit_document'),
    path('portal/documents/<int:document_id>/delete/', views.delete_document, name='delete_document'),
    
    # Dues and Payments Management
    path('portal/dues-and-payments/', views.dues_and_payments, name='dues_and_payments'),
    path('portal/dues-and-payments/create-bill/', views.create_bill, name='create_bill'),
    path('portal/dues-and-payments/add/', views.add_dues_payment, name='add_dues_payment'),
    path('portal/dues-and-payments/edit/<int:pk>/', views.edit_dues_payment, name='edit_dues_payment'),
    path('portal/dues-and-payments/delete/<int:pk>/', views.delete_dues_payment, name='delete_dues_payment'),
    path('portal/member-dues-summary/', views.member_dues_summary, name='member_dues_summary'),
    
    # Stripe Payment Integration
    path('portal/stripe/config/', views.setup_stripe_config, name='stripe_config'),
    path('portal/dues/<int:payment_id>/pay/', views.pay_dues_online, name='pay_dues_online'),
    path('portal/stripe/webhook/', views.stripe_webhook, name='stripe_webhook'),
    path('portal/payment-success/<int:stripe_payment_id>/', views.payment_success, name='payment_success'),
    path('portal/payment-cancelled/<int:stripe_payment_id>/', views.payment_cancelled, name='payment_cancelled'),
    
    # Twilio SMS Integration
    path('portal/twilio/config/', views.setup_twilio_config, name='twilio_config'),
    path('portal/sms/preferences/', views.update_sms_preferences, name='sms_preferences'),
    path('portal/sms/send-alert/', views.send_sms_alert, name='send_sms_alert'),
    path('portal/sms/logs/', views.view_sms_logs, name='view_sms_logs'),
    
    # Boutique / Shop URLs
    path('boutique/', views.shop_home, name='shop_home'),
    path('boutique/product/<int:pk>/', views.product_detail, name='product_detail'),
    path('boutique/add-to-cart/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('boutique/cart/', views.view_cart, name='view_cart'),
    path('boutique/cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('boutique/cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('boutique/checkout/', views.checkout, name='checkout'),
    path('boutique/payment/<int:order_id>/', views.payment, name='payment'),
    path('boutique/payment-success/<int:order_id>/', views.payment_success, name='payment_success'),
    path('boutique/orders/', views.order_history, name='order_history'),
    
    # Boutique Admin URLs (for staff and officers)
    path('boutique/admin/import-products/', views.import_products, name='import_products'),
    path('boutique/admin/add-product/', views.add_product, name='add_product'),
    path('boutique/admin/edit-product/<int:pk>/', views.edit_product, name='edit_product'),
    path('boutique/admin/delete-product/<int:pk>/', views.delete_product, name='delete_product'),
]
