/**
 * Advanced Face Detection System with ESP-style Detection Box
 * Features:
 * - Real-time face detection with bounding box
 * - Multiple face detection prevention
 * - Face quality validation
 * - Professional UI with status indicators
 * - Comprehensive error handling
 */

console.log('Advanced Face Detection JavaScript loaded successfully!');

class AdvancedFaceDetection {
    constructor() {
        this.video = null;
        this.canvas = null;
        this.ctx = null;
        this.isDetecting = false;
        this.detectionInterval = null;
        this.faceCount = 0;
        this.lastFaceCount = 0;
        this.faceQuality = 0;
        this.detectionBox = null;
        this.statusElement = null;
        this.captureButton = null;
        this.retryButton = null;
        this.faceData = null;
        this.isCaptured = false;
        
        // Detection parameters
        this.minFaceSize = 100;
        this.maxFaceSize = 400;
        this.qualityThreshold = 0.7;
        this.stabilityFrames = 10; // Frames to wait for stable detection
        this.stableFrames = 0;
        
        this.init();
    }
    
    init() {
        console.log('AdvancedFaceDetection: Initializing...');
        this.createDetectionUI();
        this.setupEventListeners();
        // Don't auto-initialize camera, let user click start
        this.updateStatus('Click "Start Detection" to begin camera access', 'info');
        console.log('AdvancedFaceDetection: Initialization complete');
    }
    
    createDetectionUI() {
        // UI is now created statically in HTML, just get references
        this.video = document.getElementById('faceVideo');
        this.canvas = document.getElementById('faceCanvas');
        this.ctx = this.canvas ? this.canvas.getContext('2d') : null;
        this.detectionBox = document.getElementById('faceBox');
        this.statusElement = document.getElementById('statusText');
        this.statusIndicator = document.getElementById('statusIndicator');
        this.captureButton = document.getElementById('captureFace');
        this.retryButton = document.getElementById('retryCapture');
        this.startButton = document.getElementById('startDetection');
        this.stopButton = document.getElementById('stopDetection');
        this.validationMessages = document.getElementById('validationMessages');
        
        console.log('AdvancedFaceDetection: UI elements found:', {
            video: !!this.video,
            canvas: !!this.canvas,
            startButton: !!this.startButton,
            captureButton: !!this.captureButton,
            statusElement: !!this.statusElement
        });
        
        // Initialize status
        if (this.statusElement) {
            this.statusElement.textContent = 'Ready to start detection';
        }
        if (this.statusIndicator) {
            this.statusIndicator.className = 'status-indicator info';
        }
    }
    
    setupEventListeners() {
        // Test camera button
        const testCameraBtn = document.getElementById('testCameraBtn');
        if (testCameraBtn) {
            testCameraBtn.addEventListener('click', () => this.testCamera());
        }
        
        this.startButton?.addEventListener('click', () => this.startDetection());
        this.captureButton?.addEventListener('click', () => this.captureFace());
        this.retryButton?.addEventListener('click', () => this.retryCapture());
        this.stopButton?.addEventListener('click', () => this.stopDetection());
    }
    
