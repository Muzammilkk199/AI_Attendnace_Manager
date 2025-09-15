from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
import json

class StudentSearchTestCase(TestCase):
    def setUp(self):
        """Set up test data"""
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Create a test client
        self.client = Client()
        
        # Login the user
        self.client.login(username='testuser', password='testpass123')
    
    def test_search_students_endpoint(self):
        """Test the search students API endpoint"""
        # Test search endpoint exists and returns JSON
        response = self.client.get('/api/students/search/?q=test')
        
        # Should return 200 OK
        self.assertEqual(response.status_code, 200)
        
        # Should return JSON
        self.assertEqual(response['Content-Type'], 'application/json')
        
        # Parse JSON response
        data = json.loads(response.content)
        
        # Should have success field
        self.assertIn('success', data)
        
        # Should have students field
        self.assertIn('students', data)
        
        # Should have stats fields
        self.assertIn('total_students', data)
        self.assertIn('active_students', data)
        self.assertIn('inactive_students', data)
    
    def test_search_students_empty_query(self):
        """Test search with empty query returns all students"""
        response = self.client.get('/api/students/search/?q=')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertTrue(data['success'])
    
    def test_search_students_no_query(self):
        """Test search without query parameter"""
        response = self.client.get('/api/students/search/')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertTrue(data['success'])
