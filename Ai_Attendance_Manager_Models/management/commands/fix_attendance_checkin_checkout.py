from django.core.management.base import BaseCommand
from Ai_Attendance_Manager_Models.models import Attendance


class Command(BaseCommand):
    help = 'Fix attendance records with incorrect is_checked_in and is_checked_out values'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be changed without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        self.stdout.write('Checking attendance records...')
        
        fixed_count = 0
        total_count = 0
        
        for attendance in Attendance.objects.all():
            total_count += 1
            needs_fix = False
            changes = []
            
            # Check if is_checked_in is correct
            should_be_checked_in = attendance.check_in_time is not None
            if attendance.is_checked_in != should_be_checked_in:
                needs_fix = True
                changes.append(f"is_checked_in: {attendance.is_checked_in} -> {should_be_checked_in}")
            
            # Check if is_checked_out is correct
            should_be_checked_out = attendance.check_out_time is not None
            if attendance.is_checked_out != should_be_checked_out:
                needs_fix = True
                changes.append(f"is_checked_out: {attendance.is_checked_out} -> {should_be_checked_out}")
            
            if needs_fix:
                self.stdout.write(
                    f"Record {attendance.id} ({attendance.student.name} - {attendance.date}): "
                    f"{', '.join(changes)}"
                )
                
                if not dry_run:
                    attendance.is_checked_in = should_be_checked_in
                    attendance.is_checked_out = should_be_checked_out
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
