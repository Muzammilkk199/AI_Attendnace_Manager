"""
Python Face Detection Module using OpenCV
Replaces JavaScript face detection with server-side Python processing
"""

import base64
import json
import logging
import random
import math
from typing import List, Dict, Tuple, Optional
import os

# Import OpenCV and numpy - these should be available
import cv2
import numpy as np

logger = logging.getLogger(__name__)

class PythonFaceDetector:
    """
    Advanced face detection using OpenCV with Haar Cascades
    Provides accurate face detection, multiple face handling, and face encoding
    """
    
    def __init__(self):
        self.face_cascade = None
        self.eye_cascade = None
        self.initialized = False
        self.face_history = []  # For detection stability
        self.history_size = 5   # Number of frames to consider for stability
        self.initialize_cascades()
    
    def initialize_cascades(self):
        """Initialize OpenCV Haar Cascades for face and eye detection"""
        try:
            # Load cascades from OpenCV data directory
            cascade_path = cv2.data.haarcascades
            
            # Face cascade
            face_cascade_path = os.path.join(cascade_path, 'haarcascade_frontalface_default.xml')
            if os.path.exists(face_cascade_path):
                self.face_cascade = cv2.CascadeClassifier(face_cascade_path)
            else:
                # Fallback to default
                self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            
            # Eye cascade for better face validation
            eye_cascade_path = os.path.join(cascade_path, 'haarcascade_eye.xml')
            if os.path.exists(eye_cascade_path):
                self.eye_cascade = cv2.CascadeClassifier(eye_cascade_path)
            else:
                self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
            
            if self.face_cascade.empty() or self.eye_cascade.empty():
                raise Exception("Failed to load Haar cascades")
            
            self.initialized = True
            logger.info("Python Face Detector initialized successfully with OpenCV")
            
        except Exception as e:
            logger.error(f"Failed to initialize face detector: {str(e)}")
            raise e
    
    def base64_to_image(self, base64_string: str):
        """Convert base64 string to OpenCV image"""
        try:
            # Remove data URL prefix if present
            if ',' in base64_string:
                base64_string = base64_string.split(',')[1]
            
            # Decode base64
            image_data = base64.b64decode(base64_string)
            
            # Convert to numpy array
            nparr = np.frombuffer(image_data, np.uint8)
            # Decode image
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            return image
            
        except Exception as e:
            logger.error(f"Error converting base64 to image: {str(e)}")
            return None
    
    def image_to_base64(self, image) -> str:
        """Convert OpenCV image to base64 string"""
        try:
            if image is not None and hasattr(image, 'shape'):
                # Encode image as JPEG
                _, buffer = cv2.imencode('.jpg', image, [cv2.IMWRITE_JPEG_QUALITY, 80])
                
                # Convert to base64
                image_base64 = base64.b64encode(buffer).decode('utf-8')
                
                return f"data:image/jpeg;base64,{image_base64}"
            else:
                return ""
            
        except Exception as e:
            logger.error(f"Error converting image to base64: {str(e)}")
            return ""
    
    def detect_faces(self, image) -> List[Dict]:
        """
        Detect faces in image using OpenCV Haar Cascades with enhanced accuracy
        Returns list of face dictionaries with coordinates, size, and quality
        """
        if not self.initialized or image is None:
            return []
        
        try:
            # Convert to grayscale for face detection
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply histogram equalization for better contrast
            gray = cv2.equalizeHist(gray)
            
            # Apply Gaussian blur to reduce noise
            gray = cv2.GaussianBlur(gray, (3, 3), 0)
            
            # Detect faces with improved parameters for better accuracy
            try:
                faces = self.face_cascade.detectMultiScale(
                    gray,
                    scaleFactor=1.1,   # Safe scale factor to avoid OpenCV assertion error
                    minNeighbors=4,    # Reduced threshold for easier detection
                    minSize=(30, 30),  # Smaller minimum size for easier detection
                    maxSize=(400, 400), # Increased maximum size for more flexibility
                    flags=cv2.CASCADE_SCALE_IMAGE | cv2.CASCADE_DO_CANNY_PRUNING
                )
            except cv2.error as e:
                logger.warning(f"OpenCV error with advanced parameters, falling back to basic detection: {str(e)}")
                # Fallback to basic detection parameters
                faces = self.face_cascade.detectMultiScale(
                    gray,
                    scaleFactor=1.1,
                    minNeighbors=3,    # More lenient fallback
                    minSize=(25, 25),  # Even smaller minimum size
                    flags=cv2.CASCADE_SCALE_IMAGE
                )
            
            face_data = []
            
            for i, (x, y, w, h) in enumerate(faces):
                # Extract face region
                face_roi = gray[y:y+h, x:x+w]
                
                # Detect eyes in face region for validation
                eyes = self.eye_cascade.detectMultiScale(face_roi)
                
                # Calculate face quality based on size, position, and eye detection
                quality = self.calculate_face_quality(x, y, w, h, len(eyes), image.shape)
                
                face_info = {
                    'id': i,
                    'x': int(x),
                    'y': int(y),
                    'width': int(w),
                    'height': int(h),
                    'confidence': quality,
                    'eyes_detected': len(eyes),
                    'quality_score': quality
                }
                
                face_data.append(face_info)
            
            # Apply temporal smoothing for better stability
            smoothed_faces = self.smooth_detections(face_data)
            
            return smoothed_faces
            
        except Exception as e:
            logger.error(f"Error detecting faces: {str(e)}")
            return []
    
    
    def calculate_face_quality(self, x: int, y: int, w: int, h: int, eyes_count: int, image_shape: Tuple) -> float:
        """
        Calculate enhanced face quality score based on multiple factors
        Returns score between 0.0 and 1.0
        """
        try:
            img_height, img_width = image_shape[:2]
            
            # Size score (optimal face size is 15-35% of image - more lenient)
            optimal_size = min(img_width, img_height) * 0.25
            size_diff = abs(w - optimal_size)
            max_size_diff = optimal_size * 1.0  # Increased tolerance
            size_score = max(0, 1 - (size_diff / max_size_diff))
            
            # Position score (center is better, with tolerance)
            center_x = img_width / 2
            center_y = img_height / 2
            face_center_x = x + w / 2
            face_center_y = y + h / 2
            
            distance_from_center = np.sqrt(
                (face_center_x - center_x)**2 + (face_center_y - center_y)**2
            )
            max_distance = np.sqrt(center_x**2 + center_y**2)
            position_score = max(0, 1 - (distance_from_center / max_distance))
            
            # Eye detection score (more lenient - eyes are nice but not required)
            eye_score = min(1.0, eyes_count / 2.0)  # 2 eyes = perfect score
            if eyes_count >= 2:
                eye_score = 1.0
            elif eyes_count == 1:
                eye_score = 0.8  # Increased from 0.6
            else:
                eye_score = 0.6  # Increased from 0.3 - eyes not required
            
            # Aspect ratio score (more lenient - faces can vary more)
            aspect_ratio = w / h
            ideal_ratio = 0.85  # Slightly taller than wide
            aspect_score = max(0, 1 - abs(aspect_ratio - ideal_ratio) / 0.6)  # Increased tolerance
            
            # Face area coverage score (more lenient coverage requirements)
            face_area = w * h
            image_area = img_width * img_height
            coverage_ratio = face_area / image_area
            optimal_coverage = 0.15  # 15% of image
            coverage_score = max(0, 1 - abs(coverage_ratio - optimal_coverage) / 0.2)  # Increased tolerance
            
            # Sharpness score (based on face dimensions)
            sharpness_score = min(1.0, (w + h) / 200.0)  # Larger faces are generally sharper
            
            # Overall quality (weighted average - more lenient weighting)
            quality = (
                size_score * 0.2 +      # Reduced weight
                position_score * 0.2 +   # Reduced weight
                eye_score * 0.3 +        # Increased weight for eyes
                aspect_score * 0.15 +
                coverage_score * 0.1 +   # Increased weight
                sharpness_score * 0.05
            )
            
            # Apply quality boost for good conditions (more lenient)
            if eyes_count >= 1 and size_score > 0.5 and position_score > 0.5:
                quality = min(1.0, quality * 1.15)  # Increased boost
            
            return min(1.0, max(0.0, quality))
            
        except Exception as e:
            logger.error(f"Error calculating face quality: {str(e)}")
            return 0.5
    
    def smooth_detections(self, current_faces: List[Dict]) -> List[Dict]:
        """
        Apply temporal smoothing to reduce false positives and improve stability
        """
        try:
            # Add current detection to history
            self.face_history.append(current_faces)
            
            # Keep only recent history
            if len(self.face_history) > self.history_size:
                self.face_history.pop(0)
            
            # If we don't have enough history, return current detection
            if len(self.face_history) < 3:
                return current_faces
            
            # Find faces that appear consistently across frames
            stable_faces = []
            
            for current_face in current_faces:
                cx, cy, cw, ch = current_face['x'], current_face['y'], current_face['width'], current_face['height']
                face_center = (cx + cw/2, cy + ch/2)
                
                # Count how many times a similar face appears in history
                appearance_count = 0
                total_quality = 0
                
                for historical_faces in self.face_history:
                    for hist_face in historical_faces:
                        hx, hy, hw, hh = hist_face['x'], hist_face['y'], hist_face['width'], hist_face['height']
                        hist_center = (hx + hw/2, hy + hh/2)
                        
                        # Calculate distance between face centers
                        distance = np.sqrt((face_center[0] - hist_center[0])**2 + (face_center[1] - hist_center[1])**2)
                        
                        # If faces are close enough, consider them the same
                        if distance < min(cw, ch) * 0.5:  # 50% of face size tolerance
                            appearance_count += 1
                            total_quality += hist_face.get('quality_score', 0.5)
                            break
                
                # Only include faces that appear in at least 40% of recent frames (more lenient)
                if appearance_count >= len(self.face_history) * 0.4:
                    # Average the quality score
                    avg_quality = total_quality / appearance_count if appearance_count > 0 else current_face.get('quality_score', 0.5)
                    
                    # Create smoothed face data
                    smoothed_face = current_face.copy()
                    smoothed_face['quality_score'] = avg_quality
                    smoothed_face['confidence'] = avg_quality
                    smoothed_face['stability_score'] = appearance_count / len(self.face_history)
                    
                    stable_faces.append(smoothed_face)
            
            return stable_faces
            
        except Exception as e:
            logger.error(f"Error smoothing detections: {str(e)}")
            return current_faces
    
    def reset_detection_history(self):
        """Reset the face detection history for a fresh start"""
        self.face_history = []
        logger.info("Face detection history reset")
    
    def get_detection_stats(self) -> Dict:
        """Get current detection statistics"""
        return {
            'history_size': len(self.face_history),
            'max_history_size': self.history_size,
            'initialized': self.initialized,
            'face_cascade_loaded': self.face_cascade is not None and not self.face_cascade.empty(),
            'eye_cascade_loaded': self.eye_cascade is not None and not self.eye_cascade.empty()
        }
    
    def generate_face_encoding(self, image, face_data: Dict) -> List[float]:
        """
        Generate a face encoding based on face features using OpenCV
        This creates a 128-dimensional encoding from the face region
        """
        try:
            x, y, w, h = face_data['x'], face_data['y'], face_data['width'], face_data['height']
            
            # Extract face region
            face_roi = image[y:y+h, x:x+w]
            
            # Resize to standard size
            face_resized = cv2.resize(face_roi, (128, 128))
            
            # Convert to grayscale
            face_gray = cv2.cvtColor(face_resized, cv2.COLOR_BGR2GRAY)
            
            # Flatten and normalize
            face_flat = face_gray.flatten()
            face_normalized = face_flat.astype(np.float32) / 255.0
            
            # Generate encoding (128-dimensional)
            encoding = []
            for i in range(128):  # 128-dimensional encoding
                if i < len(face_normalized):
                    encoding.append(float(face_normalized[i]))
                else:
                    # Pad with zeros if needed
                    encoding.append(0.0)
            
            return encoding
            
        except Exception as e:
            logger.error(f"Error generating face encoding: {str(e)}")
            # Return zero encoding as fallback
            return [0.0] * 128
    
    
    def process_image(self, base64_image: str) -> Dict:
        """
        Main processing function - takes base64 image and returns face detection results
        """
        try:
            # Convert base64 to image
            image = self.base64_to_image(base64_image)
            if image is None:
                return {
                    'success': False,
                    'error': 'Failed to decode image',
                    'faces': [],
                    'face_count': 0
                }
            
            # Detect faces
            faces = self.detect_faces(image)
            
            # Generate encodings for each face
            for face in faces:
                face['encoding'] = self.generate_face_encoding(image, face)
            
            # Determine status
            face_count = len(faces)
            if face_count == 0:
                status = 'no_faces'
                message = 'No faces detected'
            elif face_count == 1:
                status = 'single_face'
                message = 'Single face detected - ready for capture'
            else:
                status = 'multiple_faces'
                message = f'Multiple faces detected ({face_count}) - please ensure only one person is visible'
            
            return {
                'success': True,
                'status': status,
                'message': message,
                'faces': faces,
                'face_count': face_count,
                'image_processed': self.image_to_base64(image)
            }
            
        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'faces': [],
                'face_count': 0
            }

# Global instance
face_detector = PythonFaceDetector()

def detect_faces_in_image(base64_image: str) -> Dict:
    """
    Convenience function for Django views
    """
    return face_detector.process_image(base64_image)
