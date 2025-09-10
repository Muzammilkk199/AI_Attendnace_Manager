from django.contrib import admin
from .models import Student, Attendance


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['student_id', 'name', 'class_name', 'is_active']
    list_filter = ['class_name', 'is_active']
    search_fields = ['student_id', 'name']


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'date', 'status', 'timestamp']
    list_filter = ['status', 'date']
    search_fields = ['student__name', 'student__student_id']
