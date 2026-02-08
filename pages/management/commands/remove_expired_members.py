"""
Django management command to remove members after 90-day grace period
Run with: python manage.py remove_expired_members
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
import logging
from pages.models import MemberProfile

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Remove members who have exceeded the 90-day grace period from HQ sync'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            dest='dry_run',
            help='Show what would be removed without actually removing',
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        
        # Find all members marked for removal
        marked_members = MemberProfile.objects.filter(marked_for_removal_date__isnull=False)
        
        if not marked_members.exists():
            self.stdout.write(self.style.SUCCESS('No members marked for removal'))
            return
        
        # Find those that should be removed (90+ days passed)
        members_to_remove = [m for m in marked_members if m.should_be_removed()]
        
        if not members_to_remove:
            self.stdout.write(
                self.style.WARNING(
                    f'Found {marked_members.count()} members in grace period, '
                    f'but none ready for removal yet'
                )
            )
            return
        
        self.stdout.write(
            self.style.WARNING(f'Found {len(members_to_remove)} members ready for removal')
        )
        
        if dry_run:
            self.stdout.write('\n=== DRY RUN MODE (No changes will be made) ===\n')
        
        removed_count = 0
        for member_profile in members_to_remove:
            days_marked = (timezone.now() - member_profile.marked_for_removal_date).days
            reason = member_profile.removal_reason
            user = member_profile.user
            full_name = member_profile.get_full_name()
            member_number = member_profile.member_number
            
            self.stdout.write(
                f'  {full_name} ({member_number}) - '
                f'Marked {days_marked} days ago: {reason}'
            )
            
            if not dry_run:
                try:
                    # Delete member profile and user
                    member_profile.delete()
                    user.delete()
                    removed_count += 1
                    
                    logger.info(
                        f'Removed member {member_number} ({full_name}) '
                        f'after {days_marked} day grace period'
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Error removing {full_name}: {str(e)}')
                    )
                    logger.error(f'Error removing member {member_number}: {str(e)}')
        
        # Summary
        if dry_run:
            self.stdout.write(
                self.style.WARNING(f'\n[DRY RUN] Would remove {len(members_to_remove)} members')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'\n✓ Removed {removed_count} member(s)')
            )
            logger.info(f'Removed {removed_count} expired members via management command')
