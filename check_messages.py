#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from pages.models import Message
from django.contrib.auth.models import User

print(f'Total messages in database: {Message.objects.count()}')

messages = Message.objects.all()[:10]
print('\nAll messages:')
for m in messages:
    print(f'  - From {m.sender.username} to {m.recipient.username}: "{m.subject}" - Read: {m.is_read}')

# Check user's messages
print('\n--- Checking jeuan.mitchell messages ---')
try:
    user = User.objects.get(username='jeuan.mitchell')
    received = Message.objects.filter(recipient=user)
    print(f'Messages received by jeuan.mitchell: {received.count()}')
    for m in received:
        print(f'  - From {m.sender.username}: "{m.subject}"')
except User.DoesNotExist:
    print('User jeuan.mitchell not found')
