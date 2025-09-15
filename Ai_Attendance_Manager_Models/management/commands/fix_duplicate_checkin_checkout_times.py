from django.core.management.base import BaseCommand
from Ai_Attendance_Manager_Models.models import Attendance


class Command(BaseCommand):
    help = 'Fix attendance records where check-in and check-out times are the same'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be changed without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        self.stdout.write('Checking for duplicate check-in/check-out times...')
        
        fixed_count = 0
        total_count = 0
        
        for attendance in Attendance.objects.all():
            total_count += 1
            
            # Check if both times exist and are the same
            if (attendance.check_in_time and attendance.check_out_time and 
                attendance.check_in_time == attendance.check_out_time):
                
                self.stdout.write(
                    f"Found duplicate time for {attendance.student.name} on {attendance.date}: "
                    f"Both check-in and check-out at {attendance.check_in_time}"
                )
                
                if not dry_run:
                    # Reset check-out fields since they shouldn't be the same as check-in
                    attendance.is_checked_out = False
                    attendance.check_out_time = None
                    attendance.notes = f"Fixed: Removed duplicate check-out time. Original: {attendance.notes}"
                    attendance.save()
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
