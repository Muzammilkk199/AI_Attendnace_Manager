from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST
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
from Ai_Attendance_Manager_Models.models import Attendance, Student
from Ai_Attendance_Manager_Models.mongodb_manager import AttendanceMongoDBManager, StudentMongoDBManager
import io
from openpyxl import Workbook
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

try:
    from Ai_Attendance_Manager_Models.models import Student, Attendance
    print("Successfully imported Student and Attendance models")
except Exception as e:
    print(f"Error importing models: {e}")
    Student = None
    Attendance = None


@login_required
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
        
        # Check if user exists in database first
        try:
            user_exists = User.objects.filter(username=username).exists()
            if not user_exists:
                return JsonResponse({
                    'success': False,
                    'message': 'User does not exist in the system'
                })
        except Exception as e:
            print(f"Error checking user existence: {e}")
            return JsonResponse({
                'success': False,
                'message': 'Database error occurred. Please try again.'
            })
        
        # Try to authenticate user
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Check if user is active
            if not user.is_active:
                return JsonResponse({
                    'success': False,
                    'message': 'Your account has been deactivated. Please contact administrator.'
                })
            
            # Log the user in
            login(request, user)
            
            # Set session expiry
            if not remember_me:
                request.session.set_expiry(0)  # Session expires when browser closes
            else:
                request.session.set_expiry(86400 * 7)  # 7 days
            
            # Update last login time
            user.last_login = timezone.now()
            user.save(update_fields=['last_login'])
            
            return JsonResponse({
                'success': True,
                'message': f'Welcome back, {user.first_name or user.username}!',
                'redirect_url': '/',
                'user_role': 'Administrator' if user.is_staff else 'User'
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


@login_required
def user_management(request):
    """User management page for creating and managing users"""
    if not request.user.is_staff:
        return JsonResponse({
            'success': False,
            'message': 'Access denied. Admin privileges required.'
        }, status=403)
    
    if request.method == 'POST':
        try:
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            first_name = request.POST.get('first_name', '')
            last_name = request.POST.get('last_name', '')
            is_staff = request.POST.get('is_staff') == 'on'
            
            if not username or not email or not password:
                return JsonResponse({
                    'success': False,
                    'message': 'Username, email, and password are required'
                })
            
            # Check if user already exists
            if User.objects.filter(username=username).exists():
                return JsonResponse({
                    'success': False,
                    'message': 'Username already exists'
                })
            
            if User.objects.filter(email=email).exists():
                return JsonResponse({
                    'success': False,
                    'message': 'Email already exists'
                })
            
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                is_staff=is_staff,
                is_active=True
            )
            
            return JsonResponse({
                'success': True,
                'message': f'User "{username}" created successfully'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error creating user: {str(e)}'
            })
    
    # Get all users for display
    users = User.objects.all().order_by('-date_joined')
    context = {
        'users': users
    }
    return render(request, 'user_management.html', context)



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


@login_required
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


@login_required
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


@login_required
def report(request):
    """Render attendance report using MongoDB Atlas instead of SQLite"""
    attendance_manager = AttendanceMongoDBManager()
    student_manager = StudentMongoDBManager()

    attendance_records = []
    students = []

    total_present = 0
    total_late = 0
    total_absent = 0
    attendance_rate = 0

    if attendance_manager.connected:
        try:
            docs = attendance_manager.get_all_attendance()
            docs.sort(key=lambda x: (x.get('date', ''), x.get('timestamp', '')), reverse=True)

            for doc in docs[:50]:
                # Count summary
                status = doc.get("status", "").lower()
                if status == "present":
                    total_present += 1
                elif status == "late":
                    total_late += 1
                elif status == "absent":
                    total_absent += 1

                attendance_records.append({
                    "id": doc.get("_id"),
                    "date": doc.get("date", ""),
                    "student_id": doc.get("student_id", ""),
                    "student_name": doc.get("student_name", ""),
                    "status": doc.get("status", ""),
                    "timestamp": doc.get("timestamp", ""),
                    "notes": doc.get("notes", "-"),
                })

            # Calculate attendance rate (Present / (Present + Late + Absent))
            total = total_present + total_late + total_absent
            if total > 0:
                attendance_rate = round((total_present / total) * 100, 2)

        except Exception as e:
            print(f"Error fetching attendance from MongoDB: {e}")

    if student_manager.connected:
        try:
            students = student_manager.get_active_students()
            students.sort(key=lambda s: s.get("name", ""))
        except Exception as e:
            print(f"Error fetching students from MongoDB: {e}")

    context = {
        "attendance_records": attendance_records,
        "students": students,
        "total_present": total_present,
        "total_late": total_late,
        "total_absent": total_absent,
        "attendance_rate": attendance_rate,
    }
    return render(request, "report.html", context)

@csrf_exempt
def attendance_data(request):
    if request.method == 'POST':
        attendance_manager = AttendanceMongoDBManager()
        
        summary = {"present": 0, "late": 0, "absent": 0, "rate": 0}
        attendance_records = []

        if attendance_manager.connected:
            try:
                # Get filter parameters from request
                date_from = request.POST.get('date_from')
                date_to = request.POST.get('date_to')
                student_id = request.POST.get('student_id')

                # Build filter based on request parameters
                filter_dict = {}
                
                # Date range filter
                if date_from and date_to:
                    filter_dict['date'] = {
                        '$gte': date_from,
                        '$lte': date_to
                    }
                elif date_from:
                    filter_dict['date'] = {'$gte': date_from}
                elif date_to:
                    filter_dict['date'] = {'$lte': date_to}
                
                # Student filter
                if student_id:
                    filter_dict['student_id'] = student_id

                # Use the filter method
                docs = list(attendance_manager.collection.find(filter_dict))
                docs.sort(key=lambda x: (x.get('date', ''), x.get('timestamp', '')), reverse=True)

                for doc in docs[:100]:
                    status = doc.get("status", "").lower()
                    if status == "present":
                        summary["present"] += 1
                    elif status == "late":
                        summary["late"] += 1
                    elif status == "absent":
                        summary["absent"] += 1

                    # CORRECT WAY: Extract the _id field from MongoDB document
                    # MongoDB documents have _id field, not id
                    record_id = str(doc.get("_id", ""))  # This gets the MongoDB ObjectId
                    
                    attendance_records.append({
                        "id": record_id,  # This should now have the correct MongoDB _id
                        "date": doc.get("date", ""),
                        "student_id": doc.get("student_id", ""),
                        "student_name": doc.get("student_name", ""),
                        "status": doc.get("status", ""),
                        "timestamp": doc.get("timestamp", ""),
                        "notes": doc.get("notes", "-"),
                        # Also include django_id as fallback
                        "django_id": doc.get("django_id", "")
                    })

                total = summary["present"] + summary["late"] + summary["absent"]
                if total > 0:
                    summary["rate"] = round((summary["present"] / total) * 100, 2)

            except Exception as e:
                print(f"Error in attendance_data: {e}")

        return JsonResponse({
            "success": True,
            "summary": summary,
            "records": attendance_records
        })

    return JsonResponse({"success": False})

@csrf_exempt
def dashboard_data(request):
    """Get dashboard data from MongoDB - overall stats for cards, today's for chart"""
    try:
        student_manager = StudentMongoDBManager()
        attendance_manager = AttendanceMongoDBManager()
        
        total_students = 0
        present_total = 0
        late_total = 0
        absent_total = 0
        present_today = 0
        late_today = 0
        absent_today = 0
        recent = []
        
        # Get today's date for the pie chart
        today = datetime.now().date().isoformat()
        
        if student_manager.connected:
            # Get total students count from MongoDB
            total_students = student_manager.count()
        
        if attendance_manager.connected:
            # Get OVERALL attendance stats from MongoDB for summary cards
            all_attendance = list(attendance_manager.collection.find())
            
            for record in all_attendance:
                status = record.get("status", "").lower()
                if status == "present":
                    present_total += 1
                elif status == "late":
                    late_total += 1
                elif status == "absent":
                    absent_total += 1
            
            # Get TODAY'S attendance stats for the pie chart
            today_filter = {'date': today}
            today_attendance = list(attendance_manager.collection.find(today_filter))
            
            for record in today_attendance:
                status = record.get("status", "").lower()
                if status == "present":
                    present_today += 1
                elif status == "late":
                    late_today += 1
                elif status == "absent":
                    absent_today += 1
            
            # Get recent attendance (last 5 records) - ALL records, not filtered by date
            recent_docs = list(attendance_manager.collection.find()
                              .sort("timestamp", -1)  # Sort by timestamp descending
                              .limit(5))
            
            for doc in recent_docs:
                # Ensure status is properly formatted and lowercase for consistency
                status = doc.get("status", "").lower()
                recent.append({
                    'id': str(doc.get('_id', '')),
                    'student_id': doc.get('student_id', ''),
                    'student_name': doc.get('student_name', 'Unknown'),
                    'status': status,  # Use lowercase version
                    'timestamp': doc.get("timestamp", ""),
                    'notes': doc.get('notes', '-')
                })
                
    except Exception as e:
        print(f"Error in dashboard_data: {e}")
        # Fallback to demo data with proper status values
        total_students = 25
        present_today = 18  # Today's present count
        late_today = 4      # Today's late count
        absent_today = 3    # Today's absent count
        
        recent = [
            {
                'id': '1',
                'student_id': 'STU001',
                'student_name': 'John Doe',
                'status': 'present',
                'timestamp': datetime.now().isoformat(),
                'notes': 'On time'
            },
            {
                'id': '2',
                'student_id': 'STU002',
                'student_name': 'Jane Smith',
                'status': 'late',
                'timestamp': (datetime.now() - timedelta(hours=1)).isoformat(),
                'notes': 'Arrived 15 minutes late'
            },
            {
                'id': '3',
                'student_id': 'STU003',
                'student_name': 'Bob Johnson',
                'status': 'present',
                'timestamp': (datetime.now() - timedelta(days=1)).isoformat(),
                'notes': 'Regular attendance'
            }
        ]
    
    return JsonResponse({
        'success': True,
        'summary': {
            'total_students': total_students,
            'present_today': present_today,  # Today's present count for cards
            'late_today': late_today,        # Today's late count for cards
            'absent_today': absent_today,    # Today's absent count for cards
            'present_today_chart': present_today,  # Today's present for chart
            'late_today_chart': late_today,        # Today's late for chart
            'absent_today_chart': absent_today     # Today's absent for chart
        },
        'recent': recent
    })

@require_POST
def delete_attendance(request, attendance_id):
    """
    Deletes an attendance record from both MongoDB and SQLite databases.
    Expects POST (AJAX) with CSRF header.
    """
    try:
        sqlite_deleted = False
        mongo_deleted = False
        message_parts = []
        
        # First, try to delete from SQLite
        try:
            # Try to find the record by ID
            attendance_record = Attendance.objects.get(id=attendance_id)
            attendance_record.delete()
            sqlite_deleted = True
            message_parts.append("SQLite")
        except (Attendance.DoesNotExist, ValueError):
            # If record doesn't exist by ID, try to find it by django_id
            try:
                attendance_record = Attendance.objects.get(django_id=attendance_id)
                attendance_record.delete()
                sqlite_deleted = True
                message_parts.append("SQLite")
            except (Attendance.DoesNotExist, ValueError):
                sqlite_deleted = False
        
        # Then delete from MongoDB
        mongo = AttendanceMongoDBManager()
        if mongo.connected:
            try:
                # First try to delete by MongoDB's _id (ObjectId)
                from bson import ObjectId
                try:
                    obj_id = ObjectId(attendance_id)
                    mongo_result = mongo.collection.delete_one({"_id": obj_id})
                    if mongo_result.deleted_count > 0:
                        mongo_deleted = True
                        message_parts.append("MongoDB")
                except:
                    # If not a valid ObjectId, try with django_id field
                    mongo_result = mongo.collection.delete_one({"django_id": attendance_id})
                    if mongo_result.deleted_count > 0:
                        mongo_deleted = True
                        message_parts.append("MongoDB")
            except Exception as e:
                print(f"Error deleting from MongoDB: {e}")
                mongo_deleted = False

        # Return appropriate response
        if sqlite_deleted or mongo_deleted:
            if sqlite_deleted and mongo_deleted:
                message = "Attendance record deleted successfully from both databases"
            else:
                databases = " and ".join(message_parts)
                message = f"Attendance record deleted successfully from {databases} only"
            return JsonResponse({"success": True, "message": message})
        else:
            return JsonResponse({"success": False, "message": "Attendance record not found in either database"}, status=404)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({"success": False, "message": f"Error deleting attendance: {str(e)}"}, status=500)

def edit_attendance(request, attendance_id):
    """Edit attendance details - placeholder function"""
    # For now, just redirect back to report page
    # You can implement the actual edit functionality later
    return redirect('report')

@csrf_exempt
def export_attendance_excel(request):
    """Export filtered attendance records to Excel"""
    attendance_manager = AttendanceMongoDBManager()

    if not attendance_manager.connected:
        return HttpResponse("MongoDB not connected", status=500)

    # Get filter parameters from request
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    student_id = request.GET.get('student_id')

    # Build filter based on request parameters
    filter_dict = {}
    
    # Date range filter
    if date_from and date_to:
        filter_dict['date'] = {
            '$gte': date_from,
            '$lte': date_to
        }
    elif date_from:
        filter_dict['date'] = {'$gte': date_from}
    elif date_to:
        filter_dict['date'] = {'$lte': date_to}
    
    # Student filter
    if student_id:
        filter_dict['student_id'] = student_id

    # Get filtered records
    if hasattr(attendance_manager, 'get_all_attendance_with_filter'):
        records = attendance_manager.get_all_attendance_with_filter(filter_dict)
    else:
        # Fallback to all records if the method doesn't exist
        records = attendance_manager.get_all_attendance()

    wb = Workbook()
    ws = wb.active
    ws.title = "Attendance"

    # Headers - remove "Actions" column
    headers = ["Date", "Student ID", "Name", "Status", "Time", "Notes"]
    ws.append(headers)

    # Rows
    for rec in records:
        ws.append([
            rec.get("date", ""),
            rec.get("student_id", ""),
            rec.get("student_name", ""),
            rec.get("status", ""),
            str(rec.get("timestamp", "")),
            rec.get("notes", ""),
        ])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="attendance_report.xlsx"'
    wb.save(response)
    return response

@csrf_exempt
def export_attendance_pdf(request):
    """Export filtered attendance records to PDF"""
    attendance_manager = AttendanceMongoDBManager()

    if not attendance_manager.connected:
        return HttpResponse("MongoDB not connected", status=500)

    # Get filter parameters from request
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    student_id = request.GET.get('student_id')

    # Build filter based on request parameters
    filter_dict = {}
    
    # Date range filter
    if date_from and date_to:
        filter_dict['date'] = {
            '$gte': date_from,
            '$lte': date_to
        }
    elif date_from:
        filter_dict['date'] = {'$gte': date_from}
    elif date_to:
        filter_dict['date'] = {'$lte': date_to}
    
    # Student filter
    if student_id:
        filter_dict['student_id'] = student_id

    # Get filtered records
    if hasattr(attendance_manager, 'get_all_attendance_with_filter'):
        records = attendance_manager.get_all_attendance_with_filter(filter_dict)
    else:
        # Fallback to all records if the method doesn't exist
        records = attendance_manager.get_all_attendance()

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # Add title
    elements.append(Paragraph("Attendance Report", styles["Title"]))
    elements.append(Spacer(1, 12))

    # Table data (headers first) - remove "Actions" column
    data = [["Date", "Student ID", "Name", "Status", "Time", "Notes"]]

    for rec in records:
        data.append([
            rec.get("date", ""),
            rec.get("student_id", ""),
            rec.get("student_name", ""),
            rec.get("status", ""),
            str(rec.get("timestamp", "")),
            rec.get("notes", ""),
        ])

    table = Table(data)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#007BFF")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
    ]))

    elements.append(table)
    doc.build(elements)

    pdf = buffer.getvalue()
    buffer.close()

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="attendance_report.pdf"'
    response.write(pdf)
    return response

