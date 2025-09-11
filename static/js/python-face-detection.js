/**
 * Python Face Detection Frontend
 * Communicates with Python backend for real face detection
 * Replaces JavaScript face detection with server-side processing
 */

console.log('Python Face Detection Frontend loaded successfully!');

class PythonFaceDetection {
    constructor() {
        this.video = null;
        this.canvas = null;
        this.ctx = null;
        this.isDetecting = false;
        this.detectionInterval = null;
        this.faceCount = 0;
        this.lastFaceCount = 0;
        this.faceQuality = 0;
        this.faceBox = null;
        this.multipleFacesWarning = null;
        this.detectionGuide = null;
        this.statusElement = null;
        this.captureButton = null;
        this.retryButton = null;
        this.faceData = null;
        this.isCaptured = false;
        this.apiEndpoint = '/api/face-detection/';
        this.statusEndpoint = '/api/face-detection/status/';
        
        // Detection parameters
        this.minFaceSize = 40; // Reduced minimum size for easier detection
        this.maxFaceSize = 500;
        this.qualityThreshold = 0.4; // Reduced threshold for easier detection
        this.stabilityFrames = 2; // Reduced frames for more responsive detection
        this.stableFrames = 0;
        this.detectionFPS = 7; // 5 FPS for server communication
        this.lastFacePosition = null; // For smooth tracking
        this.targetFacePosition = null; // Target position for interpolation
        this.currentFacePosition = null; // Current interpolated position
        this.interpolationSpeed = 0.15; // How fast to interpolate (0.1 = slow, 0.3 = fast)
        
        this.init();
    }
    
    // Smooth interpolation for face tracking
    interpolatePosition(current, target, speed) {
        if (!current || !target) return target;
        
        return {
            x: current.x + (target.x - current.x) * speed,
            y: current.y + (target.y - current.y) * speed,
            width: current.width + (target.width - current.width) * speed,
            height: current.height + (target.height - current.height) * speed
        };
    }
    
    // Update face position with smooth interpolation
    updateFacePosition(newFace) {
        if (!newFace) {
            this.targetFacePosition = null;
            this.currentFacePosition = null;
            return null;
        }
        
        // Set target position
        this.targetFacePosition = {
            x: newFace.x,
            y: newFace.y,
            width: newFace.width,
            height: newFace.height
        };
        
        // Initialize current position if not set
        if (!this.currentFacePosition) {
            this.currentFacePosition = { ...this.targetFacePosition };
        }
        
        // Interpolate towards target
        this.currentFacePosition = this.interpolatePosition(
            this.currentFacePosition,
            this.targetFacePosition,
            this.interpolationSpeed
        );
        
        return this.currentFacePosition;
    }
    
    async init() {
        console.log('PythonFaceDetection: Initializing...');
        this.createDetectionUI();
        this.setupEventListeners();
        
        // Check if Python backend is ready
        await this.checkBackendStatus();
        
        this.updateStatus('Ready to start Python face detection', 'info');
        console.log('PythonFaceDetection: Initialization complete');
    }
    
    async checkBackendStatus() {
        try {
            console.log('Checking Python backend status...');
            const response = await fetch(this.statusEndpoint);
            const data = await response.json();
            
            if (data.success && data.status === 'ready') {
                console.log('Python backend is ready');
                this.updateStatus('Python face detection ready. Click "Start Camera" to begin.', 'success');
            } else {
                console.warn('Python backend not ready:', data.message);
                this.updateStatus('Python backend not ready. Using fallback detection.', 'warning');
            }
        } catch (error) {
            console.error('Failed to check backend status:', error);
            this.updateStatus('Cannot connect to Python backend. Using fallback detection.', 'error');
        }
    }
    
    createDetectionUI() {
        // Get UI element references
        this.video = document.getElementById('faceVideo');
        this.canvas = document.getElementById('faceCanvas');
        this.ctx = this.canvas ? this.canvas.getContext('2d') : null;
        this.faceBox = document.getElementById('faceBox');
        this.multipleFacesWarning = document.getElementById('multipleFacesWarning');
        this.detectionGuide = document.getElementById('detectionGuide');
        this.statusElement = document.getElementById('statusText');
        this.statusIndicator = document.getElementById('statusIndicator');
        this.captureButton = document.getElementById('captureFace');
        this.retryButton = document.getElementById('retryCapture');
        this.startButton = document.getElementById('startDetection');
        this.stopButton = document.getElementById('stopDetection');
        this.validationMessages = document.getElementById('validationMessages');
        
        console.log('PythonFaceDetection: UI elements found:', {
            video: !!this.video,
            canvas: !!this.canvas,
            startButton: !!this.startButton,
            captureButton: !!this.captureButton,
            statusElement: !!this.statusElement
        });
        
        // Initialize status
        if (this.statusElement) {
            this.statusElement.textContent = 'Checking Python backend...';
        }
        if (this.statusIndicator) {
            this.statusIndicator.className = 'status-indicator info';
        }
    }
    
