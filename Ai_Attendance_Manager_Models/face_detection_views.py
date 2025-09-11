"""
Django Views for Python Face Detection
Handles real-time face detection requests from the frontend
"""

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
    """
    API endpoint for real-time face detection
    Accepts base64 image data and returns face detection results
    """
    
    def post(self, request):
        try:
            # Parse JSON data
            data = json.loads(request.body)
            base64_image = data.get('image')
            
            if not base64_image:
                return JsonResponse({
                    'success': False,
                    'error': 'No image data provided'
                }, status=400)
            
            # Process image with Python face detection
            result = detect_faces_in_image(base64_image)
            
            # Return results
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
    """
    Simple function-based view for face detection
    """
    try:
        # Parse JSON data
        data = json.loads(request.body)
        base64_image = data.get('image')
        
        if not base64_image:
            return JsonResponse({
                'success': False,
                'error': 'No image data provided'
            }, status=400)
        
        # Process image with Python face detection
        result = detect_faces_in_image(base64_image)
        
        # Return results
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
@require_http_methods(["GET"])
def face_detection_status(request):
    """
    Check if face detection system is working
    """
    try:
        from .python_face_detection import face_detector
        
        return JsonResponse({
            'success': True,
            'status': 'ready' if face_detector.initialized else 'not_initialized',
            'message': 'Python face detection system is ready' if face_detector.initialized else 'Face detection system not initialized'
        })
        
    except Exception as e:
        logger.error(f"Status check error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Status check failed'
        }, status=500)
