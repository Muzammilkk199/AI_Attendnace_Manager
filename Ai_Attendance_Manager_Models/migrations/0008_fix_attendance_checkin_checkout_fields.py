# Generated manually to fix existing attendance records

from django.db import migrations


def fix_attendance_records(apps, schema_editor):
    """
    Fix existing attendance records to have correct is_checked_in and is_checked_out values
    """
    Attendance = apps.get_model('Ai_Attendance_Manager_Models', 'Attendance')
    
    # For all existing records, set proper values based on status and times
    for attendance in Attendance.objects.all():
        # If student has check_in_time, they are checked in
        if attendance.check_in_time:
            attendance.is_checked_in = True
        else:
            attendance.is_checked_in = False
            
        # If student has check_out_time, they are checked out
        if attendance.check_out_time:
            attendance.is_checked_out = True
        else:
            attendance.is_checked_out = False
            
        attendance.save()


def reverse_fix_attendance_records(apps, schema_editor):
    """
    Reverse migration - set all to False
    """
    Attendance = apps.get_model('Ai_Attendance_Manager_Models', 'Attendance')
    
    for attendance in Attendance.objects.all():
        attendance.is_checked_in = False
        attendance.is_checked_out = False
        attendance.save()


class Migration(migrations.Migration):

    dependencies = [
        ('Ai_Attendance_Manager_Models', '0007_attendance_is_checked_in_is_checked_out'),
    ]

    operations = [
        migrations.RunPython(fix_attendance_records, reverse_fix_attendance_records),
    ]
