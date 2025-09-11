"""
Python Face Detection Module using Face Recognition
Replaces JavaScript face detection with server-side Python processing using face_recognition library
"""

import base64
import json
import logging
import random
import math
from typing import List, Dict, Tuple, Optional
import os
import io

# Import face recognition and image processing libraries
import face_recognition
import cv2
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)

class PythonFaceDetector:
    """
    Advanced face detection using face_recognition library
    Provides accurate face detection, multiple face handling, and face encoding
    """
    
    def __init__(self):
        self.initialized = False
        self.face_history = []  # For detection stability
        self.history_size = 5   # Number of frames to consider for stability
        self.initialize_face_recognition()
    
    def initialize_face_recognition(self):
        """Initialize face_recognition library"""
        try:
            # Test face_recognition library by loading a simple image
            test_image = np.zeros((100, 100, 3), dtype=np.uint8)
            
            # Try to detect faces in test image (should return empty list)
            face_locations = face_recognition.face_locations(test_image)
            
            self.initialized = True
            logger.info("Python Face Detector initialized successfully with face_recognition library")
            
        except Exception as e:
            logger.error(f"Failed to initialize face_recognition library: {str(e)}")
            raise e
    
    def base64_to_image(self, base64_string: str):
        """Convert base64 string to RGB image for face_recognition"""
        try:
            # Remove data URL prefix if present
            if ',' in base64_string:
                base64_string = base64_string.split(',')[1]
            
            # Decode base64
            image_data = base64.b64decode(base64_string)
            
            # Convert to PIL Image
            pil_image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB (face_recognition expects RGB)
            rgb_image = np.array(pil_image.convert('RGB'))
            
            return rgb_image
            
        except Exception as e:
            logger.error(f"Error converting base64 to image: {str(e)}")
            return None
    
    def image_to_base64(self, image) -> str:
        """Convert RGB image to base64 string"""
        try:
            if image is not None and hasattr(image, 'shape'):
                # Convert numpy array to PIL Image
                pil_image = Image.fromarray(image)
                
                # Convert to base64
                buffer = io.BytesIO()
                pil_image.save(buffer, format='JPEG', quality=80)
                image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                
                return f"data:image/jpeg;base64,{image_base64}"
            else:
                return ""
            
        except Exception as e:
            logger.error(f"Error converting image to base64: {str(e)}")
            return ""
    
    def detect_faces(self, image) -> List[Dict]:
        """
        Detect faces in image using face_recognition library
        Returns list of face dictionaries with coordinates, size, and quality
        """
        if not self.initialized or image is None:
            return []
        
        try:
            # face_recognition expects RGB images
            if len(image.shape) == 3 and image.shape[2] == 3:
                rgb_image = image
            else:
                # Convert to RGB if needed
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Detect face locations using face_recognition
            face_locations = face_recognition.face_locations(rgb_image, model="hog")
            
            face_data = []
            
            for i, (top, right, bottom, left) in enumerate(face_locations):
                # Convert face_recognition format (top, right, bottom, left) to (x, y, w, h)
                x = left
                y = top
                w = right - left
                h = bottom - top
                
                # Extract face region for quality assessment
                face_roi = rgb_image[top:bottom, left:right]
                
                # Calculate face quality based on size, position, and other factors
                quality = self.calculate_face_quality(x, y, w, h, 2, image.shape)  # Assume 2 eyes for face_recognition
                
                face_info = {
                    'id': i,
                    'x': int(x),
                    'y': int(y),
                    'width': int(w),
                    'height': int(h),
                    'confidence': quality,
                    'eyes_detected': 2,  # face_recognition assumes good face quality
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
    
    def is_face_centered(self, face: Dict, image_shape: Tuple) -> bool:
        """
        Check if the face is properly centered in the image
        Returns True if face is centered within acceptable bounds
        """
        try:
            img_height, img_width = image_shape[:2]
            x, y, w, h = face['x'], face['y'], face['width'], face['height']
            
            # Calculate face center
            face_center_x = x + w / 2
            face_center_y = y + h / 2
            
            # Calculate image center
            image_center_x = img_width / 2
            image_center_y = img_height / 2
            
            # Define acceptable deviation from center (30% of image dimensions)
            max_deviation_x = img_width * 0.3
            max_deviation_y = img_height * 0.3
            
            # Check if face is within acceptable bounds
            x_deviation = abs(face_center_x - image_center_x)
            y_deviation = abs(face_center_y - image_center_y)
            
            return x_deviation <= max_deviation_x and y_deviation <= max_deviation_y
            
        except Exception as e:
            logger.error(f"Error checking face centering: {str(e)}")
            return False
    
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
            'face_recognition_loaded': self.initialized,
            'library': 'face_recognition'
        }
    
    def generate_face_encoding_from_cropped_face(self, image, face_data: Dict) -> List[float]:
        """
        Generate face encoding from cropped and preprocessed face region
        This ensures only the processed face is used for encoding generation
        """
        try:
            logger.info(f"Generating encoding from cropped face region")
            
            # First, try to generate encoding from original detection (as backup)
            # This ensures we always have a valid encoding
            original_encoding = self.generate_encoding_from_original_detection(image, face_data)
            
            # Then try to extract and preprocess face region for enhanced encoding
            cropped_face = self.crop_and_preprocess_face(image, face_data)
            if cropped_face is not None:
                # Generate face encoding from the cropped and preprocessed face
                face_encodings = face_recognition.face_encodings(cropped_face)
                
                if face_encodings:
                    encoding = face_encodings[0].tolist()
                    logger.info(f"Successfully generated encoding from cropped face (length: {len(encoding)})")
                    return encoding
                else:
                    logger.warning("No face encoding generated from cropped face, using original detection encoding")
                    return original_encoding
            else:
                logger.warning("Failed to crop face, using original detection encoding")
                return original_encoding
                
        except Exception as e:
            logger.error(f"Error generating face encoding from cropped face: {str(e)}")
            # Fallback to original detection method
            return self.generate_encoding_from_original_detection(image, face_data)
    
    def generate_encoding_from_original_detection(self, image, face_data: Dict) -> List[float]:
        """
        Generate encoding from original face detection coordinates (fallback method)
        """
        try:
            x, y, w, h = face_data['x'], face_data['y'], face_data['width'], face_data['height']
            
            # Convert face_recognition format (x, y, w, h) to (top, right, bottom, left)
            top = y
            right = x + w
            bottom = y + h
            left = x
            
            # Ensure image is RGB for face_recognition
            if len(image.shape) == 3 and image.shape[2] == 3:
                rgb_image = image
            else:
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Extract face encodings using face_recognition
            face_encodings = face_recognition.face_encodings(
                rgb_image, 
                known_face_locations=[(top, right, bottom, left)]
            )
            
            if face_encodings:
                encoding = face_encodings[0].tolist()
                logger.info(f"Generated encoding from original detection (length: {len(encoding)})")
                return encoding
            else:
                logger.warning("No face encoding generated from original detection")
                return [0.0] * 128
                
        except Exception as e:
            logger.error(f"Error generating encoding from original detection: {str(e)}")
            return [0.0] * 128
    
    def crop_and_preprocess_face(self, image, face_data: Dict):
        """
        Crop face region with padding and apply preprocessing for optimal encoding
        """
        try:
            x, y, w, h = face_data['x'], face_data['y'], face_data['width'], face_data['height']
            img_height, img_width = image.shape[:2]
            
            # Validate face coordinates
            if x < 0 or y < 0 or w <= 0 or h <= 0:
                logger.error(f"Invalid face coordinates: x={x}, y={y}, w={w}, h={h}")
                return None
            
            # Add 30% padding around face (same as frontend)
            padding = 0.3
            padded_x = max(0, int(x - w * padding))
            padded_y = max(0, int(y - h * padding))
            padded_w = min(img_width - padded_x, int(w * (1 + 2 * padding)))
            padded_h = min(img_height - padded_y, int(h * (1 + 2 * padding)))
            
            # Ensure minimum face size for encoding
            if padded_w < 50 or padded_h < 50:
                logger.warning(f"Face too small for reliable encoding: {padded_w}x{padded_h}")
                return None
            
            logger.info(f"Cropping face: original({x},{y},{w},{h}) -> padded({padded_x},{padded_y},{padded_w},{padded_h})")
            logger.info(f"Image shape: {image.shape}, Crop bounds: [{padded_y}:{padded_y+padded_h}, {padded_x}:{padded_x+padded_w}]")
            
            # Crop the face region
            cropped_face = image[padded_y:padded_y+padded_h, padded_x:padded_x+padded_w]
            
            # Validate cropped face
            if cropped_face.size == 0:
                logger.error("Cropped face is empty")
                return None
            
            logger.info(f"Cropped face shape: {cropped_face.shape}")
            
            # Apply minimal preprocessing to avoid destroying face structure
            processed_face = self.preprocess_face_for_encoding(cropped_face)
            
            return processed_face
            
        except Exception as e:
            logger.error(f"Error cropping and preprocessing face: {str(e)}")
            return None
    
    def preprocess_face_for_encoding(self, face_image):
        """
        Apply minimal preprocessing to cropped face for optimal encoding generation
        Keep preprocessing light to maintain face structure for face_recognition
        """
        try:
            # Ensure image is RGB for face_recognition
            if len(face_image.shape) == 3:
                # Convert BGR to RGB for face_recognition
                face_rgb = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)
            else:
                # Convert grayscale to RGB
                face_rgb = cv2.cvtColor(face_image, cv2.COLOR_GRAY2RGB)
            
            # Apply very light histogram equalization only if image is too dark/bright
            gray_version = cv2.cvtColor(face_rgb, cv2.COLOR_RGB2GRAY)
            mean_brightness = np.mean(gray_version)
            
            if mean_brightness < 80 or mean_brightness > 180:
                logger.info(f"Adjusting brightness from {mean_brightness}")
                # Convert to YUV, equalize Y channel, convert back
                face_yuv = cv2.cvtColor(face_rgb, cv2.COLOR_RGB2YUV)
                face_yuv[:,:,0] = cv2.equalizeHist(face_yuv[:,:,0])
                face_rgb = cv2.cvtColor(face_yuv, cv2.COLOR_YUV2RGB)
            
            logger.info(f"Preprocessed face shape: {face_rgb.shape}, brightness: {mean_brightness}")
            return face_rgb
            
        except Exception as e:
            logger.error(f"Error preprocessing face: {str(e)}")
            # Return original image converted to RGB if preprocessing fails
            try:
                if len(face_image.shape) == 3:
                    return cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)
                else:
                    return cv2.cvtColor(face_image, cv2.COLOR_GRAY2RGB)
            except:
                return face_image
    
    def generate_face_encoding(self, image, face_data: Dict) -> List[float]:
        """
        Generate face encoding - now uses cropped and preprocessed face
        """
        return self.generate_face_encoding_from_cropped_face(image, face_data)
    
    
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
            
            # Generate encodings for each face using cropped and preprocessed face regions
            for face in faces:
                face['encoding'] = self.generate_face_encoding_from_cropped_face(image, face)
            
            # Determine status with strict validation
            face_count = len(faces)
            if face_count == 0:
                status = 'no_faces'
                message = 'No face detected - please position your face in the center box'
            elif face_count == 1:
                # Additional validation for single face
                face = faces[0]
                if face.get('quality_score', 0) < 0.4:
                    status = 'poor_quality'
                    message = 'Face quality too low - please improve lighting and center your face'
                else:
                    # Check if face is centered properly
                    if self.is_face_centered(face, image.shape):
                        status = 'single_face'
                        message = 'Face detected and centered - ready for capture'
                    else:
                        status = 'not_centered'
                        message = 'Please center your face in the detection box'
            else:
                # Multiple faces - BLOCK EVERYTHING
                status = 'multiple_faces_blocked'
                message = f'BLOCKED: Multiple faces detected ({face_count}) - System locked until only one person is visible'
            
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
