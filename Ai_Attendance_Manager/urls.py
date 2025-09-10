# URL configuration
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render
import Ai_Attendance_Manager.controller as controller   

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('', controller.home, name='home'),
    path('login/', controller.login_view, name='login'),
    path('logout/', controller.logout_view, name='logout'),
    path('forgot-password/', controller.forgot_password_view, name='forgot_password'),
    path('reset-password/<str:uidb64>/<str:token>/', controller.reset_password_view, name='reset_password'),
    
    path('add-student/', controller.add_student, name='add_student'),
    path('attendance/', controller.attendance, name='attendance'),
    path('report/', controller.report, name='report'),
    path('test/',controller.test_page, name='test_page'),
    path('face-demo/', lambda request: render(request, 'face_detection_demo.html'), name='face_demo'),
    path('camera-test/', lambda request: render(request, 'camera_test.html'), name='camera_test'),
    
    path('api/dashboard-data/', controller.dashboard_data, name='dashboard_data'),
    path('api/attendance/mark/', controller.mark_attendance, name='mark_attendance'),
    path('api/attendance/data/', controller.attendance_data, name='attendance_data'),
    path('api/attendance/details/<int:attendance_id>/', controller.attendance_details, name='attendance_details'),
    path('api/test-mongodb/', controller.test_mongodb, name='test_mongodb'),
    path('api/test-student/', controller.test_student_creation, name='test_student_creation'),
    
    # legacy support
    path('Add_Student/', controller.add_student, name='Add_Student'),
]

# Serve static files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