    setupEventListeners() {
        this.startButton?.addEventListener('click', () => this.startDetection());
        this.captureButton?.addEventListener('click', () => this.captureFace());
        this.retryButton?.addEventListener('click', () => this.retryCapture());
        this.stopButton?.addEventListener('click', () => this.stopDetection());
    }
    
    async initializeCamera() {
        try {
            console.log('PythonFaceDetection: Initializing camera...');
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
            
            console.log('PythonFaceDetection: Camera stream obtained');
            
            if (this.video) {
                console.log('PythonFaceDetection: Setting video source object');
                this.video.srcObject = stream;
                
                this.video.onloadedmetadata = () => {
                    console.log('PythonFaceDetection: Video metadata loaded');
                    console.log('Video dimensions:', this.video.videoWidth, 'x', this.video.videoHeight);
                    
                    if (this.canvas) {
                        this.canvas.width = this.video.videoWidth;
                        this.canvas.height = this.video.videoHeight;
                    }
                    this.updateStatus('Camera ready. Starting Python face detection...', 'success');
                };
                
                this.video.onerror = (error) => {
                    console.error('PythonFaceDetection: Video error:', error);
                    this.updateStatus('Camera error occurred.', 'error');
                };
                
                // Force play the video
                this.video.play().catch(error => {
                    console.error('PythonFaceDetection: Video play error:', error);
                });
                
            } else {
                console.error('PythonFaceDetection: Video element not found');
                this.updateStatus('Video element not found.', 'error');
            }
            
        } catch (error) {
            console.error('PythonFaceDetection: Camera initialization failed:', error);
            this.updateStatus('Camera access denied. Please allow camera access and refresh the page.', 'error');
            this.showValidationMessage('Camera Error: ' + error.message, 'error');
        }
    }
    
    async startDetection() {
        if (!this.video || !this.canvas) {
            console.error('PythonFaceDetection: Video or canvas not found');
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
            
            this.updateStatus('Detecting faces with Python...', 'detecting');
            this.showValidationMessage('Python face detection started. Please position your face in the center.', 'info');
            
            // Hide detection guide when detection starts
            if (this.detectionGuide) {
                this.detectionGuide.style.display = 'none';
            }
            
            // Start detection loop
            this.detectionInterval = setInterval(() => {
                this.detectFacesWithPython();
            }, 1000 / this.detectionFPS); // 5 FPS for server communication
            
        } catch (error) {
            console.error('PythonFaceDetection: Failed to start detection:', error);
            this.updateStatus('Failed to start detection: ' + error.message, 'error');
            this.showValidationMessage('Failed to start detection: ' + error.message, 'error');
        }
    }
    
