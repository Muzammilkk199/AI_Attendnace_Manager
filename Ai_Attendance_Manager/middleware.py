from django.shortcuts import redirect
from django.contrib.auth import logout
from django.urls import reverse
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class AuthenticationMiddleware:
    """
    Custom middleware to check authentication on every request
    and handle session validation
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Define public URLs that don't require authentication
        self.public_urls = [
            '/login/',
            '/logout/',
            '/forgot-password/',
            '/reset-password/',
            '/admin/',
            '/static/',
            '/media/',
        ]
        
        # Define API URLs that might need special handling
        self.api_urls = [
            '/api/',
        ]
    
    def __call__(self, request):
        # Check if the current path requires authentication
        if self.requires_authentication(request.path):
            # Check if user is authenticated
            if not request.user.is_authenticated:
                logger.warning(f"Unauthenticated access attempt to: {request.path}")
                # For AJAX requests, return JSON response
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    from django.http import JsonResponse
                    return JsonResponse({
                        'success': False,
                        'message': 'Authentication required',
                        'redirect_url': reverse('login')
                    }, status=401)
                # For regular requests, redirect to login
                return redirect('login')
            
            # Check if user session is valid
            if not self.is_session_valid(request):
                logger.warning(f"Invalid session for user: {request.user.username}")
                logout(request)
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    from django.http import JsonResponse
                    return JsonResponse({
                        'success': False,
                        'message': 'Session expired. Please login again.',
                        'redirect_url': reverse('login')
                    }, status=401)
                return redirect('login')
        
        response = self.get_response(request)
        return response
    
    def requires_authentication(self, path):
        """
        Check if the given path requires authentication
        """
        # Check if it's a public URL
        for public_url in self.public_urls:
            if path.startswith(public_url):
                return False
        
        # Check if it's an API URL (might need special handling)
        for api_url in self.api_urls:
            if path.startswith(api_url):
                # For now, require authentication for all API calls
                # You can modify this based on your needs
                return True
        
        # All other URLs require authentication
        return True
    
    def is_session_valid(self, request):
        """
        Check if the user's session is valid
        """
        try:
            # Check if user exists and is active
            if not request.user.is_active:
                return False
            
            # Check if session has expired
            if not request.session.get('_auth_user_id'):
                return False
            
            # You can add more session validation logic here
            # For example, check last activity time, IP address, etc.
            
            return True
        except Exception as e:
            logger.error(f"Session validation error: {e}")
            return False
