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
    
    def save_embedding(self, embedding):
        # save face data to mongo
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
            
            existing = mongo.find_by_student_id(self.student_id)
            if existing:
                return mongo.update(existing['id'], **data)
            else:
                return mongo.create(**data)
        except Exception as e:
            print(f"Error saving embedding: {e}")
            return None
    
    def get_embedding(self):
        try:
            mongo = StudentMongoDBManager()
            data = mongo.find_by_student_id(self.student_id)
            return data.get('embedding') if data else None
        except:
            return None
    
    def find_similar_faces(self, embedding, threshold=0.8):
        try:
            mongo = StudentMongoDBManager()
            return mongo.find_similar_faces(embedding, threshold)
        except:
            return []
    
    @classmethod
    def find_by_face(cls, embedding, threshold=0.8):
        try:
            mongo = StudentMongoDBManager()
            faces = mongo.find_similar_faces(embedding, threshold)
        except:
            return None
        
        if faces:
            match = faces[0]
            if match.get('django_id'):
                try:
                    return cls.objects.get(id=match['django_id'])
                except:
                    pass
        
        return None


class Attendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('late', 'Late'),
        ('absent', 'Absent'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Absent')
    timestamp = models.DateTimeField(auto_now_add=True)
    confidence = models.FloatField(default=0.0)
    notes = models.TextField(blank=True, null=True)
    
    
    def __str__(self):
        return f"{self.student.name} - {self.date} ({self.status})"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.save_to_mongodb()
    
    def save_to_mongodb(self):
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
        except:
            return None
    
    def save_image_data(self, image_data):
        try:
            mongo = AttendanceMongoDBManager()
            data = mongo.get_by_field('django_id', self.id)
            if data:
                return mongo.update(data['id'], image_data=image_data)
            else:
                return self.save_to_mongodb()
        except:
            return None
    
    def get_image_data(self):
        try:
            mongo = AttendanceMongoDBManager()
            data = mongo.get_by_field('django_id', self.id)
            return data.get('image_data') if data else None
        except:
            return None
    
    @classmethod
    def get_attendance_by_date(cls, date):
        try:
            mongo = AttendanceMongoDBManager()
            mongo_records = mongo.get_attendance_by_date(date)
        except:
            mongo_records = []
        
        records = cls.objects.filter(date=date)
        return records
    
    @classmethod
    def get_attendance_stats(cls, start_date=None, end_date=None):
        try:
            mongo = AttendanceMongoDBManager()
            return mongo.get_attendance_stats(start_date, end_date)
        except:
            return {}
    
    # TODO: add more stats methods later
    def get_attendance_rate(self):
        # incomplete - need to implement
        pass
