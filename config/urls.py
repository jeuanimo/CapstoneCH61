"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from django.shortcuts import render
from pages import views


# Custom error handlers for security
def bad_request_view(request, exception=None):
    """Custom 400 error handler for invalid host headers and bad requests"""
    return render(request, '400.html', status=400)


def page_not_found_view(request, exception=None):
    """Custom 404 error handler"""
    return render(request, '404.html', status=404)


def server_error_view(request):
    """Custom 500 error handler"""
    return render(request, '500.html', status=500)


# Register custom error handlers
handler400 = bad_request_view
handler404 = page_not_found_view
handler500 = server_error_view

urlpatterns = [
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    path('admin/', admin.site.urls),
    path('', views.home_view, name='home'),
    path('', include('pages.urls')),  # Pages URLs at root (no /pages/ prefix)
    path('chatbot/', include('pages.urls_chatbot')),
    
    # PASSWORD RESET (for CSV-imported users to set their password)
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='registration/password_reset.html',
             email_template_name='registration/password_reset_email.html',
             subject_template_name='registration/password_reset_subject.txt',
             success_url='/password-reset/done/'
         ), 
         name='password_reset'),
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='registration/password_reset_done.html'
         ), 
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='registration/password_reset_confirm.html',
             success_url='/password-reset-complete/'
         ), 
         name='password_reset_confirm'),
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='registration/password_reset_complete.html'
         ), 
         name='password_reset_complete'),
    
    # PASSWORD CHANGE (for logged-in users to change their password)
    path('password-change/', 
         auth_views.PasswordChangeView.as_view(
             template_name='registration/password_change.html',
             success_url='/password-change/done/'
         ), 
         name='password_change'),
    path('password-change/done/', 
         auth_views.PasswordChangeDoneView.as_view(
             template_name='registration/password_change_done.html'
         ), 
         name='password_change_done'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
