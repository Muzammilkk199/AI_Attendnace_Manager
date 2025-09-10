"""
Custom MongoDB Manager for Django Models
This allows you to use MongoDB features like embeddings while maintaining Django ORM-like interface
"""

from django.conf import settings
from pymongo import MongoClient
from bson import ObjectId
import json
from datetime import datetime
from typing import List, Dict, Any, Optional


class MongoDBManager:
    """Custom manager for MongoDB operations"""
    
    def __init__(self, collection_name: str):
        self.collection_name = collection_name
        self.client = None
        self.db = None
        self.collection = None
        self.connected = False
        
        try:
            self.client = MongoClient(settings.MONGODB_URI, serverSelectionTimeoutMS=5000)
            self.db = self.client[settings.MONGODB_DB]
            self.collection = self.db[collection_name]
            # Test connection
            self.client.admin.command('ping')
            self.connected = True
            print(f"MongoDB connection successful for collection: {collection_name}")
        except Exception as e:
            print(f"MongoDB connection failed for collection {collection_name}: {e}")
            print("Continuing without MongoDB - data will be saved to SQLite only")
            self.connected = False
    
    def create(self, **kwargs):
        """Create a new document in MongoDB"""
        if not self.connected:
            print(f"MongoDB not connected - skipping create operation for {self.collection_name}")
            return None
            
        try:
            # Convert datetime objects to MongoDB format
            for key, value in kwargs.items():
                if isinstance(value, datetime):
                    kwargs[key] = value
            
            # Add created_at timestamp
            kwargs['created_at'] = datetime.now()
            
            result = self.collection.insert_one(kwargs)
            return self.get_by_id(result.inserted_id)
        except Exception as e:
            print(f"Error creating document in MongoDB: {e}")
            return None
    
    def get_by_id(self, doc_id):
        """Get document by MongoDB ObjectId"""
        if isinstance(doc_id, str):
            doc_id = ObjectId(doc_id)
        
        doc = self.collection.find_one({'_id': doc_id})
        if doc:
            doc['id'] = str(doc['_id'])
            del doc['_id']
        return doc
    
    def get_by_field(self, field: str, value: Any):
        """Get document by any field"""
        doc = self.collection.find_one({field: value})
        if doc:
            doc['id'] = str(doc['_id'])
            del doc['_id']
        return doc
    
    def get_all(self, filter_dict: Dict = None):
        """Get all documents with optional filter"""
        if filter_dict is None:
            filter_dict = {}
        
        docs = list(self.collection.find(filter_dict))
        for doc in docs:
            doc['id'] = str(doc['_id'])
            del doc['_id']
        return docs
    
    def update(self, doc_id, **kwargs):
        """Update document by ID"""
        if isinstance(doc_id, str):
            doc_id = ObjectId(doc_id)
        
        # Add updated_at timestamp
        kwargs['updated_at'] = datetime.now()
        
        result = self.collection.update_one(
            {'_id': doc_id},
            {'$set': kwargs}
        )
        return result.modified_count > 0
    
    def delete(self, doc_id):
        """Delete document by ID"""
        if isinstance(doc_id, str):
            doc_id = ObjectId(doc_id)
        
        result = self.collection.delete_one({'_id': doc_id})
        return result.deleted_count > 0
    
    def search_by_embedding(self, embedding: List[float], threshold: float = 0.8, limit: int = 10):
        """Search for similar faces using embedding similarity"""
        # This is a simplified similarity search
        # For production, you'd want to use MongoDB's vector search or a specialized vector database
        
        # Get all documents with embeddings
        docs = list(self.collection.find({'embedding': {'$exists': True}}))
        
        similar_docs = []
        for doc in docs:
            if 'embedding' in doc:
                # Calculate cosine similarity (simplified)
                similarity = self._cosine_similarity(embedding, doc['embedding'])
                if similarity >= threshold:
                    doc['similarity'] = similarity
                    doc['id'] = str(doc['_id'])
                    del doc['_id']
                    similar_docs.append(doc)
        
        # Sort by similarity and return top results
        similar_docs.sort(key=lambda x: x['similarity'], reverse=True)
        return similar_docs[:limit]
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        import math
        
        if len(vec1) != len(vec2):
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(a * a for a in vec2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    def count(self, filter_dict: Dict = None):
        """Count documents with optional filter"""
        if filter_dict is None:
            filter_dict = {}
        return self.collection.count_documents(filter_dict)
    
    def create_index(self, field: str, **kwargs):
        """Create index on a field"""
        return self.collection.create_index(field, **kwargs)


class StudentMongoDBManager(MongoDBManager):
    """Specialized manager for Student model"""
    
    def __init__(self):
        super().__init__('students')
    
    def find_by_student_id(self, student_id: str):
        """Find student by student_id"""
        return self.get_by_field('student_id', student_id)
    
    def find_similar_faces(self, embedding: List[float], threshold: float = 0.8):
        """Find students with similar face embeddings"""
        return self.search_by_embedding(embedding, threshold)
    
    def get_active_students(self):
        """Get all active students"""
        return self.get_all({'is_active': True})


class AttendanceMongoDBManager(MongoDBManager):
    """Specialized manager for Attendance model"""
    
    def __init__(self):
        super().__init__('attendance')
    
    def get_attendance_by_date(self, date):
        """Get attendance records for a specific date"""
        if isinstance(date, str):
            date = datetime.strptime(date, '%Y-%m-%d').date()
        
        return self.get_all({'date': date.isoformat()})
    
    def get_student_attendance(self, student_id: str, start_date=None, end_date=None):
        """Get attendance records for a specific student"""
        filter_dict = {'student_id': student_id}
        
        if start_date and end_date:
            filter_dict['date'] = {
                '$gte': start_date.isoformat(),
                '$lte': end_date.isoformat()
            }
        
        return self.get_all(filter_dict)
    
    def get_attendance_stats(self, start_date=None, end_date=None):
        """Get attendance statistics"""
        filter_dict = {}
        if start_date and end_date:
            filter_dict['date'] = {
                '$gte': start_date.isoformat(),
                '$lte': end_date.isoformat()
            }
        
        pipeline = [
            {'$match': filter_dict},
            {'$group': {
                '_id': '$status',
                'count': {'$sum': 1}
            }}
        ]
        
        return list(self.collection.aggregate(pipeline))
