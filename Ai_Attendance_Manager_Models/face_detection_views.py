import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from .python_face_detection import detect_faces_in_image

logger = logging.getLogger(__name__)

@method_decorator(csrf_exempt, name='dispatch')
class FaceDetectionView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            base64_image = data.get('image')
            
            if not base64_image:
                return JsonResponse({
                    'success': False,
                    'error': 'No image data provided'
                }, status=400)
            
            result = detect_faces_in_image(base64_image)
            
            return JsonResponse(result)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            }, status=400)
            
        except Exception as e:
            logger.error(f"Face detection error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Internal server error'
            }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def face_detection_api(request):
       
    logger.info(" FACE DETECTION API CALLED")
    
    try:
        body_size = len(request.body)
        if body_size > 5 * 1024 * 1024: 
            logger.warning(f"Request too large: {body_size} bytes")
            return JsonResponse({
                'success': False,
                'error': 'Image too large (max 5MB)'
            }, status=413)
            
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            }, status=400)
            
        base64_image = data.get('image')
        source = data.get('source', 'webcam')
        
        logger.info(f"📊 Request details: source={source}, image_size={len(base64_image) if base64_image else 0}")
        
        if not base64_image:
            logger.error("No image data provided")
            return JsonResponse({
                'success': False,
                'error': 'No image data provided'
            }, status=400)
        
        try:
            logger.info(" Starting face detection processing...")
            result = detect_faces_in_image(base64_image)
            logger.info(f" Face detection completed: success={result.get('success', False)}, faces={result.get('face_count', 0)}")
            
            result['source'] = source
            
            return JsonResponse(result)
            
        except Exception as detection_error:
            logger.error(f" Face detection processing error: {detection_error}")
            import traceback
            traceback.print_exc()
            return JsonResponse({
                'success': False,
                'error': f'Face detection failed: {str(detection_error)}',
                'faces': [],
                'face_count': 0
            }, status=500)
        
    except Exception as e:
        logger.error(f" Face detection API error: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': 'Internal server error'
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def face_detection_status(request):
    """
    Enhanced status check for face detection system
    """
    try:
        logger.info(" FACE DETECTION STATUS CHECK")
        
        try:
            import face_recognition
            logger.info(" face_recognition library imported successfully")
            face_recognition_available = True
        except ImportError as e:
            logger.error(f" face_recognition import failed: {e}")
            face_recognition_available = False
            
        try:
            import cv2
            logger.info(" OpenCV library imported successfully")
            opencv_available = True
        except ImportError as e:
            logger.error(f" OpenCV import failed: {e}")
            opencv_available = False
            
        try:
            from .python_face_detection import face_detector
            detector_status = 'ready' if face_detector.initialized else 'not_initialized'
            logger.info(f" Face detector status: {detector_status}")
        except Exception as e:
            logger.error(f" Face detector check failed: {e}")
            detector_status = 'error'
        
        return JsonResponse({
            'success': True,
            'status': detector_status,
            'face_recognition_available': face_recognition_available,
            'opencv_available': opencv_available,
            'message': 'Python face detection system status check completed',
            'details': {
                'detector_initialized': detector_status == 'ready',
                'libraries_available': face_recognition_available and opencv_available
            }
        })
        
    except Exception as e:
        logger.error(f" Status check error: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': f'Status check failed: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def recognize_student(request):
       
    logger.info(f"\n{'='*50}")
    logger.info(f"STUDENT RECOGNITION REQUEST")
    logger.info(f"Method: {request.method}")
    logger.info(f"Content-Type: {request.content_type}")
    logger.info(f"{'='*50}")
    
    try:
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            }, status=400)
            
        face_encoding = data.get('face_encoding')
        
        logger.info(f" Face encoding details: {type(face_encoding)}, length: {len(face_encoding) if face_encoding else 0}")
        
        if not face_encoding:
            logger.error(" No face encoding provided")
            return JsonResponse({
                'success': False,
                'error': 'No face encoding provided'
            }, status=400)
        
        if not isinstance(face_encoding, list) or len(face_encoding) != 128:
            logger.error(f" Invalid face encoding format: {type(face_encoding)}, length: {len(face_encoding) if hasattr(face_encoding, '__len__') else 'unknown'}")
            return JsonResponse({
                'success': False,
                'error': 'Invalid face encoding format (expected 128-dimensional array)'
            }, status=400)
        
        from .models import Student
        
        logger.info(" Checking database for students...")
        
        total_students = Student.objects.count()
        logger.info(f" Total students in database: {total_students}")
        
        if total_students > 0:
            sample_students = Student.objects.all()[:3]
            for student in sample_students:
                logger.info(f" Sample student: {student.student_id} - {student.name}")
        
        if total_students == 0:
            logger.warning("No students found in database")
            return JsonResponse({
                'success': False,
                'message': 'No students found in database. Please add students first.',
                'total_students': 0
            })
        else:
            # FIRST: Check if day is finished (before face recognition)
            from .models import Attendance
            from datetime import datetime
            
            # Check if this is a checkout request (from checkout button)
            is_checkout_request = data.get('checkout_request', False)
            
            # Check day status first
            current_time = datetime.now().time()
            day_status = Attendance.get_attendance_status_by_time(current_time)
            
            if day_status == 'day_finished' and not is_checkout_request:
                logger.warning("🚫 Day finished: Scanning not allowed after 2:00 PM")
                return JsonResponse({
                    'success': False,
                    'message': 'The day is finished! You cannot scan your face after 2:00 PM.',
                    'day_finished': True,
                    'time': current_time.strftime('%H:%M:%S'),
                    'security': 'DAY FINISHED: No scanning allowed after 2:00 PM',
                    'total_students': total_students
                })
            
            logger.info(" Starting face recognition comparison...")
            
            try:
                student = Student.find_by_face(face_encoding, threshold=0.9298)
                logger.info(f" Face recognition result: {student.name if student else 'Not found'}")
            except Exception as recognition_error:
                logger.error(f" Face recognition error: {recognition_error}")
                import traceback
                traceback.print_exc()
                student = None
            
            if student:
                logger.info(f" Student recognized: {student.name} ({student.student_id})")
                
                if is_checkout_request:
                    # Mark manual checkout
                    attendance_result = Attendance.mark_automatic_attendance(
                        student=student,
                        confidence=0.95,
                        notes='Manual checkout via face recognition',
                        force_checkout=True
                    )
                else:
                    # Mark automatic attendance
                    attendance_result = Attendance.mark_automatic_attendance(
                        student=student,
                        confidence=0.95,
                        notes='Automatic attendance via face recognition'
                    )
                
                if attendance_result['success']:
                    logger.info(f"✅ Attendance marked: {attendance_result['status']} at {attendance_result['time']}")
                    return JsonResponse({
                        'success': True,
                        'student': {
                            'id': student.id,
                            'student_id': student.student_id,
                            'name': student.name,
                            'first_name': student.first_name,
                            'last_name': student.last_name,
                            'email': student.email,
                            'phone': student.phone,
                            'class_name': student.class_name,
                            'section': student.section
                        },
                        'attendance': {
                            'status': attendance_result['status'],
                            'time': attendance_result['time'],
                            'attendance_id': attendance_result['attendance_id'],
                            'confidence': attendance_result['confidence']
                        },
                        'confidence': 0.95,  
                        'message': f'Student recognized and attendance marked as {attendance_result["status"].title()}',
                        'security': 'ULTRA-STRICT validation passed',
                        'total_students': total_students
                    })
                else:
                    # Check if it's a day_finished case
                    if attendance_result.get('day_finished', False):
                        # Day is finished - prevent scanning
                        logger.warning(f"🚫 Day finished: {attendance_result['message']}")
                        return JsonResponse({
                            'success': False,
                            'student': {
                                'id': student.id,
                                'student_id': student.student_id,
                                'name': student.name,
                                'first_name': student.first_name,
                                'last_name': student.last_name,
                                'email': student.email,
                                'phone': student.phone,
                                'class_name': student.class_name,
                                'section': student.section
                            },
                            'message': attendance_result['message'],
                            'day_finished': True,
                            'time': attendance_result.get('time', ''),
                            'security': 'DAY FINISHED: No scanning allowed after 2:00 PM',
                            'total_students': total_students
                        })
                    else:
                        # Attendance already marked (duplicate prevention)
                        logger.warning(f"⚠️ Duplicate attendance prevented: {attendance_result['message']}")
                        return JsonResponse({
                            'success': False,
                            'student': {
                                'id': student.id,
                                'student_id': student.student_id,
                                'name': student.name,
                                'first_name': student.first_name,
                                'last_name': student.last_name,
                                'email': student.email,
                                'phone': student.phone,
                                'class_name': student.class_name,
                                'section': student.section
                            },
                            'attendance': {
                                'status': attendance_result.get('existing_status', 'unknown'),
                                'time': attendance_result.get('existing_time', ''),
                                'duplicate_prevention': True
                            },
                            'message': attendance_result['message'],
                            'security': 'DUPLICATE PREVENTION: Attendance already marked today',
                            'total_students': total_students
                        })
            else:
                logger.warning(f" Unregistered face detected - proxy prevention active")
                return JsonResponse({
                    'success': False,
                    'message': 'Face not recognized - unregistered person detected',
                    'security': 'PROXY PREVENTION: Only registered students can be recognized',
                    'details': 'This face does not match any registered student with sufficient confidence',
                    'total_students': total_students
                })
        
    except Exception as e:
        logger.error(f" Student recognition error: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': 'Recognition failed'
        }, status=500)


