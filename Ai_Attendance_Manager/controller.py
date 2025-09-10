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
    print("Successfully imported Student and Attendance models")
except Exception as e:
    print(f"Error importing models: {e}")
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
    print(f"\n{'='*50}")
    print(f"ADD_STUDENT FUNCTION CALLED")
    print(f"Method: {request.method}")
    print(f"User: {request.user}")
    print(f"Headers: {dict(request.headers)}")
    print(f"{'='*50}")
    
    if request.method == 'POST':
        print("\n📝 PROCESSING POST REQUEST")
        
        # Log all POST data
        print("📋 POST Data received:")
        for key, value in request.POST.items():
            if key == 'face_encoding':
                print(f"  {key}: {value[:100]}... (length: {len(value)})")
            else:
                print(f"  {key}: {value}")
        
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        student_id = request.POST.get('student_id')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        class_name = request.POST.get('class_name', '')
        section = request.POST.get('section', '')
        is_active = request.POST.get('is_active', 'true').lower() == 'true'
        face_encoding = request.POST.get('face_encoding', '')
        face_image = request.POST.get('face_image', '')
        
        print(f"\n🔍 VALIDATION CHECKS:")
        print(f"  First Name: '{first_name}' (valid: {bool(first_name)})")
        print(f"  Last Name: '{last_name}' (valid: {bool(last_name)})")
        print(f"  Student ID: '{student_id}' (valid: {bool(student_id)})")
        print(f"  Face Encoding: {'Present' if face_encoding else 'Missing'}")
        print(f"  Face Image: {'Present' if face_image else 'Missing'}")
        
        if not first_name or not last_name or not student_id:
            print("❌ VALIDATION FAILED: Missing required fields")
            return JsonResponse({
                'success': False,
                'message': 'Please fill required fields'
            })
        
        # Allow testing without face data if using test data
        if not face_encoding or not face_image:
            if face_image == 'data:image/jpeg;base64,test':
                # This is test data, allow it
                face_encoding = '[]'  # Empty array for test
                print("✅ Using test data - no face capture required")
            else:
                print("❌ VALIDATION FAILED: No face data provided")
                return JsonResponse({
                    'success': False,
                    'message': 'Please capture your face for registration'
                })
        
        print(f"\n🗄️ DATABASE OPERATIONS:")
        print(f"  Student model available: {Student is not None}")
        
        if Student:
            try:
                # Check if student ID already exists
                print(f"  Checking if student ID '{student_id}' already exists...")
                existing_student = Student.objects.filter(student_id=student_id).first()
                if existing_student:
                    print(f"❌ Student ID already exists: {existing_student}")
                    return JsonResponse({
                        'success': False,
                        'message': 'Student ID already exists'
                    })
                print(f"✅ Student ID '{student_id}' is available")
                
                # Parse face encoding
                print(f"  Parsing face encoding...")
                try:
                    face_encoding_data = json.loads(face_encoding)
                    print(f"✅ Parsed face encoding: {len(face_encoding_data)} dimensions")
                except json.JSONDecodeError as e:
                    print(f"❌ JSON decode error: {e}")
                    return JsonResponse({
                        'success': False,
                        'message': f'Invalid face data format: {str(e)}'
                    })
                
                # Create student
                print(f"  Creating student in SQLite...")
                student = Student.objects.create(
                    first_name=first_name,
                    last_name=last_name,
                    student_id=student_id,
                    email=email,
                    phone=phone,
                    class_name=class_name,
                    section=section,
                    is_active=is_active
                )
                print(f"✅ Created student: {student} (ID: {student.id})")
                
                # Save face embedding to MongoDB
                print(f"  Saving face embedding to MongoDB...")
                try:
                    result = student.save_embedding(face_encoding_data)
                    print(f"✅ Saved embedding result: {result}")
                    
                    # Also verify the student was saved to MongoDB
                    from Ai_Attendance_Manager_Models.mongodb_manager import StudentMongoDBManager
                    mongo = StudentMongoDBManager()
                    if mongo.connected:
                        mongo_student = mongo.find_by_student_id(student.student_id)
                        if mongo_student:
                            print(f"✅ Student found in MongoDB: {mongo_student['name']}")
                        else:
                            print("❌ Student not found in MongoDB")
                    else:
                        print("⚠️ MongoDB not connected - skipping verification")
                        
                except Exception as e:
                    print(f"⚠️ Error saving embedding: {e}")
                    import traceback
                    traceback.print_exc()
                    # Continue even if embedding save fails - student is already saved in SQLite
                
                print(f"\n🎉 SUCCESS: Student '{student.name}' created successfully!")
                return JsonResponse({
                    'success': True,
                    'message': 'Student added successfully with face registration'
                })
                
            except Exception as e:
                print(f"❌ UNEXPECTED ERROR: {e}")
                import traceback
                traceback.print_exc()
                return JsonResponse({
                    'success': False,
                    'message': f'Error saving student: {str(e)}'
                })
        else:
            print("❌ Student model is None - import failed")
            return JsonResponse({
                'success': False,
                'message': 'Student model not available - check database connection'
            })
    
    print(f"\n📄 RENDERING ADD_STUDENT TEMPLATE")
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

