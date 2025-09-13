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
        self.history_size = 3   # Reduced for faster processing
        self.initialize_face_recognition()
        
        # Stricter recognition parameters
        self.min_face_size = 50  # Increased minimum face size
        self.max_face_size = 400  # Reduced maximum for better quality
        self.quality_threshold = 0.7  # Increased quality requirement
        self.similarity_threshold = 0.85  # Much stricter similarity (was 0.8)
        self.confidence_threshold = 0.9  # High confidence required
        self.min_face_area = 2500  # Minimum face area in pixels
    
    def initialize_face_recognition(self):
        """Initialize face_recognition library"""
        try:
            # Test face_recognition library by loading a simple image
            test_image = np.zeros((100, 100, 3), dtype=np.uint8)
            
            # Try to detect faces in test image (should return empty list)
            face_locations = face_recognition.face_locations(test_image)
            
            self.initialized = True
            logger.info("✅ Python Face Detector initialized successfully with face_recognition library")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize face_recognition library: {str(e)}")
            self.initialized = False
    
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
            logger.error(f"❌ Error converting base64 to image: {str(e)}")
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
            logger.error(f"❌ Error converting image to base64: {str(e)}")
            return ""
    
    def detect_faces(self, image) -> List[Dict]:
        """
        Detect faces in image using face_recognition library
        Returns list of face dictionaries with coordinates, size, and quality
        """
        if not self.initialized or image is None:
            logger.warning("Face detector not initialized or no image provided")
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
            logger.error(f"❌ Error detecting faces: {str(e)}")
            return []
    
    def detect_faces_strict(self, image) -> List[Dict]:
        """
        STRICT face detection with enhanced validation for accuracy and speed
        """
        if not self.initialized or image is None:
            logger.warning("Face detector not initialized or no image provided")
            return []
        
        try:
            # face_recognition expects RGB images
            if len(image.shape) == 3 and image.shape[2] == 3:
                rgb_image = image
            else:
                # Convert to RGB if needed
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # STRICT face detection with optimized parameters for speed
            face_locations = face_recognition.face_locations(
                rgb_image, 
                model="hog",
                number_of_times_to_upsample=1  # Faster processing
            )
            
            face_data = []
            
            for i, (top, right, bottom, left) in enumerate(face_locations):
                # Convert face_recognition format (top, right, bottom, left) to (x, y, w, h)
                x = left
                y = top
                w = right - left
                h = bottom - top
                face_area = w * h
                
                # STRICT size validation
                if (w < self.min_face_size or w > self.max_face_size or
                    h < self.min_face_size or h > self.max_face_size or
                    face_area < self.min_face_area):
                    logger.info(f"❌ Face {i} rejected: size {w}x{h}, area {face_area}")
                    continue
                
                # Extract face region for quality assessment
                face_roi = rgb_image[top:bottom, left:right]
                
                # Calculate STRICT face quality
                quality = self.calculate_face_quality_strict(x, y, w, h, 2, image.shape)
                
                # Only accept high-quality faces
                if quality < self.quality_threshold:
                    logger.info(f"❌ Face {i} rejected: quality {quality:.2f} < {self.quality_threshold}")
                    continue
                
                # Additional validation for face proportions
                aspect_ratio = w / h if h > 0 else 0
                if not (0.7 <= aspect_ratio <= 1.3):  # Reasonable face proportions
                    logger.info(f"❌ Face {i} rejected: bad aspect ratio {aspect_ratio:.2f}")
                    continue
                
                face_info = {
                    'id': i,
                    'x': int(x),
                    'y': int(y),
                    'width': int(w),
                    'height': int(h),
                    'confidence': quality,
                    'eyes_detected': 2,  # face_recognition assumes good face quality
                    'quality_score': quality,
                    'area': face_area,
                    'aspect_ratio': aspect_ratio
                }
                
                face_data.append(face_info)
                logger.info(f"✅ Face {i} accepted: quality {quality:.2f}, size {w}x{h}")
            
            # Apply temporal smoothing for better stability (reduced for speed)
            if len(face_data) > 0:
                face_data = self.smooth_detections(face_data)
            
            return face_data
            
        except Exception as e:
            logger.error(f"❌ Error in strict face detection: {str(e)}")
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
            logger.error(f"❌ Error calculating face quality: {str(e)}")
            return 0.5
    
    def calculate_face_quality_strict(self, x: int, y: int, w: int, h: int, eyes_count: int, image_shape: Tuple) -> float:
        """
        Calculate STRICT face quality score with enhanced validation
        Returns score between 0.0 and 1.0
        """
        try:
            img_height, img_width = image_shape[:2]
            
            # Size quality (stricter requirements)
            size_quality = 1.0
            if w < self.min_face_size or h < self.min_face_size:
                size_quality = 0.3  # Much lower score for small faces
            elif w > self.max_face_size or h > self.max_face_size:
                size_quality = 0.4  # Lower score for oversized faces
            else:
                # Optimal size range gets full points
                size_quality = 1.0
            
            # Position quality (stricter centering requirements)
            center_x = img_width // 2
            center_y = img_height // 2
            face_center_x = x + w // 2
            face_center_y = y + h // 2
            
            # Distance from center (stricter tolerance)
            distance_from_center = math.sqrt(
                (face_center_x - center_x) ** 2 + (face_center_y - center_y) ** 2
            )
            max_distance = min(img_width, img_height) // 3  # Stricter centering requirement
            
            if distance_from_center > max_distance:
                position_quality = 0.2  # Much lower score for off-center faces
            else:
                position_quality = 1.0 - (distance_from_center / max_distance) * 0.3
            
            # Eyes quality (stricter requirements)
            eyes_quality = 1.0 if eyes_count >= 2 else 0.1
            
            # Face area quality (stricter minimum area)
            face_area = w * h
            area_quality = 1.0 if face_area >= self.min_face_area else 0.2
            
            # Aspect ratio quality (stricter face proportions)
            aspect_ratio = w / h if h > 0 else 0
            if 0.8 <= aspect_ratio <= 1.2:  # Stricter aspect ratio
                ratio_quality = 1.0
            elif 0.7 <= aspect_ratio <= 1.3:
                ratio_quality = 0.7
            else:
                ratio_quality = 0.3
            
            # Calculate weighted average with stricter weights
            quality_score = (
                size_quality * 0.25 +      # Size importance
                position_quality * 0.25 +   # Position importance
                eyes_quality * 0.20 +       # Eyes importance
                area_quality * 0.15 +       # Area importance
                ratio_quality * 0.15        # Aspect ratio importance
            )
            
            # Apply minimum threshold
            if quality_score < self.quality_threshold:
                quality_score = 0.0
            
            return min(1.0, max(0.0, quality_score))
            
        except Exception as e:
            logger.error(f"❌ Error calculating strict face quality: {str(e)}")
            return 0.0
    
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
            logger.error(f"❌ Error smoothing detections: {str(e)}")
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
            logger.error(f"❌ Error checking face centering: {str(e)}")
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
    
    def generate_face_encoding(self, image, face_data: Dict) -> List[float]:
        """
        Generate face encoding from face detection coordinates
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
                logger.info(f"✅ Generated face encoding (length: {len(encoding)})")
                return encoding
            else:
                logger.warning("❌ No face encoding generated")
                return [0.0] * 128
                
        except Exception as e:
            logger.error(f"❌ Error generating face encoding: {str(e)}")
            return [0.0] * 128
    
    def process_image(self, base64_image: str) -> Dict:
        """
        STRICTER and FASTER image processing with enhanced validation
        """
        try:
            logger.info("🔍 Starting STRICT image processing...")
            
            # Convert base64 to image
            image = self.base64_to_image(base64_image)
            if image is None:
                logger.error("❌ Failed to decode base64 image")
                return {
                    'success': False,
                    'error': 'Failed to decode image',
                    'faces': [],
                    'face_count': 0
                }
            
            logger.info(f"📊 Image decoded successfully: {image.shape}")
            
            # STRICT face detection with size filtering
            faces = self.detect_faces_strict(image)
            logger.info(f"🔍 STRICT detection found {len(faces)} valid faces")
            
            # Generate encodings for each face
            for face in faces:
                face['encoding'] = self.generate_face_encoding(image, face)
            
            # Determine status with MUCH stricter validation
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
            
            logger.info(f"✅ Processing complete: status={status}, faces={face_count}")
            
            return {
                'success': True,
                'status': status,
                'message': message,
                'faces': faces,
                'face_count': face_count,
                'image_processed': self.image_to_base64(image)
            }
            
        except Exception as e:
            logger.error(f"❌ Error processing image: {str(e)}")
            import traceback
            traceback.print_exc()
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