@require_http_methods(["GET"])
def initialize_daily_attendance(request):
    """
    Initialize all students as absent for today
    This should be called daily to set default absent status
    """
    logger.info("📅 INITIALIZING DAILY ATTENDANCE")
    
    try:
        from .models import Attendance
        
        result = Attendance.initialize_daily_attendance()
        
        logger.info(f"✅ Daily attendance initialized: {result['message']}")
        return JsonResponse(result)
        
    except Exception as e:
        logger.error(f"❌ Error initializing daily attendance: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': 'Failed to initialize daily attendance'
        }, status=500)


@require_http_methods(["GET"])
def get_attendance_summary(request):
    """
    Get attendance summary for today
    """
    logger.info("📊 GETTING ATTENDANCE SUMMARY")
    
    try:
        from .models import Attendance
        
        # Get date from query parameter or use today
        date_param = request.GET.get('date')
        if date_param:
            from datetime import datetime
            date = datetime.strptime(date_param, '%Y-%m-%d').date()
        else:
            date = None
        
        summary = Attendance.get_daily_attendance_summary(date)
        
        logger.info(f"✅ Attendance summary retrieved: {summary['scanned']}/{summary['total_students']} scanned")
        return JsonResponse({
            'success': True,
            'summary': summary
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting attendance summary: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': 'Failed to get attendance summary'
        }, status=500)


