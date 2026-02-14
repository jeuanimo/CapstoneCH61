"""
PUBLIC INFORMATION CHATBOT URLS
URL routing for public chatbot endpoints.
"""

from django.urls import path
from pages.views_chatbot import chatbot_query, chatbot_widget

app_name = 'chatbot'

urlpatterns = [
    # GET - Chatbot widget page
    path('', chatbot_widget, name='widget'),
    
    # POST - Query endpoint (API)
    path('api/query/', chatbot_query, name='query'),
]
