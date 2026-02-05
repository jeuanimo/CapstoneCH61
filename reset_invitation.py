#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from pages.models import InvitationCode

# Get the most recently used invitation
inv = InvitationCode.objects.filter(is_used=True).order_by('-created_at').first()

if inv:
    print(f'Resetting invitation code: {inv.code}')
    inv.is_used = False
    inv.used_by = None
    inv.used_at = None
    inv.save()
    print('Successfully reset!')
else:
    print('No used invitations found')
