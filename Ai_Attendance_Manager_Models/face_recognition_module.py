"""
Face Recognition Module for AI Attendance Manager
Handles face detection, embedding generation, and face matching
"""

import cv2
import numpy as np
import base64
import io
from PIL import Image
import face_recognition
from typing import List, Tuple, Optional, Dict
import os
import json
from datetime import datetime


class FaceRecognitionManager:
    """Main class for handling face recognition operations"""
    
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.known_encodings = []
        self.known_names = []
        self.known_student_ids = []
        
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for better face recognition"""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply histogram equalization for better contrast
        equalized = cv2.equalizeHist(gray)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(equalized, (3, 3), 0)
        
        return blurred
    
    def detect_faces(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Detect faces in the image using OpenCV"""
        gray = self.preprocess_image(image)
        
        # Detect faces
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        
        return faces
    
    def extract_face_encoding(self, image: np.ndarray, face_location: Tuple[int, int, int, int] = None) -> Optional[np.ndarray]:
        """Extract face encoding using face_recognition library"""
        try:
            # Convert BGR to RGB
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            if face_location:
                # Use provided face location
                top, right, bottom, left = face_location
                face_image = rgb_image[top:bottom, left:right]
            else:
                # Find face locations
                face_locations = face_recognition.face_locations(rgb_image)
                if not face_locations:
                    return None
                face_image = rgb_image[face_locations[0][0]:face_locations[0][2], 
                                     face_locations[0][3]:face_locations[0][1]]
            
            # Get face encodings
            encodings = face_recognition.face_encodings(face_image)
            
            if encodings:
                return encodings[0]
            return None
            
        except Exception as e:
            print(f"Error extracting face encoding: {e}")
            return None
    
    def base64_to_image(self, base64_string: str) -> np.ndarray:
        """Convert base64 string to OpenCV image"""
        try:
            # Remove data URL prefix if present
            if ',' in base64_string:
                base64_string = base64_string.split(',')[1]
            
            # Decode base64
            image_data = base64.b64decode(base64_string)
            
            # Convert to PIL Image
            pil_image = Image.open(io.BytesIO(image_data))
            
            # Convert to OpenCV format
            opencv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
            
            return opencv_image
        except Exception as e:
            print(f"Error converting base64 to image: {e}")
            return None
    
    def image_to_base64(self, image: np.ndarray, format: str = 'JPEG') -> str:
        """Convert OpenCV image to base64 string"""
        try:
            # Convert BGR to RGB
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Convert to PIL Image
            pil_image = Image.fromarray(rgb_image)
            
            # Convert to base64
            buffer = io.BytesIO()
            pil_image.save(buffer, format=format)
            img_str = base64.b64encode(buffer.getvalue()).decode()
            
            return f"data:image/{format.lower()};base64,{img_str}"
        except Exception as e:
            print(f"Error converting image to base64: {e}")
            return None
    
    def capture_face_for_training(self, image: np.ndarray, student_id: str, student_name: str) -> Dict:
        """Capture and process face for training dataset"""
        try:
            # Detect faces
            faces = self.detect_faces(image)
            
            if len(faces) == 0:
                return {
                    'success': False,
                    'message': 'No face detected in the image'
                }
            
            if len(faces) > 1:
                return {
                    'success': False,
                    'message': 'Multiple faces detected. Please ensure only one person is in the frame.'
                }
            
            # Get the first (and should be only) face
            x, y, w, h = faces[0]
            
            # Extract face region
            face_image = image[y:y+h, x:x+w]
            
            # Convert to grayscale as per SRS requirement
            gray_face = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)
            
            # Resize to standard size for consistency
            resized_face = cv2.resize(gray_face, (150, 150))
            
            # Extract face encoding
            face_encoding = self.extract_face_encoding(image, (y, x+w, y+h, x))
            
            if face_encoding is None:
                return {
                    'success': False,
                    'message': 'Could not extract face features. Please try again.'
                }
            
            # Convert processed face to base64 for storage
            face_base64 = self.image_to_base64(resized_face)
            
            return {
                'success': True,
                'message': 'Face captured successfully',
                'face_encoding': face_encoding.tolist(),
                'face_image': face_base64,
                'face_location': faces[0].tolist(),
                'student_id': student_id,
                'student_name': student_name
            }
            
        except Exception as e:
            print(f"Error capturing face: {e}")
            return {
                'success': False,
                'message': f'Error processing face: {str(e)}'
            }
    
    def recognize_face(self, image: np.ndarray, known_encodings: List, known_names: List, tolerance: float = 0.6) -> Dict:
        """Recognize face from image using known encodings"""
        try:
            # Extract face encoding from image
            face_encoding = self.extract_face_encoding(image)
            
            if face_encoding is None:
                return {
                    'success': False,
                    'message': 'No face detected in the image'
                }
            
            # Compare with known faces
            matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=tolerance)
            face_distances = face_recognition.face_distance(known_encodings, face_encoding)
            
            if True in matches:
                # Find the best match
                best_match_index = np.argmin(face_distances)
                confidence = 1 - face_distances[best_match_index]
                
                return {
                    'success': True,
                    'recognized': True,
                    'student_name': known_names[best_match_index],
                    'confidence': float(confidence),
                    'face_encoding': face_encoding.tolist()
                }
            else:
                return {
                    'success': True,
                    'recognized': False,
                    'message': 'Face not recognized',
                    'face_encoding': face_encoding.tolist()
                }
                
        except Exception as e:
            print(f"Error recognizing face: {e}")
            return {
                'success': False,
                'message': f'Error recognizing face: {str(e)}'
            }
    
    def validate_face_quality(self, image: np.ndarray) -> Dict:
        """Validate face quality for better recognition"""
        try:
            faces = self.detect_faces(image)
            
            if len(faces) == 0:
                return {
                    'valid': False,
                    'message': 'No face detected'
                }
            
            if len(faces) > 1:
                return {
                    'valid': False,
                    'message': 'Multiple faces detected'
                }
            
            x, y, w, h = faces[0]
            
            # Check face size (should be reasonably large)
            if w < 50 or h < 50:
                return {
                    'valid': False,
                    'message': 'Face too small. Please move closer to the camera.'
                }
            
            # Check face position (should be roughly centered)
            image_height, image_width = image.shape[:2]
            center_x = x + w // 2
            center_y = y + h // 2
            
            if (center_x < image_width * 0.2 or center_x > image_width * 0.8 or
                center_y < image_height * 0.2 or center_y > image_height * 0.8):
                return {
                    'valid': False,
                    'message': 'Please center your face in the frame'
                }
            
            return {
                'valid': True,
                'message': 'Face quality is good',
                'face_location': faces[0].tolist()
            }
            
        except Exception as e:
            print(f"Error validating face quality: {e}")
            return {
                'valid': False,
                'message': f'Error validating face: {str(e)}'
            }


# Global instance
face_manager = FaceRecognitionManager()
