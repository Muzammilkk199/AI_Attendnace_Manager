from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import datetime
import json

# models
try:
    from Ai_Attendance_Manager_Models.models import Student, Attendance
except:
    Student = None
    Attendance = None


def home(request):
    return render(request, 'home.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # simple login check
        if username == 'admin' and password == 'admin123':
            request.session['user_id'] = 1
            request.session['username'] = username
            request.session['is_authenticated'] = True
            
            return JsonResponse({
                'success': True,
                'message': 'Login successful',
                'redirect_url': '/'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Invalid username or password'
            })
    
    return render(request, 'login.html')


def logout_view(request):
    request.session.flush()
    return redirect('login')


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
        
        if Student:
            try:
                student = Student.objects.get(student_id=student_id)
            except:
                return JsonResponse({
                    'success': False,
                    'message': 'Student not found'
                })
        else:
            # demo data
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
                'rate': 75.0
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
    return JsonResponse({'success': False, 'message': 'Not implemented yet'})
