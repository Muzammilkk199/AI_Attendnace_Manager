from django.core.management.base import BaseCommand
from Ai_Attendance_Manager_Models.models import Attendance


class Command(BaseCommand):
    help = 'Fix attendance records with invalid status values'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be changed without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        self.stdout.write('Checking for invalid attendance statuses...')
        
        # Valid statuses are: present, late, absent
        valid_statuses = ['present', 'late', 'absent']
        fixed_count = 0
        total_count = 0
        
        for attendance in Attendance.objects.all():
            total_count += 1
            
            # Check if status is invalid
            if attendance.status not in valid_statuses:
                self.stdout.write(
                    f"Found invalid status for {attendance.student.name} on {attendance.date}: "
                    f"'{attendance.status}' (should be one of: {', '.join(valid_statuses)})"
                )
                
                if not dry_run:
                    # Determine correct status based on check-in/check-out status
                    if attendance.is_checked_in:
                        # If checked in, determine if present or late based on check-in time
                        if attendance.check_in_time:
                            from datetime import time
                            if attendance.check_in_time <= time(8, 0):  # 8:00 AM
                                new_status = 'present'
                            else:
                                new_status = 'late'
                        else:
                            new_status = 'late'  # Default to late if no time
                    else:
                        new_status = 'absent'
                    
                    old_status = attendance.status
                    attendance.status = new_status
                    attendance.notes = f"Fixed: Changed status from '{old_status}' to '{new_status}'. Original: {attendance.notes}"
                    attendance.save()
                    
                    self.stdout.write(f"  -> Changed status from '{old_status}' to '{new_status}'")
                    fixed_count += 1
                else:
                    fixed_count += 1
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(f'DRY RUN: Would fix {fixed_count} out of {total_count} records')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Fixed {fixed_count} out of {total_count} records')
            )
