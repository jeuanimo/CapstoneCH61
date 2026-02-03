from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),           # Home page
    path('about/', views.about, name='about'),       # About page
    path('events/', views.events, name='events'),     # Events & Service page
    path('news/', views.news, name='news'),           # News page
    path('programs/', views.programs, name='programs'),  # Programs page
    path('chapter-history/', views.chapter_history, name='chapter_history'),  # Chapter History page
    path('chapter-leadership/', views.chapter_leadership, name='chapter_leadership'),  # Chapter Leadership page
    path('chapter-membership/', views.chapter_membership, name='chapter_membership'),  # Chapter Membership page
    path('chapter-programs/', views.chapter_programs, name='chapter_programs'),  # Chapter Programs page
    path('action/', views.action, name='action'),     # Nu Gamma Sigma in Action page
    path('signin/', views.signin, name='signin'),     # Sign in page
    path('contact/', views.contact, name='contact'),   # Contact page
]