from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from datetime import datetime, timedelta
import json
import re

try:
    from Ai_Attendance_Manager_Models.models import Student, Attendance
except:
    Student = None
    Attendance = None


def home(request):
    return render(request, 'home.html')



def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me') == 'on'
        
        if not username or not password:
            return JsonResponse({
                'success': False,
                'message': 'Please provide both username and password'
            })
        
        # Try to authenticate user
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            if not remember_me:
                request.session.set_expiry(0)
            else:
                request.session.set_expiry(86400 * 7)
            
            return JsonResponse({
                'success': True,
                'message': f'Welcome back, {user.first_name or user.username}!',
                'redirect_url': '/'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Invalid username or password'
            })
    
    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('login')



@csrf_exempt
def forgot_password_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            
            if not email:
                return JsonResponse({
                    'success': False,
                    'message': 'Email address is required'
                })
            
            try:
                user = User.objects.get(email=email)
                
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                
                reset_link = f"{request.scheme}://{request.get_host()}/reset-password/{uid}/{token}/"
                
                send_mail(
                    'Password Reset Request',
                    f'Click the link to reset your password: {reset_link}',
                    settings.DEFAULT_FROM_EMAIL or 'noreply@attendancemanager.com',
                    [email],
                    fail_silently=False,
                )
                
                return JsonResponse({
                    'success': True,
                    'message': 'Password reset link sent to your email'
                })
                
            except User.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'No account found with this email address'
                })
                
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'Invalid JSON data'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Failed to send reset email: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


def reset_password_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            try:
                data = json.loads(request.body)
                password = data.get('password')
                confirm_password = data.get('confirm_password')
                
                if not password or not confirm_password:
                    return JsonResponse({
                        'success': False,
                        'message': 'Both password fields are required'
                    })
                
                if password != confirm_password:
                    return JsonResponse({
                        'success': False,
                        'message': 'Passwords do not match'
                    })
                
                if len(password) < 8:
                    return JsonResponse({
                        'success': False,
                        'message': 'Password must be at least 8 characters long'
                    })
                
                user.set_password(password)
                user.save()
                
                return JsonResponse({
                    'success': True,
                    'message': 'Password reset successfully! You can now login with your new password.'
                })
                
            except json.JSONDecodeError:
                return JsonResponse({
                    'success': False,
                    'message': 'Invalid JSON data'
                })
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'message': f'Password reset failed: {str(e)}'
                })
        
        return render(request, 'reset_password.html', {
            'uidb64': uidb64,
            'token': token,
            'valid': True
        })
    else:
        return render(request, 'reset_password.html', {
            'valid': False,
            'message': 'Invalid or expired reset link'
        })


def add_student(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        student_id = request.POST.get('student_id')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        class_name = request.POST.get('class_name', '')
        
        if not first_name or not last_name or not student_id:
            return JsonResponse({
                'success': False,
                'message': 'Please fill required fields'
            })
        
        # basic validation - need to improve later
        
        if Student:
            if Student.objects.filter(student_id=student_id).exists():
                return JsonResponse({
                    'success': False,
                    'message': 'Student ID already exists'
                })
            
            student = Student.objects.create(
                first_name=first_name,
                last_name=last_name,
                student_id=student_id,
                email=email,
                phone=phone,
                class_name=class_name
            )
        
        return JsonResponse({
            'success': True,
            'message': 'Student added successfully'
        })
    
    return render(request, 'add_student.html')


def attendance(request):
    return render(request, 'attendance.html')



@csrf_exempt
def mark_attendance(request):
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        attendance_type = request.POST.get('attendance_type', 'present')
        
        if not student_id:
            return JsonResponse({
                'success': False,
                'message': 'Student ID required'
            })
        
        # face recognition logic - working on it
        
        if Student:
            try:
                student = Student.objects.get(student_id=student_id)
            except:
                return JsonResponse({
                    'success': False,
                    'message': 'Student not found'
                })
        else:
            # fallback for testing - remove in production
            student = type('Student', (), {
                'id': 1,
                'student_id': student_id,
                'first_name': 'Demo',
                'last_name': 'Student'
            })()
        
        if Attendance:
            attendance_record = Attendance.objects.create(
                student=student,
                date=timezone.now().date(),
                status=attendance_type,
                timestamp=timezone.now()
            )
        else:
            # mock attendance for demo - replace with real data
            attendance_record = type('Attendance', (), {
                'id': 1,
                'student': student,
                'date': timezone.now().date(),
                'status': attendance_type,
                'timestamp': timezone.now()
            })()
        
        return JsonResponse({
            'success': True,
            'message': 'Attendance marked',
            'attendance': {
                'id': attendance_record.id,
                'student_id': student.student_id,
                'student_name': f"{student.first_name} {student.last_name}",
                'status': attendance_type,
                'timestamp': attendance_record.timestamp.isoformat()
            }
        })
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


def report(request):
    students = []
    if Student:
        students = Student.objects.all()
    return render(request, 'report.html', {'students': students})



@csrf_exempt
def attendance_data(request):
    if request.method == 'POST':
        if Attendance:
            records = Attendance.objects.all()[:20]
            summary = {
                'present': records.filter(status='present').count(),
                'late': records.filter(status='late').count(),
                'absent': records.filter(status='absent').count(),
                'rate': 75.0  # hardcoded for now - fix later
            }
            
            attendance_records = []
            for record in records:
                attendance_records.append({
                    'id': record.id,
                    'date': record.date.isoformat(),
                    'student_id': record.student.student_id,
                    'student_name': f"{record.student.first_name} {record.student.last_name}",
                    'status': record.status,
                    'timestamp': record.timestamp.isoformat()
                })
        else:
            summary = {'present': 15, 'late': 3, 'absent': 2, 'rate': 75.0}
            attendance_records = [
                {
                    'id': 1,
                    'date': timezone.now().date().isoformat(),
                    'student_id': 'STU001',
                    'student_name': 'John Doe',
                    'status': 'present',
                    'timestamp': timezone.now().isoformat()
                }
            ]
        
        return JsonResponse({
            'success': True,
            'summary': summary,
            'records': attendance_records
        })
    
    return JsonResponse({'success': False})



@csrf_exempt
def dashboard_data(request):
    if Student and Attendance:
        total_students = Student.objects.count()
        present_today = Attendance.objects.filter(status='present').count()
        late_today = Attendance.objects.filter(status='late').count()
        absent_today = Attendance.objects.filter(status='absent').count()
        
        recent = []
        for record in Attendance.objects.all()[:5]:
            recent.append({
                'id': record.id,
                'student_id': record.student.student_id,
                'student_name': f"{record.student.first_name} {record.student.last_name}",
                'status': record.status,
                'timestamp': record.timestamp.isoformat()
            })
    else:
        # hardcoded values for demo - replace with real data
        total_students = 25
        present_today = 18
        late_today = 4
        absent_today = 3
        
        recent = [
            {
                'id': 1,
                'student_id': 'STU001',
                'student_name': 'John Doe',
                'status': 'present',
                'timestamp': timezone.now().isoformat()
            }
        ]
    
    return JsonResponse({
        'success': True,
        'summary': {
            'total_students': total_students,
            'present_today': present_today,
            'late_today': late_today,
            'absent_today': absent_today
        },
        'recent': recent
    })



def attendance_details(request, attendance_id):
    # not implemented yet - will add later
    return JsonResponse({'success': False, 'message': 'Not implemented yet'})