@require_http_methods(["POST"])
def manual_attendance_mark(request):
    """
    Manually mark attendance for a student
    """
    logger.info("✏️ MANUAL ATTENDANCE MARKING")
    
    try:
        data = json.loads(request.body)
        student_id = data.get('student_id')
        status = data.get('status', 'present')  # present, late, absent
        notes = data.get('notes', '')
        
        if not student_id:
            return JsonResponse({
                'success': False,
                'error': 'Student ID is required'
            }, status=400)
        
        from .models import Student, Attendance
        from datetime import date
        
        try:
            student = Student.objects.get(student_id=student_id)
        except Student.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Student not found'
            }, status=404)
        
        # Check if attendance already exists for today
        today = date.today()
        existing_attendance = Attendance.objects.filter(
            student=student,
            date=today
        ).first()
        
        if existing_attendance:
            # Update existing attendance
            existing_attendance.status = status
            existing_attendance.notes = notes
            existing_attendance.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Attendance updated for {student.name}',
                'attendance': {
                    'status': status,
                    'time': existing_attendance.timestamp.strftime('%H:%M:%S'),
                    'attendance_id': existing_attendance.id
                }
            })
        else:
            # Create new attendance record
            attendance = Attendance.objects.create(
                student=student,
                date=today,
                status=status,
                confidence=1.0,  # Manual marking has 100% confidence
                notes=notes or f'Manual attendance - {status.title()}'
            )
            
            return JsonResponse({
                'success': True,
                'message': f'Attendance marked for {student.name}',
                'attendance': {
                    'status': status,
                    'time': attendance.timestamp.strftime('%H:%M:%S'),
                    'attendance_id': attendance.id
                }
            })
        
    except Exception as e:
        logger.error(f"❌ Error in manual attendance marking: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': 'Failed to mark attendance'
        }, status=500)