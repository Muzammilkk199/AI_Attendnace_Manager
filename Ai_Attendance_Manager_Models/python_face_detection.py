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
from collections import deque

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
        
        # Anti-spoofing detection parameters
        self.movement_history = deque(maxlen=10)
        self.last_face_center = None
        self.frame_count = 0
        self.spoofing_alert_active = False
        
        # Spoofing detection thresholds (very lenient for real faces)
        self.MOVEMENT_THRESHOLD = 1.0  # Very low movement threshold
        self.SPOOFING_FRAMES_THRESHOLD = 30
        self.SIMILARITY_THRESHOLD = 0.9  # Very high similarity threshold (more lenient)
    
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
    
    def analyze_skin_pixels(self, face_roi):
        """
        Analyze skin pixels to detect if it's a real face or a photo/screen.
        """
        # Convert to HSV for better skin detection
        hsv = cv2.cvtColor(face_roi, cv2.COLOR_BGR2HSV)
        
        # Define expanded skin color range in HSV for different skin tones
        # Lower range (lighter skin tones)
        lower_skin1 = np.array([0, 20, 70], dtype=np.uint8)
        upper_skin1 = np.array([20, 255, 255], dtype=np.uint8)
        
        # Upper range (darker skin tones)
        lower_skin2 = np.array([0, 20, 20], dtype=np.uint8)
        upper_skin2 = np.array([20, 255, 200], dtype=np.uint8)
        
        # Additional range for very dark skin tones
        lower_skin3 = np.array([0, 10, 10], dtype=np.uint8)
        upper_skin3 = np.array([30, 255, 150], dtype=np.uint8)
        
        # Create combined skin mask
        skin_mask1 = cv2.inRange(hsv, lower_skin1, upper_skin1)
        skin_mask2 = cv2.inRange(hsv, lower_skin2, upper_skin2)
        skin_mask3 = cv2.inRange(hsv, lower_skin3, upper_skin3)
        
        # Combine all skin masks
        skin_mask = cv2.bitwise_or(skin_mask1, cv2.bitwise_or(skin_mask2, skin_mask3))
        
        # Calculate skin pixel percentage
        total_pixels = face_roi.shape[0] * face_roi.shape[1]
        skin_pixels = np.sum(skin_mask > 0)
        skin_percentage = (skin_pixels / total_pixels) * 100
        
        # Analyze skin texture using Laplacian variance
        gray_face = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
        laplacian_var = cv2.Laplacian(gray_face, cv2.CV_64F).var()
        
        return skin_percentage, laplacian_var
    
    def detect_mobile_screen(self, face_roi):
        """
        Detect if the face region contains a mobile screen (LCD/OLED patterns).
        """
        # Convert to grayscale
        gray = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
        
        # Detect high-frequency patterns typical of screens
        # Apply Sobel edge detection
        sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        sobel_magnitude = np.sqrt(sobel_x**2 + sobel_y**2)
        
        # Calculate edge density
        edge_threshold = 50
        edge_pixels = np.sum(sobel_magnitude > edge_threshold)
        total_pixels = gray.shape[0] * gray.shape[1]
        edge_density = (edge_pixels / total_pixels) * 100
        
        # Detect pixel patterns typical of screens
        # Check for regular grid patterns
        fft = np.fft.fft2(gray)
        fft_shift = np.fft.fftshift(fft)
        magnitude_spectrum = np.log(np.abs(fft_shift) + 1)
        
        # Look for high-frequency components (screen pixels)
        high_freq_energy = np.sum(magnitude_spectrum[gray.shape[0]//3:2*gray.shape[0]//3, 
                                                gray.shape[1]//3:2*gray.shape[1]//3])
        
        return edge_density, high_freq_energy
    
    def detect_reflection_patterns(self, face_roi):
        """
        Detect reflection patterns that indicate a screen or photo.
        """
        # Convert to grayscale
        gray = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
        
        # Detect bright spots (potential reflections)
        bright_threshold = 200
        bright_pixels = np.sum(gray > bright_threshold)
        total_pixels = gray.shape[0] * gray.shape[1]
        bright_percentage = (bright_pixels / total_pixels) * 100
        
        # Check for uniform brightness (typical of screens)
        brightness_std = np.std(gray)
        
        return bright_percentage, brightness_std
    
    def calculate_face_movement(self, current_center, previous_center):
        """
        Calculate the amount of face movement between frames.
        """
        if previous_center is None:
            return 0
        
        return np.sqrt((current_center[0] - previous_center[0])**2 + (current_center[1] - previous_center[1])**2)
    
    def detect_face_variation(self, current_encoding, previous_encoding):
        """
        Detect if the face has changed significantly (indicating movement/liveness).
        """
        if previous_encoding is None:
            return True  # First detection, assume movement
        
        # Calculate cosine similarity
        from scipy.spatial.distance import cosine
        similarity = 1 - cosine(current_encoding, previous_encoding)
        
        # If similarity is too high, it might be a static image
        return similarity < self.SIMILARITY_THRESHOLD
    
    def is_spoofing_attack(self, face_center, face_encoding, face_roi, frame_count):
        """
        Advanced spoofing detection using multiple techniques.
        """
        if face_center is None:
            return True, "No face detected"
        
        # Calculate face movement
        movement = self.calculate_face_movement(face_center, self.last_face_center)
        self.movement_history.append(movement)
        
        # Check for face variation (liveness)
        face_variation = self.detect_face_variation(face_encoding, getattr(self, 'last_encoding', None))
        
        # Advanced spoofing detection
        spoofing_score = 0
        spoofing_reasons = []
        
        # 1. Analyze skin pixels
        skin_percentage, laplacian_var = self.analyze_skin_pixels(face_roi)
        
        # Debug: Print skin percentage for troubleshooting
        if frame_count % 30 == 0:  # Print every 30 frames
            logger.info(f"Skin percentage: {skin_percentage:.1f}%, Texture variance: {laplacian_var:.1f}")
        
        if skin_percentage < 0.5:  # Only flag if almost no skin at all
            spoofing_score += 1
            spoofing_reasons.append("Extremely low skin pixel count")
        
        if laplacian_var < 2:  # Only flag if extremely low texture variance
            spoofing_score += 1
            spoofing_reasons.append("Extremely low texture variance")
        
        # 2. Detect mobile screen patterns (very strict for mobile detection)
        edge_density, high_freq_energy = self.detect_mobile_screen(face_roi)
        if edge_density > 25:  # Higher threshold for edge density (only flag obvious screens)
            spoofing_score += 4  # Higher penalty for screen detection
            spoofing_reasons.append("High edge density (screen detected)")
        
        if high_freq_energy > 1500:  # Higher threshold for frequency energy (only flag obvious screens)
            spoofing_score += 4  # Higher penalty for screen patterns
            spoofing_reasons.append("Screen pixel patterns detected")
        
        # 3. Detect reflection patterns (very lenient for real faces)
        bright_percentage, brightness_std = self.detect_reflection_patterns(face_roi)
        if bright_percentage > 50:  # Higher threshold for bright pixels (only flag obvious screens)
            spoofing_score += 2  # Moderate penalty
            spoofing_reasons.append("Excessive reflections")
        
        if brightness_std < 10:  # Lower threshold for brightness uniformity (only flag very uniform screens)
            spoofing_score += 2  # Moderate penalty
            spoofing_reasons.append("Uniform brightness (screen)")
        
        # 4. Movement and variation checks (very lenient)
        if len(self.movement_history) >= 10:
            avg_movement = np.mean(list(self.movement_history))
            if avg_movement < self.MOVEMENT_THRESHOLD:
                spoofing_score += 1  # Very low penalty for no movement
                spoofing_reasons.append("No movement detected")
            
            if not face_variation:
                spoofing_score += 1  # Very low penalty for no variation
                spoofing_reasons.append("No face variation")
        
        # Update tracking variables
        self.last_face_center = face_center
        self.last_encoding = face_encoding
        
        # Determine if it's a spoofing attack (very high threshold to avoid false positives)
        if spoofing_score >= 8:  # Very high threshold for spoofing detection
            self.spoofing_alert_active = True
            reason_text = ", ".join(spoofing_reasons[:3])  # Show top 3 reasons
            return True, f"SPOOFING DETECTED: {reason_text}"
        else:
            self.spoofing_alert_active = False
            return False, "Live person detected"
    
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
        STRICTER and FASTER image processing with enhanced validation and anti-spoofing
        """
        try:
            logger.info("🔍 Starting STRICT image processing with anti-spoofing...")
            
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
            
            # Generate encodings for each face and perform spoofing detection
            for face in faces:
                face['encoding'] = self.generate_face_encoding(image, face)
                
                # Perform anti-spoofing detection for each face
                if face['encoding'] and len(face['encoding']) == 128:
                    # Calculate face center
                    face_center = (face['x'] + face['width']//2, face['y'] + face['height']//2)
                    
                    # Extract face region for spoofing analysis
                    x, y, w, h = face['x'], face['y'], face['width'], face['height']
                    face_roi = image[y:y+h, x:x+w]
                    
                    # Perform spoofing detection
                    is_spoofing, spoofing_message = self.is_spoofing_attack(
                        face_center, face['encoding'], face_roi, self.frame_count
                    )
                    
                    # Add spoofing information to face data
                    face['is_spoofing'] = is_spoofing
                    face['spoofing_message'] = spoofing_message
                    face['spoofing_score'] = getattr(self, 'spoofing_score', 0)
                    
                    logger.info(f"🛡️ Anti-spoofing result for face: {spoofing_message}")
            
            # Increment frame count for spoofing detection
            self.frame_count += 1
            
            # Determine status with MUCH stricter validation and spoofing checks
            face_count = len(faces)
            if face_count == 0:
                status = 'no_faces'
                message = 'No face detected - please position your face in the center box'
            elif face_count == 1:
                # Additional validation for single face
                face = faces[0]
                
                # Check for spoofing first
                if face.get('is_spoofing', False):
                    status = 'spoofing_detected'
                    message = face.get('spoofing_message', 'SPOOFING DETECTED: Mobile phone or photo detected')
                    logger.warning(f"🚨 SPOOFING DETECTED: {message}")
                elif face.get('quality_score', 0) < 0.4:
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
                'image_processed': self.image_to_base64(image),
                'spoofing_detection_enabled': True
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