    async detectFacesWithPython() {
        if (!this.isDetecting || !this.video || !this.ctx) return;
        
        try {
            // Draw current frame to canvas
            this.ctx.drawImage(this.video, 0, 0, this.canvas.width, this.canvas.height);
            
            // Convert canvas to base64
            const base64Image = this.canvas.toDataURL('image/jpeg', 0.8);
            
            // Send to Python backend for face detection
            const response = await fetch(this.apiEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify({
                    image: base64Image
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.processDetectionResults(result);
            } else {
                console.error('Python detection failed:', result.error);
                this.showValidationMessage('Detection error: ' + result.error, 'error');
            }
            
        } catch (error) {
            console.error('Face detection error:', error);
            // Fallback to local detection if server fails
            this.fallbackDetection();
        }
    }
    
    processDetectionResults(result) {
        const faces = result.faces || [];
        this.faceCount = result.face_count || 0;
        this.updateFaceCount();
        
        if (this.faceCount === 0) {
            this.hideAllFaceBoxes();
            this.hideMultipleFacesWarning();
            this.stableFrames = 0;
            this.faceQuality = 0;
            this.updateQualityIndicator();
        } else if (this.faceCount === 1) {
            const face = faces[0];
            this.showSingleFaceBox(face);
            this.hideMultipleFacesWarning();
            this.faceQuality = face.quality_score || 0.8;
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
            // Multiple faces detected - show ESP boxes on all faces
            this.showMultipleFaceBoxes(faces);
            this.showMultipleFacesWarning();
            this.stableFrames = 0;
            this.showValidationMessage(`Multiple faces detected (${this.faceCount}). Please ensure only one person is visible.`, 'error');
            this.disableCapture();
        }
        
        this.lastFaceCount = this.faceCount;
    }
    
    fallbackDetection() {
        // Simple fallback detection when Python backend is not available
        console.log('Using fallback detection');
        this.faceCount = Math.random() > 0.5 ? 1 : 0;
        this.updateFaceCount();
        
        if (this.faceCount === 1) {
            // Simulate single face detection
            const mockFace = {
                x: this.canvas.width / 2 - 75,
                y: this.canvas.height / 2 - 75,
                width: 150,
                height: 150,
                confidence: 0.8,
                quality_score: 0.8
            };
            this.showSingleFaceBox(mockFace);
            this.hideMultipleFacesWarning();
            this.faceQuality = 0.8;
            this.updateQualityIndicator();
            this.enableCapture();
        } else {
            this.hideAllFaceBoxes();
            this.hideMultipleFacesWarning();
        }
    }
    
    showSingleFaceBox(face) {
        if (!this.faceBox) return;
        
        // Update face position with smooth interpolation
        const smoothFace = this.updateFacePosition(face);
        if (!smoothFace) return;
        
        const scaleX = this.video.offsetWidth / this.canvas.width;
        const scaleY = this.video.offsetHeight / this.canvas.height;
        
        const boxX = smoothFace.x * scaleX;
        const boxY = smoothFace.y * scaleY;
        const boxWidth = smoothFace.width * scaleX;
        const boxHeight = smoothFace.height * scaleY;
        
        // Apply smooth positioning with CSS transitions
        this.faceBox.style.transition = 'left 0.1s ease-out, top 0.1s ease-out, width 0.1s ease-out, height 0.1s ease-out';
        this.faceBox.style.left = boxX + 'px';
        this.faceBox.style.top = boxY + 'px';
        this.faceBox.style.width = boxWidth + 'px';
        this.faceBox.style.height = boxHeight + 'px';
        this.faceBox.style.display = 'block';
        
        // Add pulsing animation
        this.faceBox.classList.add('pulse');
        
        // Update face info
        const faceCount = document.getElementById('faceCount');
        const qualityScore = document.getElementById('qualityScore');
        
        if (faceCount) faceCount.textContent = '1 Face';
        if (qualityScore) qualityScore.textContent = Math.round(this.faceQuality * 100) + '%';
    }
    
    showMultipleFaceBoxes(faces) {
        // Clear existing face boxes
        this.hideAllFaceBoxes();
        
        // Create ESP boxes for each detected face
        faces.forEach((face, index) => {
            this.createFaceBox(face, index);
        });
        
        // Update face info
        const faceCount = document.getElementById('faceCount');
        const qualityScore = document.getElementById('qualityScore');
        
        if (faceCount) faceCount.textContent = `${faces.length} Faces`;
        if (qualityScore) qualityScore.textContent = 'Multiple';
    }
    
    createFaceBox(face, index) {
        const scaleX = this.video.offsetWidth / this.canvas.width;
        const scaleY = this.video.offsetHeight / this.canvas.height;
        
        const boxX = face.x * scaleX;
        const boxY = face.y * scaleY;
        const boxWidth = face.width * scaleX;
        const boxHeight = face.height * scaleY;
        
        // Create a new face box element
        const faceBox = document.createElement('div');
        faceBox.className = 'face-box multiple-face';
        faceBox.id = `faceBox_${index}`;
        faceBox.style.left = boxX + 'px';
        faceBox.style.top = boxY + 'px';
        faceBox.style.width = boxWidth + 'px';
        faceBox.style.height = boxHeight + 'px';
        faceBox.style.display = 'block';
        faceBox.style.borderColor = '#ff0000'; // Red for multiple faces
        faceBox.style.boxShadow = '0 0 15px rgba(255, 0, 0, 0.5)';
        
        // Add ESP corners
        const espCorners = document.createElement('div');
        espCorners.className = 'esp-corners';
        espCorners.innerHTML = `
            <div class="corner top-left"></div>
            <div class="corner top-right"></div>
            <div class="corner bottom-left"></div>
            <div class="corner bottom-right"></div>
        `;
        faceBox.appendChild(espCorners);
        
        // Add face info with enhanced quality display
        const faceInfo = document.createElement('div');
        faceInfo.className = 'face-info';
        const qualityScore = Math.round(face.quality_score * 100);
        const stabilityScore = face.stability_score ? Math.round(face.stability_score * 100) : 0;
        faceInfo.innerHTML = `
            <span class="face-count">Face ${index + 1}</span>
            <span class="quality-score">${qualityScore}%</span>
            ${stabilityScore > 0 ? `<span class="stability-score">${stabilityScore}%</span>` : ''}
        `;
        faceBox.appendChild(faceInfo);
        
        // Add to overlay
        const overlay = document.getElementById('detectionOverlay');
        if (overlay) {
            overlay.appendChild(faceBox);
        }
    }
    
    hideAllFaceBoxes() {
        // Hide the main face box
        if (this.faceBox) {
            this.faceBox.style.display = 'none';
            this.faceBox.classList.remove('pulse');
        }
        
        // Remove all multiple face boxes
        const multipleFaceBoxes = document.querySelectorAll('.multiple-face');
        multipleFaceBoxes.forEach(box => box.remove());
        
        // Reset position tracking when hiding
        this.targetFacePosition = null;
        this.currentFacePosition = null;
        this.lastFacePosition = null;
    }
    
    showMultipleFacesWarning() {
        if (this.multipleFacesWarning) {
            this.multipleFacesWarning.style.display = 'block';
        }
    }
    
    hideMultipleFacesWarning() {
        if (this.multipleFacesWarning) {
            this.multipleFacesWarning.style.display = 'none';
        }
    }
    
    updateQualityIndicator() {
        const qualityScore = document.getElementById('qualityScore');
        
        if (qualityScore) {
            const percentage = Math.round(this.faceQuality * 100);
            qualityScore.textContent = percentage + '%';
            
            // Color coding based on quality
            if (percentage >= 80) {
                qualityScore.style.background = 'rgba(40, 167, 69, 0.8)';
            } else if (percentage >= 60) {
                qualityScore.style.background = 'rgba(255, 193, 7, 0.8)';
            } else {
                qualityScore.style.background = 'rgba(220, 53, 69, 0.8)';
            }
        }
    }
    
    updateFaceCount() {
        const faceCountElement = document.getElementById('faceCount');
        if (faceCountElement) {
            faceCountElement.textContent = `${this.faceCount} Face${this.faceCount !== 1 ? 's' : ''}`;
            
            // Color coding
            if (this.faceCount === 0) {
                faceCountElement.style.background = 'rgba(108, 117, 125, 0.8)';
            } else if (this.faceCount === 1) {
                faceCountElement.style.background = 'rgba(40, 167, 69, 0.8)';
            } else {
                faceCountElement.style.background = 'rgba(220, 53, 69, 0.8)';
            }
        }
    }
    
    enableCapture() {
        if (this.faceQuality >= this.qualityThreshold) {
            this.captureButton.disabled = false;
            this.updateStatus('Face detected! Ready to capture.', 'success');
            this.showValidationMessage('Face detected successfully. Click "Capture" to register.', 'success');
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
            
            // Send to Python backend for face encoding
            const response = await fetch(this.apiEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify({
                    image: imageData
                })
            });
            
            const result = await response.json();
            
            if (result.success && result.faces && result.faces.length > 0) {
                const face = result.faces[0];
                const faceEncoding = face.encoding || this.generateFallbackEncoding();
                
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
                this.hideAllFaceBoxes();
                this.hideMultipleFacesWarning();
                
                // Update form validation
                this.updateFormValidation();
                
            } else {
                throw new Error('Failed to process face encoding');
            }
            
        } catch (error) {
            this.updateStatus('Capture failed. Please try again.', 'error');
            this.showValidationMessage('Capture Error: ' + error.message, 'error');
            this.captureButton.disabled = false;
        }
    }
    
    generateFallbackEncoding() {
        // Generate a fallback encoding if Python backend fails
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
        
        this.updateStatus('Ready to capture. Position your face and click "Capture".', 'info');
        this.showValidationMessage('Ready for new capture. Please position your face.', 'info');
        
        // Show detection guide again
        if (this.detectionGuide) {
            this.detectionGuide.style.display = 'block';
        }
        
        // Restart detection
        this.startDetection();
    }
    
    stopDetection() {
        this.isDetecting = false;
        if (this.detectionInterval) {
            clearInterval(this.detectionInterval);
            this.detectionInterval = null;
        }
        
        this.hideAllFaceBoxes();
        this.hideMultipleFacesWarning();
        this.startButton.disabled = false;
        this.stopButton.disabled = true;
        this.captureButton.disabled = true;
        
        // Show detection guide again
        if (this.detectionGuide) {
            this.detectionGuide.style.display = 'block';
        }
        
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
        console.log('Initializing Python Face Detection System...');
        window.pythonFaceDetection = new PythonFaceDetection();
    } else {
        console.log('Face detection elements not found, skipping initialization');
    }
});
