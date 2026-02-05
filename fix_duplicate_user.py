#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from pages.models import MemberProfile, Message

# Get both users
user_old = User.objects.get(id=2)  # Jeuan.Mitchell
user_new = User.objects.get(id=3)  # jeuan.mitchell

print(f'Old user: {user_old.username} (ID: {user_old.id})')
print(f'New user: {user_new.username} (ID: {user_new.id})')

# Transfer messages
messages_received = Message.objects.filter(recipient=user_old)
print(f'\nTransferring {messages_received.count()} received messages...')
messages_received.update(recipient=user_new)

messages_sent = Message.objects.filter(sender=user_old)
print(f'Transferring {messages_sent.count()} sent messages...')
messages_sent.update(sender=user_new)

# Transfer member profile
try:
    profile_old = MemberProfile.objects.get(user=user_old)
    print(f'\nTransferring MemberProfile (member #{profile_old.member_number})...')
    profile_old.user = user_new
    profile_old.save()
except MemberProfile.DoesNotExist:
    print('\nNo profile found for old user')

# Delete duplicate profile on new user if exists
try:
    profile_new = MemberProfile.objects.get(user=user_new)
    if profile_new.id != profile_old.id:
        print(f'Deleting duplicate profile on new user...')
        profile_new.delete()
except:
    pass

# Delete old user
print(f'\nDeleting old user {user_old.username}...')
user_old.delete()

print('\nMigration complete!')
print(f'All data now belongs to user: {user_new.username}')
