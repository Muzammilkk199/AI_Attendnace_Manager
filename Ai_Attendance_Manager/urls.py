"""
URL configuration for Ai_Attendance_Manager project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
import Ai_Attendance_Manager.controller as controller

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Main Pages
    path('', controller.home, name='home'),
    path('login/', controller.login_view, name='login'),
    path('logout/', controller.logout_view, name='logout'),
    path('add-student/', controller.add_student, name='add_student'),
    path('attendance/', controller.attendance, name='attendance'),
    path('report/', controller.report, name='report'),
    
    # API Endpoints
    path('api/dashboard-data/', controller.dashboard_data, name='dashboard_data'),
    path('api/attendance/mark/', controller.mark_attendance, name='mark_attendance'),
    path('api/attendance/data/', controller.attendance_data, name='attendance_data'),
    path('api/attendance/details/<int:attendance_id>/', controller.attendance_details, name='attendance_details'),
    
    # Legacy URLs (for backward compatibility)
    path('Add_Student/', controller.add_student, name='Add_Student'),
]

# Serve static files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
