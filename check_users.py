#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User

users = User.objects.all()
print('All users in database:')
for user in users:
    print(f'  - Username: "{user.username}" | Full name: {user.get_full_name()} | ID: {user.id}')