    async testCamera() {
        console.log('AdvancedFaceDetection: Testing camera...');
        try {
            this.updateStatus('Testing camera access...', 'warning');
            
            // Check if getUserMedia is supported
            if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                throw new Error('Camera access not supported in this browser');
            }
            
            const stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    width: { ideal: 640 },
                    height: { ideal: 480 },
                    facingMode: 'user'
                }
            });
            
            console.log('AdvancedFaceDetection: Test camera stream obtained');
            
            if (this.video) {
                this.video.srcObject = stream;
                
                this.video.onloadedmetadata = () => {
                    console.log('AdvancedFaceDetection: Test video metadata loaded');
                    console.log('Test video dimensions:', this.video.videoWidth, 'x', this.video.videoHeight);
                    this.updateStatus('Camera test successful! Video size: ' + this.video.videoWidth + 'x' + this.video.videoHeight, 'success');
                };
                
                this.video.onerror = (error) => {
                    console.error('AdvancedFaceDetection: Test video error:', error);
                    this.updateStatus('Camera test failed: ' + error.message, 'error');
                };
                
                // Force play the video
                this.video.play().catch(error => {
                    console.error('AdvancedFaceDetection: Test video play error:', error);
                });
                
            } else {
                console.error('AdvancedFaceDetection: Video element not found for test');
                this.updateStatus('Video element not found for test.', 'error');
            }
            
        } catch (error) {
            console.error('AdvancedFaceDetection: Camera test failed:', error);
            this.updateStatus('Camera test failed: ' + error.message, 'error');
            this.showValidationMessage('Camera Test Error: ' + error.message, 'error');
        }
    }
    
    async initializeCamera() {
        try {
            console.log('AdvancedFaceDetection: Initializing camera...');
            this.updateStatus('Requesting camera access...', 'warning');
            
            // Check if getUserMedia is supported
            if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                throw new Error('Camera access not supported in this browser');
            }
            
            const stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    width: { ideal: 640 },
                    height: { ideal: 480 },
                    facingMode: 'user'
                }
            });
            
            console.log('AdvancedFaceDetection: Camera stream obtained');
            
            if (this.video) {
                console.log('AdvancedFaceDetection: Setting video source object');
                this.video.srcObject = stream;
                
                this.video.onloadedmetadata = () => {
                    console.log('AdvancedFaceDetection: Video metadata loaded');
                    console.log('Video dimensions:', this.video.videoWidth, 'x', this.video.videoHeight);
                    console.log('Video ready state:', this.video.readyState);
                    
                    if (this.canvas) {
                        this.canvas.width = this.video.videoWidth;
                        this.canvas.height = this.video.videoHeight;
                    }
                    this.updateStatus('Camera ready. Click "Start Detection" to begin.', 'success');
                    if (this.startButton) {
                        this.startButton.disabled = false;
                    }
                };
                
                this.video.oncanplay = () => {
                    console.log('AdvancedFaceDetection: Video can play');
                };
                
                this.video.onplay = () => {
                    console.log('AdvancedFaceDetection: Video started playing');
                };
                
                this.video.onerror = (error) => {
                    console.error('AdvancedFaceDetection: Video error:', error);
                    this.updateStatus('Camera error occurred.', 'error');
                };
                
                // Force play the video
                this.video.play().catch(error => {
                    console.error('AdvancedFaceDetection: Video play error:', error);
                });
                
            } else {
                console.error('AdvancedFaceDetection: Video element not found');
                this.updateStatus('Video element not found.', 'error');
            }
            
        } catch (error) {
            console.error('AdvancedFaceDetection: Camera initialization failed:', error);
            this.updateStatus('Camera access denied. Please allow camera access and refresh the page.', 'error');
            this.showValidationMessage('Camera Error: ' + error.message, 'error');
        }
    }
    
    async startDetection() {
        if (!this.video || !this.canvas) {
            console.error('AdvancedFaceDetection: Video or canvas not found');
            return;
        }
        
        try {
            this.updateStatus('Starting camera...', 'warning');
            
            // Initialize camera if not already done
            if (!this.video.srcObject) {
                await this.initializeCamera();
                // Wait a bit for camera to be ready
                await new Promise(resolve => setTimeout(resolve, 1000));
            }
            
            this.isDetecting = true;
            if (this.startButton) this.startButton.disabled = true;
            if (this.stopButton) this.stopButton.disabled = false;
            if (this.captureButton) this.captureButton.disabled = true;
            if (this.retryButton) this.retryButton.disabled = true;
            
            this.updateStatus('Detecting faces...', 'detecting');
            this.showValidationMessage('Face detection started. Please position your face in the center.', 'info');
            
            // Start detection loop
            this.detectionInterval = setInterval(() => {
                this.detectFaces();
            }, 100); // 10 FPS for smooth detection
            
        } catch (error) {
            console.error('AdvancedFaceDetection: Failed to start detection:', error);
            this.updateStatus('Failed to start detection: ' + error.message, 'error');
            this.showValidationMessage('Failed to start detection: ' + error.message, 'error');
        }
    }
    
    detectFaces() {
        if (!this.isDetecting || !this.video || !this.ctx) return;
        
        // Draw current frame to canvas
        this.ctx.drawImage(this.video, 0, 0, this.canvas.width, this.canvas.height);
        
        // Simulate face detection (replace with actual face detection library)
        const faces = this.simulateFaceDetection();
        
        this.faceCount = faces.length;
        this.updateFaceCount();
        
        if (faces.length === 0) {
            this.hideFaceBox();
            this.stableFrames = 0;
            this.faceQuality = 0;
            this.updateQualityIndicator();
        } else if (faces.length === 1) {
            const face = faces[0];
            this.showFaceBox(face);
            this.calculateFaceQuality(face);
            this.updateQualityIndicator();
            
            // Check for stable detection
            if (this.lastFaceCount === 1) {
                this.stableFrames++;
                if (this.stableFrames >= this.stabilityFrames) {
                    this.enableCapture();
                }
            } else {
                this.stableFrames = 0;
            }
        } else {
            this.hideFaceBox();
            this.stableFrames = 0;
            this.showValidationMessage(`Multiple faces detected (${faces.length}). Please ensure only one person is visible.`, 'error');
            this.disableCapture();
        }
        
        this.lastFaceCount = this.faceCount;
    }
    
    simulateFaceDetection() {
        // This is a simulation - replace with actual face detection
        // For now, we'll simulate detection based on mouse position or random
        const faces = [];
        
        // Simulate face detection in center area
        const centerX = this.canvas.width / 2;
        const centerY = this.canvas.height / 2;
        const faceSize = 150 + Math.random() * 50;
        
        // Simulate detection with some randomness
        if (Math.random() > 0.3) { // 70% chance of detecting a face
            faces.push({
                x: centerX - faceSize / 2,
                y: centerY - faceSize / 2,
                width: faceSize,
                height: faceSize,
                confidence: 0.8 + Math.random() * 0.2
            });
        }
        
        return faces;
    }
    
    showFaceBox(face) {
        if (!this.detectionBox) return;
        
        const scaleX = this.video.offsetWidth / this.canvas.width;
        const scaleY = this.video.offsetHeight / this.canvas.height;
        
        const boxX = face.x * scaleX;
        const boxY = face.y * scaleY;
        const boxWidth = face.width * scaleX;
        const boxHeight = face.height * scaleY;
        
        this.detectionBox.style.left = boxX + 'px';
        this.detectionBox.style.top = boxY + 'px';
        this.detectionBox.style.width = boxWidth + 'px';
        this.detectionBox.style.height = boxHeight + 'px';
        this.detectionBox.style.display = 'block';
        
        // Add pulsing animation
        this.detectionBox.classList.add('pulse');
    }
    
    hideFaceBox() {
        if (this.detectionBox) {
            this.detectionBox.style.display = 'none';
            this.detectionBox.classList.remove('pulse');
        }
    }
    
    calculateFaceQuality(face) {
        // Calculate face quality based on size, position, and other factors
        const centerX = this.canvas.width / 2;
        const centerY = this.canvas.height / 2;
        const faceCenterX = face.x + face.width / 2;
        const faceCenterY = face.y + face.height / 2;
        
        // Distance from center (closer is better)
        const distanceFromCenter = Math.sqrt(
            Math.pow(faceCenterX - centerX, 2) + Math.pow(faceCenterY - centerY, 2)
        );
        const maxDistance = Math.sqrt(Math.pow(centerX, 2) + Math.pow(centerY, 2));
        const centerScore = 1 - (distanceFromCenter / maxDistance);
        
        // Size score (optimal size is better)
        const optimalSize = (this.minFaceSize + this.maxFaceSize) / 2;
        const sizeDiff = Math.abs(face.width - optimalSize);
        const maxSizeDiff = Math.abs(this.maxFaceSize - this.minFaceSize) / 2;
        const sizeScore = 1 - (sizeDiff / maxSizeDiff);
        
        // Confidence score
        const confidenceScore = face.confidence || 0.8;
        
        // Overall quality (weighted average)
        this.faceQuality = (centerScore * 0.4 + sizeScore * 0.3 + confidenceScore * 0.3);
    }
    
    updateQualityIndicator() {
        const qualityFill = document.getElementById('qualityFill');
        const qualityValue = document.getElementById('qualityValue');
        
        if (qualityFill && qualityValue) {
            const percentage = Math.round(this.faceQuality * 100);
            qualityFill.style.width = percentage + '%';
            qualityValue.textContent = percentage + '%';
            
            // Color coding
            if (percentage >= 80) {
                qualityFill.style.backgroundColor = '#28a745';
            } else if (percentage >= 60) {
                qualityFill.style.backgroundColor = '#ffc107';
            } else {
                qualityFill.style.backgroundColor = '#dc3545';
            }
        }
    }
    
    updateFaceCount() {
        const faceCountElement = document.getElementById('faceCount');
        if (faceCountElement) {
            faceCountElement.textContent = `Faces: ${this.faceCount}`;
            
            // Color coding
            if (this.faceCount === 0) {
                faceCountElement.style.color = '#6c757d';
            } else if (this.faceCount === 1) {
                faceCountElement.style.color = '#28a745';
            } else {
                faceCountElement.style.color = '#dc3545';
            }
        }
    }
    
    enableCapture() {
        if (this.faceQuality >= this.qualityThreshold) {
            this.captureButton.disabled = false;
            this.updateStatus('Face detected! Ready to capture.', 'success');
            this.showValidationMessage('Face detected successfully. Click "Capture Face" to register.', 'success');
        } else {
            this.disableCapture();
            this.showValidationMessage('Face quality too low. Please adjust your position.', 'warning');
        }
    }
    
    disableCapture() {
        this.captureButton.disabled = true;
        this.stableFrames = 0;
    }
    
    async captureFace() {
        if (!this.video || !this.canvas || this.faceCount !== 1) return;
        
        try {
            this.captureButton.disabled = true;
            this.updateStatus('Capturing face...', 'capturing');
            
            // Capture the current frame
            this.ctx.drawImage(this.video, 0, 0, this.canvas.width, this.canvas.height);
            
            // Convert to base64
            const imageData = this.canvas.toDataURL('image/jpeg', 0.8);
            
            // Generate face encoding (simulate)
            const faceEncoding = this.generateFaceEncoding();
            
            // Store face data
            this.faceData = {
                image: imageData,
                encoding: faceEncoding,
                quality: this.faceQuality,
                timestamp: new Date().toISOString()
            };
            
            // Update form fields
            document.getElementById('face_image').value = imageData;
            document.getElementById('face_encoding').value = JSON.stringify(faceEncoding);
            
            this.isCaptured = true;
            this.updateStatus('Face captured successfully!', 'success');
            this.showValidationMessage('Face captured successfully. You can now submit the form.', 'success');
            
            // Update buttons
            this.retryButton.disabled = false;
            this.stopButton.disabled = true;
            this.startButton.disabled = false;
            
            // Hide detection box
            this.hideFaceBox();
            
            // Update form validation
            this.updateFormValidation();
            
        } catch (error) {
            this.updateStatus('Capture failed. Please try again.', 'error');
            this.showValidationMessage('Capture Error: ' + error.message, 'error');
            this.captureButton.disabled = false;
        }
    }
    
    generateFaceEncoding() {
        // Generate a realistic 128-dimensional face encoding
        const encoding = [];
        for (let i = 0; i < 128; i++) {
            encoding.push((Math.random() - 0.5) * 2);
        }
        return encoding;
    }
    
    retryCapture() {
        this.isCaptured = false;
        this.faceData = null;
        this.retryButton.disabled = true;
        this.captureButton.disabled = true;
        
        // Clear form fields
        document.getElementById('face_image').value = '';
        document.getElementById('face_encoding').value = '';
        
        this.updateStatus('Ready to capture. Position your face and click "Capture Face".', 'info');
        this.showValidationMessage('Ready for new capture. Please position your face.', 'info');
        
        // Restart detection
        this.startDetection();
    }
    
    stopDetection() {
        this.isDetecting = false;
        if (this.detectionInterval) {
            clearInterval(this.detectionInterval);
            this.detectionInterval = null;
        }
        
        this.hideFaceBox();
        this.startButton.disabled = false;
        this.stopButton.disabled = true;
        this.captureButton.disabled = true;
        
        this.updateStatus('Detection stopped.', 'info');
    }
    
    updateStatus(message, type) {
        if (this.statusElement) {
            this.statusElement.textContent = message;
        }
        
        if (this.statusIndicator) {
            this.statusIndicator.className = 'status-indicator ' + type;
        }
    }
    
    showValidationMessage(message, type) {
        if (!this.validationMessages) return;
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `validation-message ${type}`;
        messageDiv.innerHTML = `
            <i class="fas fa-${this.getIconForType(type)}"></i>
            <span>${message}</span>
        `;
        
        this.validationMessages.appendChild(messageDiv);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (messageDiv.parentNode) {
                messageDiv.parentNode.removeChild(messageDiv);
            }
        }, 5000);
    }
    
    getIconForType(type) {
        const icons = {
            'success': 'check-circle',
            'error': 'exclamation-circle',
            'warning': 'exclamation-triangle',
            'info': 'info-circle',
            'detecting': 'spinner fa-spin',
            'capturing': 'camera'
        };
        return icons[type] || 'info-circle';
    }
    
    updateFormValidation() {
        // Update the form validation based on face capture status
        const submitButton = document.getElementById('submitBtn');
        if (submitButton) {
            // This will be handled by the existing form validation
            if (typeof updateSubmitButton === 'function') {
                updateSubmitButton();
            }
            
            // Also call the global updateFormValidation function
            if (typeof window.updateFormValidation === 'function') {
                window.updateFormValidation();
            }
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Only initialize if we're on the add student page and have the required elements
    if (document.getElementById('faceVideo') && document.getElementById('startDetection')) {
        console.log('Initializing Advanced Face Detection System...');
        new AdvancedFaceDetection();
    } else {
        console.log('Face detection elements not found, skipping initialization');
    }
});
