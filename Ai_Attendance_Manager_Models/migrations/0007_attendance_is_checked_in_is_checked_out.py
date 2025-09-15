# Generated manually for attendance model updates

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Ai_Attendance_Manager_Models', '0006_attendance_check_in_time_attendance_check_out_time_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='attendance',
            name='status',
        ),
        migrations.AddField(
            model_name='attendance',
            name='status',
            field=models.CharField(choices=[('present', 'Present'), ('late', 'Late'), ('absent', 'Absent')], default='present', max_length=15),
        ),
        migrations.AddField(
            model_name='attendance',
            name='is_checked_in',
            field=models.BooleanField(default=False, help_text='Whether student has checked in today'),
        ),
        migrations.AddField(
            model_name='attendance',
            name='is_checked_out',
            field=models.BooleanField(default=False, help_text='Whether student has checked out today'),
        ),
    ]
