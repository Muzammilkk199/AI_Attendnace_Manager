from django.contrib import admin
from .models import Student, Attendance


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['student_id', 'name', 'class_name', 'is_active']
    list_filter = ['class_name', 'is_active']
    search_fields = ['student_id', 'name']


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'date', 'status', 'is_checked_in', 'is_checked_out', 'check_in_time', 'check_out_time', 'timestamp']
    list_filter = ['status', 'date', 'is_checked_in', 'is_checked_out']
    search_fields = ['student__name', 'student__student_id']
    fields = ['student', 'date', 'status', 'is_checked_in', 'is_checked_out', 'check_in_time', 'check_out_time', 'confidence', 'notes']
    
    def save_model(self, request, obj, form, change):
        """
        Override save to ensure proper check-in/check-out logic
        """
        # If manually setting check_in_time, ensure is_checked_in is True
        if obj.check_in_time and not obj.is_checked_in:
            obj.is_checked_in = True
            
        # If manually setting check_out_time, ensure is_checked_out is True
        if obj.check_out_time and not obj.is_checked_out:
            obj.is_checked_out = True
            
        # If removing check_in_time, set is_checked_in to False
        if not obj.check_in_time and obj.is_checked_in:
            obj.is_checked_in = False
            
        # If removing check_out_time, set is_checked_out to False
        if not obj.check_out_time and obj.is_checked_out:
            obj.is_checked_out = False
            
        super().save_model(request, obj, form, change)