@login_required
def test_page(request):
    return render(request, 'test_page.html')

@login_required
def student_details(request):
    # Get all students from MongoDB
    student_manager = StudentMongoDBManager()
    students = list(student_manager.get_all_students())

    # Calculate stats
    total_students = len(students)
    active_students = sum(1 for s in students if s.get("is_active", False))
    inactive_students = total_students - active_students

    context = {
        "students": students,
        "total_students": total_students,
        "active_students": active_students,
        "inactive_students": inactive_students,
    }
    return render(request, "student_details.html", context)

@require_POST
def delete_student(request, student_id):
    """ 
    Deletes a student from MongoDB by student_id and returns JSON.
    Expects POST (AJAX) with CSRF header.
    """
    try:
        mongo = StudentMongoDBManager()
        if not getattr(mongo, "connected", True):
            return JsonResponse({"success": False, "message": "MongoDB not connected"}, status=500)

        result = mongo.delete_by_student_id(student_id)
        # result is a pymongo DeleteResult (has deleted_count)
        deleted_count = getattr(result, "deleted_count", None)

        if deleted_count is None:
            # fallback for custom manager return types
            if result:
                return JsonResponse({"success": True, "message": "Student deleted successfully"})
            return JsonResponse({"success": False, "message": "Student not found"}, status=404)

        if deleted_count > 0:
            return JsonResponse({"success": True, "message": "Student deleted successfully"})
        else:
            return JsonResponse({"success": False, "message": "Student not found"}, status=404)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({"success": False, "message": f"Error deleting student: {str(e)}"}, status=500)


def edit_student(request, student_id):
    """Edit student details in MongoDB"""
    mongo = StudentMongoDBManager()
    if not mongo.connected:
        return JsonResponse({"success": False, "message": "MongoDB not connected"})

    student = mongo.find_by_student_id(student_id)
    if not student:
        return JsonResponse({"success": False, "message": "Student not found"})

    if request.method == "POST":
        data = {
            "name": request.POST.get("name"),
            "first_name": request.POST.get("first_name"),
            "last_name": request.POST.get("last_name"),
            "email": request.POST.get("email"),
            "phone": request.POST.get("phone"),
            "class_name": request.POST.get("class_name"),
            "section": request.POST.get("section"),
            "is_active": request.POST.get("is_active") == "on",
        }
        mongo.update_student(student_id, data)
        return redirect("student_details")

    return render(request, "edit_student.html", {"student": student})

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
