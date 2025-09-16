from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import json
from .mongodb_manager import StudentMongoDBManager, AttendanceMongoDBManager


class Student(models.Model):
    student_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    class_name = models.CharField(max_length=50, blank=True, null=True)
    section = models.CharField(max_length=20, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    
    def __str__(self):
        return f"{self.name} ({self.student_id})"
    
    def save(self, *args, **kwargs):
        if not self.name and self.first_name and self.last_name:
            self.name = f"{self.first_name} {self.last_name}"
        super().save(*args, **kwargs)
        # Also save to MongoDB
        self.save_to_mongodb()
    
    def save_to_mongodb(self):
        """Save student data to MongoDB"""
        try:
            mongo = StudentMongoDBManager()
            data = {
                'student_id': self.student_id,
                'name': self.name,
                'first_name': self.first_name,
                'last_name': self.last_name,
                'email': self.email,
                'phone': self.phone,
                'class_name': self.class_name,
                'section': self.section,
                'is_active': self.is_active,
                'django_id': self.id,
                'created_at': self.created_at.isoformat() if hasattr(self, 'created_at') else None
            }
            
            print(f"💾 Saving student to MongoDB: {data}")
            
            existing = mongo.find_by_student_id(self.student_id)
            if existing:
                result = mongo.update(existing['id'], **data)
                print(f"✅ Updated existing MongoDB student record: {result}")
                return result
            else:
                result = mongo.create(**data)
                print(f"✅ Created new MongoDB student record: {result}")
                return result
        except Exception as e:
            print(f"❌ Error saving student to MongoDB: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def save_embedding(self, embedding):
        """Save face embedding to MongoDB"""
        try:
            mongo = StudentMongoDBManager()
            data = {
                'student_id': self.student_id,
                'name': self.name,
                'first_name': self.first_name,
                'last_name': self.last_name,
                'email': self.email,
                'phone': self.phone,
                'class_name': self.class_name,
                'section': self.section,
                'embedding': embedding,
                'is_active': self.is_active,
                'django_id': self.id
            }
            
            print(f"💾 Attempting to save face embedding to MongoDB: {self.student_id}")
            
            existing = mongo.find_by_student_id(self.student_id)
            if existing:
                result = mongo.update(existing['id'], **data)
                print(f"✅ Updated existing MongoDB record with embedding: {result}")
                return result
            else:
                result = mongo.create(**data)
                print(f"✅ Created new MongoDB record with embedding: {result}")
                return result
        except Exception as e:
            print(f"❌ Error saving embedding to MongoDB: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_embedding(self):
        """Get face embedding from MongoDB"""
        try:
            mongo = StudentMongoDBManager()
            data = mongo.find_by_student_id(self.student_id)
            return data.get('embedding') if data else None
        except Exception as e:
            print(f"❌ Error getting embedding from MongoDB: {e}")
            return None
    
    def find_similar_faces(self, embedding, threshold=0.8):
        """Find similar faces in MongoDB"""
        try:
            mongo = StudentMongoDBManager()
            return mongo.find_similar_faces(embedding, threshold)
        except Exception as e:
            print(f"❌ Error finding similar faces: {e}")
            return []
    
    @classmethod
    def find_by_face(cls, embedding, threshold=0.9298):
        """
        ULTRA-STRICT face recognition to prevent unregistered faces from matching
        """
        print(f"\n{'='*60}")
        print(f"🔍 ULTRA-STRICT FIND_BY_FACE METHOD CALLED")
        print(f"📊 Embedding type: {type(embedding)}, length: {len(embedding) if embedding else 0}")
        print(f"📊 ULTRA-STRICT Threshold: {threshold}")
        print(f"{'='*60}")
        
        try:
            print("🔍 Connecting to MongoDB...")
            mongo = StudentMongoDBManager()
            
            if not mongo.connected:
                print("❌ MongoDB not connected - cannot perform face recognition")
                return None
            
            print("✅ MongoDB connected, searching for similar faces with ULTRA-STRICT criteria...")
            faces = mongo.find_similar_faces(embedding, threshold)
            print(f"📈 Found {len(faces) if faces else 0} similar faces with ultra-strict criteria")
            
        except Exception as e:
            print(f"❌ Error connecting to MongoDB: {e}")
            import traceback
            traceback.print_exc()
            return None
        
        if faces:
            print(f"🗺️ Processing {len(faces)} face matches...")
            for i, match in enumerate(faces):
                print(f"  📋 Match {i+1}: {match.get('name', 'Unknown')} (Django ID: {match.get('django_id', 'None')})")
            
            best_match = faces[0]
            similarity_score = best_match.get('similarity', 0)
            confidence_level = best_match.get('confidence', 'UNKNOWN')
            django_id = best_match.get('django_id')
            
            # ULTRA-STRICT validation to prevent unregistered face matches
            print(f"🔍 VALIDATION: Similarity: {similarity_score:.3f}, Confidence: {confidence_level}")
            
            # Only accept matches with very high confidence (92.98% threshold)
            if similarity_score >= 0.9298 and confidence_level in ['VERY_HIGH', 'HIGH']:
                if django_id:
                    print(f"🎯 Best match Django ID: {django_id}")
                    try:
                        student = cls.objects.get(id=django_id)
                        print(f"✅ ULTRA-STRICT MATCH: {student.name} ({student.student_id}) - Similarity: {similarity_score:.3f}")
                        return student
                    except cls.DoesNotExist:
                        print(f"❌ Student with Django ID {django_id} not found in Django database")
                    except Exception as e:
                        print(f"❌ Error retrieving student from Django DB: {e}")
                else:
                    print("❌ Best match has no Django ID")
            else:
                print(f"❌ REJECTED: Similarity {similarity_score:.3f} < 0.9298 or confidence {confidence_level} insufficient")
                print("Unregistered face detected and rejected")
        else:
            print("🚫 No similar faces found with ultra-strict criteria")
            print("No registered face matches found")
        
        print("🚫 Returning None - unregistered face or insufficient match quality")
        return None


class Attendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('late', 'Late'),
        ('absent', 'Absent'),
        ('checkout', 'Checkout'),
        ('day_finished', 'Day Finished'),
        ('day_locked', 'Day Locked'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='present')
    timestamp = models.DateTimeField(auto_now_add=True)
    confidence = models.FloatField(default=0.0)
    notes = models.TextField(blank=True, null=True)
    
    
    def __str__(self):
        return f"{self.student.name} - {self.date} ({self.status})"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.save_to_mongodb()
    
    def save_to_mongodb(self):
        """Save attendance data to MongoDB"""
        try:
            mongo = AttendanceMongoDBManager()
            data = {
                'student_id': self.student.student_id,
                'student_name': self.student.name,
                'date': self.date.isoformat(),
                'status': self.status,
                'confidence': self.confidence,
                'notes': self.notes,
                'timestamp': self.timestamp.isoformat(),
                'django_id': self.id
            }
            
            existing = mongo.get_by_field('django_id', self.id)
            if existing:
                return mongo.update(existing['id'], **data)
            else:
                return mongo.create(**data)
        except Exception as e:
            print(f"❌ Error saving attendance to MongoDB: {e}")
            return None
    
    def save_image_data(self, image_data):
        """Save image data to MongoDB"""
        try:
            mongo = AttendanceMongoDBManager()
            data = mongo.get_by_field('django_id', self.id)
            if data:
                return mongo.update(data['id'], image_data=image_data)
            else:
                return self.save_to_mongodb()
        except Exception as e:
            print(f"❌ Error saving image data: {e}")
            return None
    
    def get_image_data(self):
        """Get image data from MongoDB"""
        try:
            mongo = AttendanceMongoDBManager()
            data = mongo.get_by_field('django_id', self.id)
            return data.get('image_data') if data else None
        except Exception as e:
            print(f"❌ Error getting image data: {e}")
            return None
    
    @classmethod
    def get_attendance_by_date(cls, date):
        """Get attendance records by date"""
        try:
            mongo = AttendanceMongoDBManager()
            mongo_records = mongo.get_attendance_by_date(date)
        except Exception as e:
            print(f"❌ Error getting MongoDB attendance: {e}")
            mongo_records = []
        
        records = cls.objects.filter(date=date)
        return records
    
    @classmethod
    def get_attendance_stats(cls, start_date=None, end_date=None):
        """Get attendance statistics"""
        try:
            mongo = AttendanceMongoDBManager()
            return mongo.get_attendance_stats(start_date, end_date)
        except Exception as e:
            print(f"❌ Error getting attendance stats: {e}")
            return {}
    
    def get_attendance_rate(self):
        """Calculate attendance rate for student"""
        # TODO: implement attendance rate calculation
        pass
    
    @classmethod
    def get_attendance_status_by_time(cls, current_time=None, force_checkout=False, existing_status=None):
        """
        Determine attendance status based on current time and existing status
        - Before 8:00 AM: Present
        - 8:00 AM to 2:00 PM: Late
        - After 2:00 PM: Checkout (only if student was present/late) or Day Finished
        - Force checkout: Override time logic for manual checkout
        - existing_status: Current attendance status to determine checkout eligibility
        """
        from datetime import datetime, time
        import logging
        
        logger = logging.getLogger(__name__)
        
        try:
            if current_time is None:
                current_time = datetime.now().time()
            
            # Log the input type for debugging
            logger.info(f"get_attendance_status_by_time called with current_time type: {type(current_time)}, value: {current_time}")
            
            # Handle string time input (convert to time object)
            if isinstance(current_time, str):
                try:
                    # Try to parse time string (HH:MM:SS or HH:MM format)
                    if len(current_time.split(':')) == 3:
                        hour, minute, second = map(int, current_time.split(':'))
                        current_time = time(hour, minute, second)
                    elif len(current_time.split(':')) == 2:
                        hour, minute = map(int, current_time.split(':'))
                        current_time = time(hour, minute)
                    else:
                        # Fallback to current time if parsing fails
                        current_time = datetime.now().time()
                except (ValueError, TypeError) as e:
                    logger.error(f"Error parsing time string '{current_time}': {e}")
                    # Fallback to current time if parsing fails
                    current_time = datetime.now().time()
            
            # Ensure current_time is a time object
            if not isinstance(current_time, time):
                logger.error(f"current_time is not a time object: {type(current_time)}")
                current_time = datetime.now().time()
            
            # If force checkout is requested, return checkout regardless of time
            if force_checkout:
                return 'checkout'
            
            # Define time thresholds
            morning_cutoff = time(8, 0)    # 8:00 AM
            checkout_cutoff = time(14, 0)  # 2:00 PM (checkout time starts)
            day_end = time(14, 0)           # 2:00 PM (midnight) - day finished
            
            logger.info(f"Comparing current_time {current_time} with morning_cutoff {morning_cutoff}, checkout_cutoff {checkout_cutoff}, and day_end {day_end}")
            logger.info(f"Existing status: {existing_status}")
            
            if current_time <= morning_cutoff:
                return 'present'
            elif current_time < checkout_cutoff:
                return 'late'
            elif current_time >= checkout_cutoff:
                # After 2:00 PM - checkout time, but only if student was present/late
                # Check if it's after midnight (next day)
                if current_time.hour >= 0 and current_time.hour < 8:  # Between midnight and 8 AM (next day)
                    return 'day_finished'  # After 2:00 PM - day is finished
                else:
                    # Between 2 PM and midnight - checkout time
                    if existing_status in ['present', 'late']:
                        return 'checkout'
                    elif existing_status == 'absent':
                        return 'day_finished'  # Absent students get day finished message
                    else:
                        return 'checkout'  # New students can checkout
            else:
                return 'day_finished'  # After 2:00 PM - day is finished
                
        except Exception as e:
            logger.error(f"Error in get_attendance_status_by_time: {e}")
            logger.error(f"current_time type: {type(current_time)}, value: {current_time}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            # Return a safe default
            return 'day_finished'
    
    @classmethod
    def mark_automatic_attendance(cls, student, confidence=0.95, notes=None, force_checkout=False):
        """
        Automatically mark attendance for a student based on current time
        Updates existing attendance if student was previously marked as absent
        """
        from datetime import date, datetime
        
        today = date.today()
        current_time = datetime.now().time()
        
        # Check if student already has attendance for today
        existing_attendance = cls.objects.filter(
            student=student,
            date=today
        ).first()
        
        # Determine status based on time, force checkout flag, and existing status
        existing_status = existing_attendance.status if existing_attendance else None
        status = cls.get_attendance_status_by_time(current_time, force_checkout, existing_status)
        
        # If day is finished (after 12:00 AM), prevent attendance marking
        if status == 'day_finished' and not force_checkout:
            return {
                'success': False,
                'message': 'The day is finished! You cannot scan your face after 2:00 PM.',
                'status': 'day_finished',
                'time': current_time.strftime('%H:%M:%S'),
                'day_finished': True,
                'error_type': 'after_hours'
            }
        
        # If day is finished (absent student trying to checkout during checkout hours), prevent attendance marking
        if status == 'day_finished' and existing_status == 'absent' and not force_checkout:
            return {
                'success': False,
                'message': f'Day finished for {student.name}! You were marked absent today.',
                'status': 'day_finished',
                'time': current_time.strftime('%H:%M:%S'),
                'day_finished': True,
                'error_type': 'absent_student_checkout',
                'existing_status': existing_status
            }
        
        if existing_attendance:
            # If student was previously marked as absent, update to present/late/checkout
            if existing_attendance.status == 'absent':
                existing_attendance.status = status
                existing_attendance.confidence = confidence
                existing_attendance.notes = notes or f'Automatic attendance - {status.title()}'
                existing_attendance.timestamp = datetime.now()
                existing_attendance.save()
                
                return {
                    'success': True,
                    'message': f'Attendance updated for {student.name} from ABSENT to {status.upper()}',
                    'status': status,
                    'time': current_time.strftime('%H:%M:%S'),
                    'attendance_id': existing_attendance.id,
                    'confidence': confidence,
                    'updated_from_absent': True
                }
            # Allow checkout even if already marked present/late (end of day checkout)
            elif status == 'checkout' and existing_attendance.status in ['present', 'late']:
                existing_attendance.status = 'checkout'
                existing_attendance.confidence = confidence
                existing_attendance.notes = notes or f'End of day checkout - {status.title()}'
                existing_attendance.timestamp = datetime.now()
                existing_attendance.save()
                
                return {
                    'success': True,
                    'message': f'Checkout marked for {student.name} (was {existing_attendance.status.upper()})',
                    'status': status,
                    'time': current_time.strftime('%H:%M:%S'),
                    'attendance_id': existing_attendance.id,
                    'confidence': confidence,
                    'checkout_update': True
                }
            # Allow manual checkout regardless of time or existing status
            elif notes and 'checkout' in notes.lower():
                existing_attendance.status = 'checkout'
                existing_attendance.confidence = confidence
                existing_attendance.notes = notes or f'Manual checkout - {status.title()}'
                existing_attendance.timestamp = datetime.now()
                existing_attendance.save()
                
                return {
                    'success': True,
                    'message': f'Manual checkout marked for {student.name} (was {existing_attendance.status.upper()})',
                    'status': 'checkout',
                    'time': current_time.strftime('%H:%M:%S'),
                    'attendance_id': existing_attendance.id,
                    'confidence': confidence,
                    'manual_checkout': True
                }
            else:
                # Student already has attendance - prevent duplicate
                return {
                    'success': False,
                    'message': f'Attendance already marked for {student.name} today',
                    'existing_status': existing_attendance.status,
                    'existing_time': existing_attendance.timestamp.strftime('%H:%M:%S'),
                    'duplicate_prevention': True
                }
        
        # Create new attendance record
        attendance = cls.objects.create(
            student=student,
            date=today,
            status=status,
            confidence=confidence,
            notes=notes or f'Automatic attendance - {status.title()}'
        )
        
        return {
            'success': True,
            'message': f'Attendance marked successfully for {student.name}',
            'status': status,
            'time': current_time.strftime('%H:%M:%S'),
            'attendance_id': attendance.id,
            'confidence': confidence
        }
    
    @classmethod
    def initialize_daily_attendance(cls, date=None):
        """
        Initialize all students as absent for a given date
        This should be run daily to set default absent status
        Only creates new records for students who don't have attendance yet
        """
        from datetime import date as date_class
        
        if date is None:
            date = date_class.today()
        
        # Get all active students
        students = Student.objects.filter(is_active=True)
        
        initialized_count = 0
        already_marked_count = 0
        
        for student in students:
            # Check if attendance already exists for this date
            existing = cls.objects.filter(
                student=student,
                date=date
            ).first()
            
            if existing:
                # Student already has attendance - don't change it
                already_marked_count += 1
            else:
                # Create new absent attendance record
                cls.objects.create(
                    student=student,
                    date=date,
                    status='absent',
                    confidence=0.0,
                    notes='Default absent status - not scanned today'
                )
                initialized_count += 1
        
        return {
            'success': True,
            'message': f'Initialized {initialized_count} new students as ABSENT, {already_marked_count} already had attendance for {date}',
            'date': date.isoformat(),
            'initialized_count': initialized_count,
            'already_marked_count': already_marked_count,
            'total_students': students.count()
        }
    
    @classmethod
    def get_daily_attendance_summary(cls, date=None):
        """
        Get attendance summary for a specific date
        """
        from datetime import date as date_class
        
        if date is None:
            date = date_class.today()
        
        attendance_records = cls.objects.filter(date=date)
        
        summary = {
            'date': date.isoformat(),
            'total_students': Student.objects.filter(is_active=True).count(),
            'present': attendance_records.filter(status='present').count(),
            'late': attendance_records.filter(status='late').count(),
            'absent': attendance_records.filter(status='absent').count(),
            'checkout': attendance_records.filter(status='checkout').count(),
            'day_finished': attendance_records.filter(status='day_finished').count(),
            'scanned': attendance_records.filter(status__in=['present', 'late', 'checkout']).count(),
            'not_scanned': 0
        }
        
        summary['not_scanned'] = summary['total_students'] - summary['scanned']
        
        return summary