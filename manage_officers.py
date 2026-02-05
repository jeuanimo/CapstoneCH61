#!/usr/bin/env python
"""
Script to manage officer permissions for chapter members
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, '/home/user/Downloads/CapstoneCH61')
django.setup()

from django.contrib.auth.models import User
from pages.models import MemberProfile

def check_officer_status(username):
    """Check if a user has officer status"""
    try:
        user = User.objects.get(username=username)
        if hasattr(user, 'memberprofile'):
            profile = user.memberprofile
            print(f"\n{'='*60}")
            print(f"User: {user.get_full_name()} (@{username})")
            print(f"Member Number: {profile.member_number}")
            print(f"Status: {profile.status}")
            print(f"Dues Current: {profile.dues_current}")
            print(f"Is Officer: {profile.is_officer} {'✓' if profile.is_officer else '✗'}")
            print(f"{'='*60}\n")
            return profile.is_officer
        else:
            print(f"\n❌ User '{username}' does not have a MemberProfile!\n")
            return False
    except User.DoesNotExist:
        print(f"\n❌ User '{username}' not found!\n")
        return False

def set_officer_status(username, is_officer):
    """Set officer status for a user"""
    try:
        user = User.objects.get(username=username)
        if hasattr(user, 'memberprofile'):
            profile = user.memberprofile
            old_status = profile.is_officer
            profile.is_officer = is_officer
            profile.save()
            print(f"\n✅ Updated {user.get_full_name()} (@{username})")
            print(f"   is_officer: {old_status} → {is_officer}\n")
            return True
        else:
            print(f"\n❌ User '{username}' does not have a MemberProfile!\n")
            return False
    except User.DoesNotExist:
        print(f"\n❌ User '{username}' not found!\n")
        return False

def list_all_officers():
    """List all users with officer status"""
    officers = MemberProfile.objects.filter(is_officer=True).select_related('user')
    print(f"\n{'='*60}")
    print(f"Officers with Admin Privileges ({officers.count()} total)")
    print(f"{'='*60}")
    for profile in officers:
        print(f"  • {profile.user.get_full_name()} (@{profile.user.username}) - {profile.member_number}")
    print(f"{'='*60}\n")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Manage officer permissions')
    parser.add_argument('--check', help='Check officer status for a user')
    parser.add_argument('--grant', help='Grant officer privileges to a user')
    parser.add_argument('--revoke', help='Revoke officer privileges from a user')
    parser.add_argument('--list', action='store_true', help='List all officers')
    
    args = parser.parse_args()
    
    if args.check:
        check_officer_status(args.check)
    elif args.grant:
        set_officer_status(args.grant, True)
    elif args.revoke:
        set_officer_status(args.revoke, False)
    elif args.list:
        list_all_officers()
    else:
        parser.print_help()