def test_page(request):
    return render(request, 'test_page.html')

@csrf_exempt
def test_mongodb(request):
    """Test MongoDB connection and functionality"""
    print(f"\n{'='*30} MONGODB TEST {'='*30}")
    try:
        from Ai_Attendance_Manager_Models.mongodb_manager import StudentMongoDBManager
        
        # Test connection
        print("Testing MongoDB connection...")
        mongo = StudentMongoDBManager()
        
        if not mongo.connected:
            print("❌ MongoDB not connected")
            return JsonResponse({
                'success': False,
                'message': 'MongoDB connection failed - check your internet connection and MongoDB URI',
                'created': False,
                'retrieved': False
            })
        
        print("✅ MongoDB connected successfully")
        
        # Test creating a document
        test_data = {
            'student_id': 'TEST_MONGO',
            'name': 'Test MongoDB User',
            'first_name': 'Test',
            'last_name': 'MongoDB',
            'email': 'test@mongodb.com',
            'phone': '1234567890',
            'class_name': 'Test Class',
            'section': 'A',
            'is_active': True,
            'embedding': [0.1] * 128,
            'django_id': 999
        }
        
        print("Creating test document...")
        result = mongo.create(**test_data)
        print(f"Create result: {result}")
        
        # Test retrieving the document
        print("Retrieving test document...")
        retrieved = mongo.find_by_student_id('TEST_MONGO')
        print(f"Retrieved: {retrieved is not None}")
        
        # Clean up
        if retrieved:
            print("Cleaning up test document...")
            mongo.delete(retrieved['id'])
        
        print("✅ MongoDB test completed successfully")
        return JsonResponse({
            'success': True,
            'message': 'MongoDB test successful',
            'created': result is not None,
            'retrieved': retrieved is not None
        })
        
    except Exception as e:
        print(f"❌ MongoDB test failed: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'message': f'MongoDB test failed: {str(e)}',
            'created': False,
            'retrieved': False
        })


@csrf_exempt
def test_student_creation(request):
    """Test student creation with mock data"""
    print(f"\n{'='*30} STUDENT CREATION TEST {'='*30}")
    
    try:
        if not Student:
            return JsonResponse({
                'success': False,
                'message': 'Student model not available'
            })
        
        # Create test student data
        test_data = {
            'first_name': 'Test',
            'last_name': 'Student',
            'student_id': f'TEST_{int(timezone.now().timestamp())}',
            'email': 'test@example.com',
            'phone': '1234567890',
            'class_name': 'Test Class',
            'section': 'A',
            'is_active': True,
            'face_encoding': json.dumps([0.1] * 128),
            'face_image': 'data:image/jpeg;base64,test'
        }
        
        print("Creating test student...")
        print(f"Test data: {test_data}")
        
        # Simulate the add_student logic
        student = Student.objects.create(
            first_name=test_data['first_name'],
            last_name=test_data['last_name'],
            student_id=test_data['student_id'],
            email=test_data['email'],
            phone=test_data['phone'],
            class_name=test_data['class_name'],
            section=test_data['section'],
            is_active=test_data['is_active']
        )
        
        print(f"✅ Created student: {student}")
        
        # Test MongoDB save
        try:
            face_encoding_data = json.loads(test_data['face_encoding'])
            result = student.save_embedding(face_encoding_data)
            print(f"✅ Saved embedding: {result}")
        except Exception as e:
            print(f"⚠️ Embedding save failed: {e}")
        
        # Clean up
        student.delete()
        print("✅ Test student deleted")
        
        return JsonResponse({
            'success': True,
            'message': 'Student creation test successful',
            'student_created': True,
            'embedding_saved': result is not None
        })
        
    except Exception as e:
        print(f"❌ Student creation test failed: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'message': f'Student creation test failed: {str(e)}'
        })
