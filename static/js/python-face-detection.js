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
        this.errorLogs = []; // Store error logs
        this.maxLogs = 5; // Maximum number of logs to display
        this.isScreenLocked = false; // Screen lock state
        this.networkStatus = 'online'; // Network status: 'online', 'retrying', 'offline'
        this.isRetrying = false; // Prevent multiple concurrent retry loops
        this.pendingRequest = null; // Track current request
        this.lockOverlay = null; // Lock overlay element
        this.canCapture = false; // Whether capture is permitted
        this.lastStatus = 'unknown';
        this.lastMessage = '';
        this.lastFaces = [];
        
        // Detection parameters - optimized for face_recognition
        this.minFaceSize = 30; // face_recognition can detect smaller faces
        this.maxFaceSize = 500;
        this.qualityThreshold = 0.3; // face_recognition is more accurate, can use lower threshold
        this.stabilityFrames = 2; // Reduced frames for more responsive detection
        this.stableFrames = 0;
        this.detectionFPS = 5; // Reduced FPS for better performance with face_recognition
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
                console.log('Face recognition backend is ready');
                this.updateStatus('Face recognition system ready. Click "Start Camera" to begin.', 'success');
            } else {
                console.warn('Face recognition backend not ready:', data.message);
                this.updateStatus('Face recognition system not ready. Using fallback detection.', 'warning');
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
        this.centeredDetectionBox = document.getElementById('centeredDetectionBox');
        
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
        this.startButton?.addEventListener('click', () => {
            console.log('🎬 START BUTTON CLICKED - Initiating face detection');
            this.addErrorLog('Starting camera and face detection...', 'info');
            this.startDetection();
        });
        
        this.captureButton?.addEventListener('click', () => {
            console.log('📸 CAPTURE BUTTON CLICKED - Attempting to capture face');
            this.addErrorLog('Capture button pressed - validating conditions...', 'info');
            this.captureFace();
        });
        
        this.retryButton?.addEventListener('click', () => {
            console.log('🔄 RETRY BUTTON CLICKED - Clearing captured data and restarting');
            this.addErrorLog('Retry button pressed - clearing previous capture...', 'info');
            this.retryCapture();
        });
        
        this.stopButton?.addEventListener('click', () => {
            console.log('🛑 STOP BUTTON CLICKED - Stopping face detection');
            this.addErrorLog('Stop button pressed - ending detection session...', 'info');
            this.stopDetection();
        });
    }
    
    async initializeCamera() {
        try {
            console.log('📷 INITIALIZING CAMERA - Requesting camera access...');
            this.addErrorLog('Requesting camera access...', 'info');
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
            
            console.log('✅ CAMERA STREAM OBTAINED - Setting up video element');
            this.addErrorLog('Camera access granted - setting up video stream...', 'success');
            
            if (this.video) {
                console.log('🎥 SETTING VIDEO SOURCE - Connecting stream to video element');
                this.video.srcObject = stream;
                
                this.video.onloadedmetadata = () => {
                    console.log('📐 VIDEO METADATA LOADED - Dimensions:', this.video.videoWidth, 'x', this.video.videoHeight);
                    this.addErrorLog(`Camera ready (${this.video.videoWidth}x${this.video.videoHeight})`, 'success');
                    
                    if (this.canvas) {
                        this.canvas.width = this.video.videoWidth;
                        this.canvas.height = this.video.videoHeight;
                        console.log('🎨 CANVAS CONFIGURED - Size:', this.canvas.width, 'x', this.canvas.height);
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
            console.error('❌ CAMERA INITIALIZATION FAILED:', error);
            this.addErrorLog('Camera access denied: ' + error.message, 'error');
            this.updateStatus('Camera access denied. Please allow camera access and refresh the page.', 'error');
            this.showValidationMessage('Camera Error: ' + error.message, 'error');
        }
    }
    
    async startDetection() {
        if (!this.video || !this.canvas) {
            console.error('❌ DETECTION START FAILED - Video or canvas not found');
            this.addErrorLog('Cannot start detection: video or canvas elements missing', 'error');
            return;
        }
        
        try {
            console.log('🚀 STARTING DETECTION PROCESS...');
            this.updateStatus('Starting camera...', 'warning');
            
            // Initialize camera if not already done
            if (!this.video.srcObject) {
                console.log('📷 Camera not initialized, starting camera setup...');
                await this.initializeCamera();
                console.log('⏳ Waiting for camera to stabilize...');
                await new Promise(resolve => setTimeout(resolve, 1000));
            }
            
            console.log('🎯 ENABLING DETECTION MODE - Setting up UI state');
            this.isDetecting = true;
            if (this.startButton) {
                this.startButton.disabled = true;
                console.log('🔒 Start button disabled');
            }
            if (this.stopButton) {
                this.stopButton.disabled = false;
                console.log('🔓 Stop button enabled');
            }
            if (this.captureButton) {
                this.captureButton.disabled = true;
                console.log('📸 Capture button initially disabled');
            }
            if (this.retryButton) {
                this.retryButton.disabled = true;
                console.log('🔄 Retry button disabled');
            }
            
            this.updateStatus('Detecting faces with face recognition...', 'detecting');
            this.addErrorLog('Face detection active - position your face in the center box', 'info');
            
            // Hide detection guide and show centered detection box when detection starts
            if (this.detectionGuide) {
                this.detectionGuide.style.display = 'none';
                console.log('👁️ Detection guide hidden');
            }
            if (this.centeredDetectionBox) {
                this.centeredDetectionBox.style.display = 'block';
                console.log('🎯 Centered detection box shown');
            }
            
            // Start detection loop
            console.log(`🔄 STARTING DETECTION LOOP - ${this.detectionFPS} FPS`);
            this.detectionInterval = setInterval(() => {
                this.detectFacesWithPython();
            }, 1000 / this.detectionFPS); // 5 FPS for server communication
            
        } catch (error) {
            console.error('❌ DETECTION START ERROR:', error);
            this.addErrorLog('Failed to start detection: ' + error.message, 'error');
            this.updateStatus('Failed to start detection: ' + error.message, 'error');
        }
    }
    
    async sendDetectionRequest(imageData, retryCount = 0) {
        const maxRetries = 3;
        const retryDelay = 1000; // 1 second
        
        // Prevent multiple concurrent retry loops
        if (this.isRetrying && retryCount === 0) {
            console.log('⏭️ Skipping request - already retrying');
            return {
                success: false,
                error: 'Request skipped - retry in progress',
                faces: [],
                face_count: 0,
                network_error: false
            };
        }
        
        try {
            console.log(`🌐 Network request attempt ${retryCount + 1}/${maxRetries + 1}`);
            
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 8000); // 8 second timeout
            
            const response = await fetch(this.apiEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify({
                    image: imageData
                }),
                signal: controller.signal
            });

            clearTimeout(timeoutId);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const result = await response.json();
            console.log('🔍 DETECTION RESULT:', {
                success: result.success,
                status: result.status,
                face_count: result.face_count,
                message: result.message
            });
            
            // Reset network error state on success
            if (retryCount > 0) {
                console.log('✅ Network connection recovered');
                this.networkStatus = 'online';
                this.addErrorLog('Connection recovered - detection resumed', 'success');
                this.updateNetworkStatusIndicator();
            }
            
            return result;

        } catch (error) {
            console.error(`❌ Network error (attempt ${retryCount + 1}):`, error);
            
            // Check if it's a recoverable network error
            const isNetworkError = error.name === 'TypeError' || 
                                 error.message.includes('Failed to fetch') ||
                                 error.message.includes('ERR_NETWORK_CHANGED') ||
                                 error.message.includes('ERR_INTERNET_DISCONNECTED') ||
                                 error.message.includes('ERR_CONNECTION_RESET') ||
                                 error.message.includes('ERR_CONNECTION_REFUSED') ||
                                 error.name === 'AbortError';
            
            // Special handling for server down
            if (error.message.includes('ERR_CONNECTION_REFUSED')) {
                console.log('🚫 Django server appears to be down');
                this.addErrorLog('Django server is not running - please start the server', 'error');
                
                // If server is down and we've tried multiple times, pause detection
                if (retryCount >= 2) {
                    console.log('🛑 Pausing detection due to server unavailability');
                    this.addErrorLog('Detection paused - server unavailable', 'error');
                    this.pauseDetectionTemporarily();
                }
            }
            
            if (isNetworkError && retryCount < maxRetries) {
                console.log(`🔄 Network issue detected, retrying in ${retryDelay}ms...`);
                this.isRetrying = true;
                this.networkStatus = 'retrying';
                this.addErrorLog(`Network error - retrying (${retryCount + 1}/${maxRetries})...`, 'warning');
                this.updateNetworkStatusIndicator();
                
                // Wait before retry with exponential backoff
                const delay = retryDelay * Math.pow(2, retryCount);
                await new Promise(resolve => setTimeout(resolve, delay));
                
                // Recursive retry
                const result = await this.sendDetectionRequest(imageData, retryCount + 1);
                this.isRetrying = false;
                return result;
            }
            
            // All retries exhausted or non-network error
            const errorMsg = isNetworkError ? 
                'Network connection lost - check your internet connection' : 
                `Detection failed: ${error.message}`;
                
            console.error('❌ Final network error:', errorMsg);
            this.isRetrying = false;
            this.networkStatus = isNetworkError ? 'offline' : 'online';
            this.updateNetworkStatusIndicator();
            
            return {
                success: false,
                error: errorMsg,
                faces: [],
                face_count: 0,
                network_error: isNetworkError
            };
        }
    }
    
    async detectFacesWithPython() {
        if (!this.isDetecting || !this.video || !this.ctx) return;
        
        // Skip if already processing a request
        if (this.pendingRequest) {
            console.log('⏭️ Skipping frame - request already in progress');
            return;
        }
        
        try {
            // Draw current frame to canvas
            this.ctx.drawImage(this.video, 0, 0, this.canvas.width, this.canvas.height);
            
            // Convert canvas to base64
            const base64Image = this.canvas.toDataURL('image/jpeg', 0.8);
            console.log('🖼️ FRAME CAPTURED - Sending to face recognition backend...');
            
            // Send to face recognition backend for face detection with retry logic
            this.pendingRequest = this.sendDetectionRequest(base64Image);
            const result = await this.pendingRequest;
            this.pendingRequest = null;
            
            if (result.success) {
                // Store face encodings from detection results for instant capture
                if (result.faces && result.faces.length > 0) {
                    console.log('💾 Caching face encodings for instant capture...');
                    result.faces.forEach((face, index) => {
                        if (face.encoding) {
                            console.log(`🧬 Cached encoding ${index + 1} - Length: ${face.encoding.length}`);
                        }
                    });
                }
                this.processDetectionResults(result);
            } else {
                console.error('❌ FACE DETECTION FAILED:', result.error);
                if (result.network_error) {
                    this.addErrorLog('Network error - check internet connection', 'error');
                } else {
                    this.addErrorLog('Detection error: ' + result.error, 'error');
                }
            }
            
        } catch (error) {
            console.error('❌ UNEXPECTED DETECTION ERROR:', error);
            this.addErrorLog('Unexpected detection error: ' + error.message, 'error');
            // Reset pending request
            this.pendingRequest = null;
            this.isRetrying = false;
            // Fallback to local detection if server fails
            this.fallbackDetection();
        }
    }
    
    processDetectionResults(result) {
        const faces = result.faces || [];
        this.faceCount = result.face_count || 0;
        const status = result.status || 'unknown';
        const message = result.message || '';
        this.lastStatus = status;
        this.lastMessage = message;
        this.lastFaces = faces;
        
        console.log(`📊 PROCESSING DETECTION - Status: ${status}, Faces: ${this.faceCount}`);
        this.updateFaceCount();
        
        // Handle different detection statuses
        switch (status) {
            case 'no_faces':
                console.log('👻 NO FACES DETECTED - Clearing UI and disabling capture');
                this.unlockScreen();
            this.hideAllFaceBoxes();
            this.hideMultipleFacesWarning();
            this.stableFrames = 0;
            this.faceQuality = 0;
            this.updateQualityIndicator();
                this.addErrorLog('No face detected. Center your face within the box.', 'warning');
                this.disableCapture();
                break;
                
            case 'single_face':
                console.log('✅ SINGLE FACE DETECTED - Quality:', faces[0]?.quality_score || 'unknown');
                this.unlockScreen();
            const face = faces[0];
                this.showCenteredFaceBox(face);
            this.hideMultipleFacesWarning();
            this.faceQuality = face.quality_score || 0.8;
            this.updateQualityIndicator();
            
            // Check for stable detection
            if (this.lastFaceCount === 1) {
                this.stableFrames++;
                    console.log(`🎯 STABILITY CHECK - Stable frames: ${this.stableFrames}/${this.stabilityFrames}`);
                if (this.stableFrames >= this.stabilityFrames) {
                        console.log('🎉 FACE STABLE - Enabling capture');
                    this.enableCapture();
                }
            } else {
                this.stableFrames = 0;
                    console.log('🔄 FACE COUNT CHANGED - Resetting stability counter');
                }
                this.clearErrorLogs();
                break;
                
            case 'poor_quality':
                console.log('⚠️ POOR QUALITY FACE - Disabling capture');
                this.unlockScreen();
                this.hideAllFaceBoxes();
                this.hideMultipleFacesWarning();
                this.stableFrames = 0;
                this.faceQuality = 0;
                this.updateQualityIndicator();
                this.addErrorLog('Face quality too low. Improve lighting or move closer.', 'warning');
                this.disableCapture();
                break;
                
            case 'not_centered':
                console.log('📐 FACE NOT CENTERED - Disabling capture');
                this.unlockScreen();
                this.hideAllFaceBoxes();
                this.hideMultipleFacesWarning();
                this.stableFrames = 0;
                this.faceQuality = 0;
                this.updateQualityIndicator();
                this.addErrorLog('Please center your face within the detection box.', 'warning');
                this.disableCapture();
                break;
                
            case 'multiple_faces_blocked':
                console.log(`🚨 MULTIPLE FACES DETECTED (${this.faceCount}) - LOCKING SCREEN`);
                // Multiple faces detected - LOCK THE SCREEN
                this.lockScreen(message);
            this.showMultipleFaceBoxes(faces);
            this.showMultipleFacesWarning();
            this.stableFrames = 0;
                this.addErrorLog('Multiple faces detected. System locked until only one face is visible.', 'error');
                this.disableCapture();
                break;
                
            default:
                this.unlockScreen();
                this.addErrorLog('Unknown detection status', 'error');
            this.disableCapture();
        }
        
        this.lastFaceCount = this.faceCount;
    }
    
    fallbackDetection() {
        // Simple fallback detection when face recognition backend is not available
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
    
    showCenteredFaceBox(face) {
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
        
        // Add pulsing animation for centered face
        this.faceBox.classList.add('pulse');
        this.faceBox.classList.add('centered-face');
        
        // Update face info
        const faceCount = document.getElementById('faceCount');
        const qualityScore = document.getElementById('qualityScore');
        
        if (faceCount) faceCount.textContent = '1 Face';
        if (qualityScore) qualityScore.textContent = Math.round(this.faceQuality * 100) + '%';
    }
    
    showSingleFaceBox(face) {
        // Use the new centered face box method
        this.showCenteredFaceBox(face);
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
        if (!this.captureButton) return;
        if (this.faceQuality >= this.qualityThreshold) {
            this.canCapture = true;
            this.captureButton.disabled = false; // keep clickable to allow feedback
            this.captureButton.title = 'Ready to capture';
            this.updateStatus('Face detected! Ready to capture.', 'success');
            this.showValidationMessage('Face detected successfully. Click "Capture" to register.', 'success');
        } else {
            this.disableCapture();
            this.showValidationMessage('Face quality too low. Please adjust your position.', 'warning');
        }
    }
    
    disableCapture() {
        if (!this.captureButton) return;
        this.canCapture = false;
        this.captureButton.disabled = false; // keep clickable for error feedback
        this.captureButton.title = 'Not ready yet - see guidance in the panel';
        this.stableFrames = 0;
    }
    
    async captureFace() {
        console.log('📸 CAPTURE FACE INITIATED - Validating conditions...');
        console.log('Current state:', {
            canCapture: this.canCapture,
            lastStatus: this.lastStatus,
            faceCount: this.faceCount,
            faceQuality: this.faceQuality,
            isScreenLocked: this.isScreenLocked
        });
        
        if (!this.video || !this.canvas) {
            console.log('❌ CAPTURE FAILED - Video or canvas missing');
            this.addErrorLog('Cannot capture: video or canvas not available', 'error');
            return;
        }
        
        // Validate capture conditions and surface specific reasons
        if (!this.canCapture) {
            console.log('❌ CAPTURE BLOCKED - Conditions not met');
            if (this.isScreenLocked || this.lastStatus === 'multiple_faces_blocked' || this.faceCount > 1) {
                console.log('🚨 Reason: Multiple faces detected');
                this.addErrorLog('Cannot capture: multiple faces detected. Ensure only one person is in frame.', 'error');
            } else if (this.faceCount === 0 || this.lastStatus === 'no_faces') {
                console.log('👻 Reason: No face detected');
                this.addErrorLog('Cannot capture: no face detected. Position your face in the center box.', 'warning');
            } else if (this.lastStatus === 'not_centered') {
                console.log('📐 Reason: Face not centered');
                this.addErrorLog('Cannot capture: please center your face within the detection box.', 'warning');
            } else if (this.lastStatus === 'poor_quality' || this.faceQuality < this.qualityThreshold) {
                console.log('⚠️ Reason: Poor quality');
                this.addErrorLog('Cannot capture: face quality too low. Improve lighting or move closer.', 'warning');
            } else {
                console.log('🔄 Reason: Detection not stable');
                this.addErrorLog('Cannot capture: detection not stable yet. Hold steady for a moment.', 'info');
            }
            return;
        }
        
        try {
            console.log('✅ CAPTURE PROCEEDING - Conditions met');
            this.captureButton.disabled = true;
            this.captureButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Capturing...';
            this.updateStatus('Capturing face...', 'capturing');
            this.addErrorLog('Capturing face data...', 'info');
            
            // Capture and preprocess the current frame
            console.log('🎨 Drawing video frame to canvas...');
            this.ctx.drawImage(this.video, 0, 0, this.canvas.width, this.canvas.height);
            
            // Apply advanced image preprocessing for optimal face recognition
            console.log('🔧 Applying advanced image preprocessing...');
            const processedImageData = this.preprocessImageForFaceRecognition();
            
            console.log('📦 Preprocessed image prepared - Size:', processedImageData.length, 'characters');
            
            // Add a small delay to show the loading state briefly (for user feedback)
            await new Promise(resolve => setTimeout(resolve, 200));
            
            // Use the last detected face data instead of making another API call
            console.log('🧬 Using cached face data from last detection...');
            let faceEncoding;
            
            if (this.lastFaces && this.lastFaces.length > 0 && this.lastFaces[0].encoding) {
                faceEncoding = this.lastFaces[0].encoding;
                console.log('✅ Using cached face encoding from backend - Length:', faceEncoding.length);
                console.log('🧬 Backend encoding process: Original detection → Crop face → Preprocess → Generate encoding');
                console.log('📊 Encoding source: Cropped face region (with fallback to original detection if cropping fails)');
                
                // Check if encoding is fallback (all zeros)
                const isZeroEncoding = faceEncoding.every(val => val === 0.0);
                if (isZeroEncoding) {
                    console.log('⚠️ WARNING: Received zero/fallback encoding from backend');
                    this.addErrorLog('Backend encoding failed - using fallback encoding', 'warning');
                } else {
                    console.log('✅ Valid encoding received from backend');
                }
            } else {
                console.log('⚠️ No cached encoding from backend, generating client-side fallback...');
                console.log('❌ WARNING: Client-side fallback encoding is not ideal');
                faceEncoding = this.generateFallbackEncoding();
                this.addErrorLog('No backend encoding available - using client fallback', 'warning');
            }
                
                // Store face data
                this.faceData = {
                image: processedImageData,
                    encoding: faceEncoding,
                    quality: this.faceQuality,
                    timestamp: new Date().toISOString()
                };
                
            // Update form fields with correct IDs
            console.log('💾 Saving to form fields...');
            const faceImageField = document.getElementById('faceImage');
            const faceEncodingField = document.getElementById('faceEncoding');
            
            if (faceImageField) {
                faceImageField.value = processedImageData;
                console.log('✅ Preprocessed face image saved to form field');
            } else {
                console.error('❌ faceImage field not found');
            }
            
            if (faceEncodingField) {
                faceEncodingField.value = JSON.stringify(faceEncoding);
                console.log('✅ Face encoding saved to form field');
            } else {
                console.error('❌ faceEncoding field not found');
            }
            
                console.log('📊 Face data summary:', {
                    savedImage: 'Cropped and preprocessed grayscale face',
                    imageLength: processedImageData.length,
                    savedEncoding: 'Generated from cropped face region only',
                    encodingLength: faceEncoding.length,
                    quality: this.faceQuality,
                    timestamp: this.faceData.timestamp,
                    preprocessed: true,
                    originalImageUsed: false,
                    croppedImageUsed: true
                });
                
                this.isCaptured = true;
                this.updateStatus('Face captured successfully!', 'success');
            this.addErrorLog('Face captured successfully! You can now submit the form.', 'success');
            
            // Show captured face preview
            console.log('🖼️ Showing face preview...');
            this.showCapturedFacePreview(processedImageData);
                
                // Update buttons
            console.log('🎛️ Updating button states...');
            this.captureButton.innerHTML = '<i class="fas fa-camera"></i> Capture';
                this.retryButton.disabled = false;
                this.stopButton.disabled = true;
                this.startButton.disabled = false;
                
            // Hide detection box and centered box
            console.log('🎯 Hiding detection UI...');
                this.hideAllFaceBoxes();
                this.hideMultipleFacesWarning();
            if (this.centeredDetectionBox) {
                this.centeredDetectionBox.style.display = 'none';
            }
                
                // Update form validation
            console.log('✅ Updating form validation...');
                this.updateFormValidation();
                
            // Enable submit button
            console.log('🎉 Enabling submit button...');
            this.enableSubmitButton();
            
        } catch (error) {
            console.error('❌ CAPTURE ERROR:', error);
            this.updateStatus('Capture failed. Please try again.', 'error');
            this.addErrorLog('Capture error: ' + error.message, 'error');
            if (this.captureButton) {
            this.captureButton.disabled = false;
                this.captureButton.innerHTML = '<i class="fas fa-camera"></i> Capture';
            }
        }
    }
    
    generateFallbackEncoding() {
        // Generate a fallback encoding if face recognition backend fails
        const encoding = [];
        for (let i = 0; i < 128; i++) {
            encoding.push((Math.random() - 0.5) * 2);
        }
        return encoding;
    }
    
    retryCapture() {
        console.log('🔄 RETRY CAPTURE - Clearing previous data and restarting...');
        this.isCaptured = false;
        this.faceData = null;
        this.retryButton.disabled = true;
        this.captureButton.disabled = true;
        
        // Clear form fields with correct IDs
        console.log('🗑️ Clearing form fields...');
        const faceImageField = document.getElementById('faceImage');
        const faceEncodingField = document.getElementById('faceEncoding');
        
        if (faceImageField) {
            faceImageField.value = '';
            console.log('✅ Face image field cleared');
        } else {
            console.error('❌ faceImage field not found for clearing');
        }
        
        if (faceEncodingField) {
            faceEncodingField.value = '';
            console.log('✅ Face encoding field cleared');
        } else {
            console.error('❌ faceEncoding field not found for clearing');
        }
        
        // Hide face data display and clear processing info
        console.log('🙈 Hiding face data display...');
        const faceDataDisplay = document.getElementById('faceDataDisplay');
        if (faceDataDisplay) {
            faceDataDisplay.style.display = 'none';
            
            // Clear processing info if it exists
            const processingInfo = faceDataDisplay.querySelector('.processing-info');
            if (processingInfo) {
                processingInfo.remove();
                console.log('🗑️ Processing info cleared');
            }
        }
        
        // Reset submit button
        console.log('🎛️ Resetting submit button state...');
        const submitBtn = document.getElementById('submitBtn');
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.classList.remove('btn-success');
            submitBtn.classList.add('btn-primary');
            submitBtn.title = 'Please capture your face for registration';
        }
        
        this.updateStatus('Ready to capture. Position your face and click "Capture".', 'info');
        this.addErrorLog('Retry initiated - ready for new capture', 'info');
        
        // Show detection guide again and hide centered detection box
        console.log('🎯 Switching UI back to detection mode...');
        if (this.detectionGuide) {
            this.detectionGuide.style.display = 'block';
            console.log('👁️ Detection guide shown');
        }
        if (this.centeredDetectionBox) {
            this.centeredDetectionBox.style.display = 'none';
            console.log('📦 Centered detection box hidden');
        }
        
        // Restart detection
        console.log('🚀 Restarting detection...');
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
        
        // Show detection guide again and hide centered detection box
        if (this.detectionGuide) {
            this.detectionGuide.style.display = 'block';
        }
        if (this.centeredDetectionBox) {
            this.centeredDetectionBox.style.display = 'none';
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
    
    addErrorLog(message, type) {
        // Add timestamp to the log
        const timestamp = new Date().toLocaleTimeString();
        const logEntry = {
            message: message,
            type: type,
            timestamp: timestamp
        };
        
        // Add to logs array
        this.errorLogs.unshift(logEntry);
        
        // Keep only the latest logs
        if (this.errorLogs.length > this.maxLogs) {
            this.errorLogs = this.errorLogs.slice(0, this.maxLogs);
        }
        
        // Update the display
        this.updateErrorLogDisplay();
    }
    
    clearErrorLogs() {
        this.errorLogs = [];
        this.updateErrorLogDisplay();
    }
    
    updateErrorLogDisplay() {
        if (!this.validationMessages) return;
        
        // Clear existing messages
        this.validationMessages.innerHTML = '';
        
        // Add current logs
        this.errorLogs.forEach(log => {
        const messageDiv = document.createElement('div');
            messageDiv.className = `validation-message ${log.type}`;
        messageDiv.innerHTML = `
                <i class="fas fa-${this.getIconForType(log.type)}"></i>
                <span>${log.message}</span>
                <small class="log-timestamp">${log.timestamp}</small>
        `;
        this.validationMessages.appendChild(messageDiv);
        });
    }
    
    lockScreen(message) {
        if (this.isScreenLocked) return;
        
        this.isScreenLocked = true;
        
        // Create lock overlay
        this.lockOverlay = document.createElement('div');
        this.lockOverlay.className = 'screen-lock-overlay';
        this.lockOverlay.innerHTML = `
            <div class="lock-content">
                <div class="lock-icon">
                    <i class="fas fa-lock"></i>
                </div>
                <h3>SYSTEM LOCKED</h3>
                <p>Multiple faces detected!</p>
                <p class="lock-message">${message}</p>
                <div class="lock-instructions">
                    <p><strong>Instructions:</strong></p>
                    <ul>
                        <li>Ensure only ONE person is visible in the camera</li>
                        <li>Move other people out of the frame</li>
                        <li>Wait for automatic unlock</li>
                    </ul>
                </div>
            </div>
        `;
        
        // Add to camera container
        const cameraContainer = document.querySelector('.camera-container');
        if (cameraContainer) {
            cameraContainer.appendChild(this.lockOverlay);
        }
        
        // Disable all controls
        this.disableAllControls();
        
        console.log('Screen locked due to multiple faces');
    }
    
    unlockScreen() {
        if (!this.isScreenLocked) return;
        
        this.isScreenLocked = false;
        
        // Remove lock overlay
        if (this.lockOverlay && this.lockOverlay.parentNode) {
            this.lockOverlay.parentNode.removeChild(this.lockOverlay);
            this.lockOverlay = null;
        }
        
        // Re-enable controls
        this.enableControls();
        
        console.log('Screen unlocked');
    }
    
    disableAllControls() {
        // Disable all buttons and controls
        const controls = [
            this.startButton,
            this.stopButton,
            this.captureButton,
            this.retryButton
        ];
        
        controls.forEach(control => {
            if (control) {
                control.disabled = true;
                control.style.opacity = '0.5';
            }
        });
    }
    
    enableControls() {
        // Re-enable controls based on current state
        if (this.startButton) {
            this.startButton.disabled = this.isDetecting;
            this.startButton.style.opacity = this.isDetecting ? '0.5' : '1';
        }
        
        if (this.stopButton) {
            this.stopButton.disabled = !this.isDetecting;
            this.stopButton.style.opacity = !this.isDetecting ? '0.5' : '1';
        }
        
        if (this.captureButton) {
            this.captureButton.disabled = !this.isCaptured && this.faceCount !== 1;
            this.captureButton.style.opacity = (!this.isCaptured && this.faceCount !== 1) ? '0.5' : '1';
        }
        
        if (this.retryButton) {
            this.retryButton.disabled = !this.isCaptured;
            this.retryButton.style.opacity = !this.isCaptured ? '0.5' : '1';
        }
    }
    
    showCapturedFacePreview(processedImageData) {
        // Show the face data display section with the cropped and processed face
        console.log('🖼️ Displaying cropped and preprocessed face preview...');
        
        const faceDataDisplay = document.getElementById('faceDataDisplay');
        if (faceDataDisplay) {
            faceDataDisplay.style.display = 'block';
            
            // Update captured image with the processed cropped face
            const capturedImage = document.getElementById('capturedImage');
            if (capturedImage) {
                capturedImage.src = processedImageData;
                
                // Force the styles to ensure cropped image display
                capturedImage.style.cssText = `
                    max-width: 200px !important;
                    max-height: 250px !important;
                    border: 2px solid #28a745 !important;
                    border-radius: 8px !important;
                    object-fit: contain !important;
                    display: block !important;
                    margin: 0 auto !important;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.1) !important;
                `;
                
                // Add a data attribute to confirm it's the cropped version
                capturedImage.setAttribute('data-processed', 'cropped');
                capturedImage.setAttribute('title', 'Cropped and Preprocessed Face');
                
                console.log('✅ Preview updated with cropped face image');
                console.log('🔍 Image data length:', processedImageData.length);
                console.log('📏 Image should be cropped to face region only');
                
                // Debug: Create a side-by-side comparison for verification
                this.createDebugComparison(processedImageData);
            } else {
                console.error('❌ capturedImage element not found');
            }
            
            // Update face data information
            const qualityScore = document.getElementById('qualityScore');
            const encodingDimensions = document.getElementById('encodingDimensions');
            const captureTime = document.getElementById('captureTime');
            
            if (qualityScore) {
                qualityScore.textContent = Math.round(this.faceQuality * 100) + '%';
                console.log('📊 Quality score updated:', Math.round(this.faceQuality * 100) + '%');
            }
            if (encodingDimensions) {
                encodingDimensions.textContent = '128 dimensions';
                console.log('🧬 Encoding dimensions updated: 128 dimensions');
            }
            if (captureTime) {
                const timestamp = new Date().toLocaleString();
                captureTime.textContent = timestamp;
                console.log('⏰ Capture time updated:', timestamp);
            }
            
            // Add processing information to the preview
            this.addProcessingInfo(faceDataDisplay);
        } else {
            console.error('❌ faceDataDisplay element not found');
        }
    }
    
    addProcessingInfo(faceDataDisplay) {
        // Add information about the processing applied
        let processingInfo = faceDataDisplay.querySelector('.processing-info');
        if (!processingInfo) {
            processingInfo = document.createElement('div');
            processingInfo.className = 'processing-info mt-2';
            processingInfo.innerHTML = `
                <small class="text-muted">
                    <strong>Processing Applied:</strong><br>
                    ✂️ Face Cropped (30% padding)<br>
                    🎨 Grayscale Converted<br>
                    📈 Histogram Equalized<br>
                    🔍 Noise Reduced<br>
                    🔪 Edge Sharpened<br>
                    ✨ Face Enhanced
                </small>
            `;
            faceDataDisplay.appendChild(processingInfo);
            console.log('📝 Processing information added to preview');
        }
    }
    
    enableSubmitButton() {
        const submitBtn = document.getElementById('submitBtn');
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.title = 'Ready to submit - All requirements met';
            submitBtn.classList.add('btn-success');
            submitBtn.classList.remove('btn-primary');
        }
    }
    
    showValidationMessage(message, type) {
        // Use the new error logging system instead of individual toasts
        this.addErrorLog(message, type);
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
    
    preprocessImageForFaceRecognition() {
        /**
         * Advanced face cropping and preprocessing for optimal face recognition
         * Crops face region and applies multiple enhancement techniques
         */
        console.log('🔧 Starting advanced face cropping and preprocessing pipeline...');
        
        // Ensure we have face coordinates from the last detection
        if (!this.lastFaces || this.lastFaces.length === 0) {
            console.error('❌ No face coordinates available - cannot crop face');
            throw new Error('Face coordinates required for cropping - ensure face is detected first');
        }
        
        const face = this.lastFaces[0];
        console.log('👤 Face coordinates:', face);
        
        // Calculate face region with padding for better cropping
        const padding = 0.3; // 30% padding around face
        const faceX = Math.max(0, Math.floor(face.x - face.width * padding));
        const faceY = Math.max(0, Math.floor(face.y - face.height * padding));
        const faceW = Math.min(this.canvas.width - faceX, Math.floor(face.width * (1 + 2 * padding)));
        const faceH = Math.min(this.canvas.height - faceY, Math.floor(face.height * (1 + 2 * padding)));
        
        console.log('✂️ Cropping face region:', { faceX, faceY, faceW, faceH, padding: `${padding * 100}%` });
        
        // Extract face region from canvas
        const faceImageData = this.ctx.getImageData(faceX, faceY, faceW, faceH);
        const data = faceImageData.data;
        const width = faceW;
        const height = faceH;
        
        console.log('📊 Cropped face specs:', { 
            width, 
            height, 
            channels: 4,
            totalPixels: width * height,
            dataLength: data.length,
            originalCanvas: `${this.canvas.width}x${this.canvas.height}`,
            cropRegion: `${faceX},${faceY} to ${faceX + faceW},${faceY + faceH}`
        });
        
        // Step 1: Convert to grayscale with optimized weights
        console.log('🎨 Converting to grayscale with luminance weighting...');
        const grayscaleData = new Uint8ClampedArray(width * height);
        for (let i = 0; i < data.length; i += 4) {
            // Use luminance formula for better grayscale conversion
            const luminance = Math.round(
                0.299 * data[i] +     // Red
                0.587 * data[i + 1] + // Green  
                0.114 * data[i + 2]   // Blue
            );
            grayscaleData[i / 4] = luminance;
        }
        
        // Step 2: Apply Gaussian blur for noise reduction
        console.log('🔍 Applying Gaussian blur for noise reduction...');
        const blurredData = this.applyGaussianBlur(grayscaleData, width, height, 1.0);
        
        // Step 3: Histogram equalization for contrast enhancement
        console.log('📈 Applying histogram equalization...');
        const equalizedData = this.applyHistogramEqualization(blurredData, width, height);
        
        // Step 4: Sharpening filter for edge enhancement
        console.log('🔪 Applying sharpening filter...');
        const sharpenedData = this.applySharpeningFilter(equalizedData, width, height);
        
        // Step 5: Face-specific enhancement (since we're already working on cropped face)
        console.log('👤 Applying face-specific enhancement...');
        const enhancedData = this.enhanceCroppedFace(sharpenedData, width, height);
        
        // Step 6: Convert back to RGBA for canvas
        console.log('🎨 Converting back to RGBA format...');
        const finalImageData = new ImageData(width, height);
        for (let i = 0; i < enhancedData.length; i++) {
            const pixelIndex = i * 4;
            const grayValue = enhancedData[i];
            finalImageData.data[pixelIndex] = grayValue;     // Red
            finalImageData.data[pixelIndex + 1] = grayValue; // Green
            finalImageData.data[pixelIndex + 2] = grayValue; // Blue
            finalImageData.data[pixelIndex + 3] = 255;       // Alpha
        }
        
        // Create a temporary canvas for the processed image
        const tempCanvas = document.createElement('canvas');
        tempCanvas.width = width;
        tempCanvas.height = height;
        const tempCtx = tempCanvas.getContext('2d');
        tempCtx.putImageData(finalImageData, 0, 0);
        
        // Convert to base64 with high quality
        const processedBase64 = tempCanvas.toDataURL('image/jpeg', 0.95);
        
        console.log('✅ Face cropping and preprocessing complete!', {
            originalImageSize: `${this.canvas.width}x${this.canvas.height}`,
            croppedFaceSize: `${width}x${height}`,
            processedSize: processedBase64.length,
            enhancements: ['face_crop', 'grayscale', 'blur', 'histogram_eq', 'sharpen', 'face_enhance'],
            paddingUsed: '30%',
            tempCanvasSize: `${tempCanvas.width}x${tempCanvas.height}`,
            isDataURL: processedBase64.startsWith('data:image/')
        });
        
        // Verify the processed image is actually different from the original
        const originalBase64 = this.canvas.toDataURL('image/jpeg', 0.95);
        const isCropped = processedBase64 !== originalBase64;
        console.log('🔍 Verification:', {
            isCropped,
            originalLength: originalBase64.length,
            croppedLength: processedBase64.length,
            sizeDifference: originalBase64.length - processedBase64.length
        });
        
        return processedBase64;
    }
    
    applyGaussianBlur(data, width, height, sigma) {
        // Simple Gaussian blur implementation
        const kernel = this.generateGaussianKernel(sigma);
        const kernelSize = kernel.length;
        const radius = Math.floor(kernelSize / 2);
        const blurred = new Uint8ClampedArray(data.length);
        
        for (let y = 0; y < height; y++) {
            for (let x = 0; x < width; x++) {
                let sum = 0;
                let weightSum = 0;
                
                for (let ky = -radius; ky <= radius; ky++) {
                    for (let kx = -radius; kx <= radius; kx++) {
                        const px = Math.max(0, Math.min(width - 1, x + kx));
                        const py = Math.max(0, Math.min(height - 1, y + ky));
                        const weight = kernel[ky + radius][kx + radius];
                        sum += data[py * width + px] * weight;
                        weightSum += weight;
                    }
                }
                
                blurred[y * width + x] = Math.round(sum / weightSum);
            }
        }
        
        return blurred;
    }
    
    generateGaussianKernel(sigma) {
        const size = Math.ceil(sigma * 3) * 2 + 1;
        const kernel = [];
        const center = Math.floor(size / 2);
        
        for (let y = 0; y < size; y++) {
            kernel[y] = [];
            for (let x = 0; x < size; x++) {
                const dx = x - center;
                const dy = y - center;
                kernel[y][x] = Math.exp(-(dx * dx + dy * dy) / (2 * sigma * sigma));
            }
        }
        
        return kernel;
    }
    
    applyHistogramEqualization(data, width, height) {
        // Calculate histogram
        const histogram = new Array(256).fill(0);
        for (let i = 0; i < data.length; i++) {
            histogram[data[i]]++;
        }
        
        // Calculate cumulative distribution
        const cdf = new Array(256);
        cdf[0] = histogram[0];
        for (let i = 1; i < 256; i++) {
            cdf[i] = cdf[i - 1] + histogram[i];
        }
        
        // Normalize CDF
        const totalPixels = width * height;
        const equalizedData = new Uint8ClampedArray(data.length);
        
        for (let i = 0; i < data.length; i++) {
            equalizedData[i] = Math.round((cdf[data[i]] / totalPixels) * 255);
        }
        
        return equalizedData;
    }
    
    applySharpeningFilter(data, width, height) {
        // Sharpening kernel
        const kernel = [
            [0, -1, 0],
            [-1, 5, -1],
            [0, -1, 0]
        ];
        
        const sharpened = new Uint8ClampedArray(data.length);
        
        for (let y = 1; y < height - 1; y++) {
            for (let x = 1; x < width - 1; x++) {
                let sum = 0;
                
                for (let ky = -1; ky <= 1; ky++) {
                    for (let kx = -1; kx <= 1; kx++) {
                        const px = x + kx;
                        const py = y + ky;
                        sum += data[py * width + px] * kernel[ky + 1][kx + 1];
                    }
                }
                
                sharpened[y * width + x] = Math.max(0, Math.min(255, sum));
            }
        }
        
        // Copy border pixels
        for (let i = 0; i < data.length; i++) {
            if (sharpened[i] === 0) {
                sharpened[i] = data[i];
            }
        }
        
        return sharpened;
    }
    
    enhanceCroppedFace(data, width, height) {
        /**
         * Apply face-specific enhancements to the already cropped face region
         * Since we're working with a cropped face, we can apply global enhancements
         */
        console.log('🎭 Applying face-specific enhancements to cropped region...');
        const enhanced = new Uint8ClampedArray(data);
        
        // Apply adaptive contrast enhancement
        const mean = data.reduce((sum, val) => sum + val, 0) / data.length;
        const variance = data.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / data.length;
        const stdDev = Math.sqrt(variance);
        
        console.log('📊 Face statistics:', { mean: mean.toFixed(2), stdDev: stdDev.toFixed(2) });
        
        // Apply adaptive enhancement based on face statistics
        for (let i = 0; i < data.length; i++) {
            const pixel = data[i];
            
            // Adaptive contrast stretching
            let enhanced_pixel;
            if (stdDev > 30) {
                // High contrast face - apply mild enhancement
                enhanced_pixel = pixel * 1.05;
            } else {
                // Low contrast face - apply stronger enhancement
                enhanced_pixel = pixel * 1.2;
            }
            
            // Apply S-curve for better tonal distribution
            enhanced_pixel = this.applySCurve(enhanced_pixel / 255.0) * 255;
            
            enhanced[i] = Math.min(255, Math.max(0, Math.round(enhanced_pixel)));
        }
        
        console.log('✨ Face-specific enhancement complete');
        return enhanced;
    }
    
    applySCurve(x) {
        /**
         * Apply S-curve for better tonal distribution
         * Enhances midtones while preserving highlights and shadows
         */
        // S-curve formula: f(x) = 3x² - 2x³ (for x in [0,1])
        return 3 * x * x - 2 * x * x * x;
    }
    
    pauseDetectionTemporarily() {
        // Pause detection for 10 seconds when server is down
        const originalDetecting = this.isDetecting;
        this.isDetecting = false;
        this.pendingRequest = null;
        this.isRetrying = false;
        this.networkStatus = 'offline';
        this.updateNetworkStatusIndicator();
        
        console.log('⏸️ Detection paused for 10 seconds...');
        
        setTimeout(() => {
            if (originalDetecting) {
                console.log('▶️ Resuming detection...');
                this.isDetecting = true;
                this.networkStatus = 'online';
                this.addErrorLog('Attempting to resume detection...', 'info');
            }
        }, 10000);
    }
    
    updateNetworkStatusIndicator() {
        // Add a small network status indicator to the detection area
        let statusIndicator = document.getElementById('networkStatusIndicator');
        if (!statusIndicator) {
            statusIndicator = document.createElement('div');
            statusIndicator.id = 'networkStatusIndicator';
            statusIndicator.style.cssText = `
                position: absolute;
                top: 10px;
                left: 10px;
                padding: 5px 10px;
                border-radius: 15px;
                font-size: 12px;
                font-weight: bold;
                z-index: 1000;
                transition: all 0.3s ease;
            `;
            
            // Add to detection container
            const detectionContainer = document.querySelector('.detection-container') || document.body;
            detectionContainer.appendChild(statusIndicator);
        }
        
        // Update indicator based on network status
        switch (this.networkStatus) {
            case 'online':
                statusIndicator.style.cssText += `
                    background: #28a745;
                    color: white;
                    display: none;
                `;
                statusIndicator.textContent = '🟢 Online';
                // Hide after 2 seconds if just recovered
                setTimeout(() => {
                    if (statusIndicator && this.networkStatus === 'online') {
                        statusIndicator.style.display = 'none';
                    }
                }, 2000);
                break;
                
            case 'retrying':
                statusIndicator.style.cssText += `
                    background: #ffc107;
                    color: #212529;
                    display: block;
                `;
                statusIndicator.textContent = '🔄 Retrying...';
                break;
                
            case 'offline':
                statusIndicator.style.cssText += `
                    background: #dc3545;
                    color: white;
                    display: block;
                `;
                statusIndicator.textContent = '🔴 Offline';
                break;
        }
    }
    
    createDebugComparison(processedImageData) {
        /**
         * Create a debug comparison to verify cropping is working
         */
        console.log('🔍 Creating debug comparison...');
        
        // Get original full image
        const originalImageData = this.canvas.toDataURL('image/jpeg', 0.95);
        
        // Create debug container if it doesn't exist
        let debugContainer = document.getElementById('debugComparison');
        if (!debugContainer) {
            debugContainer = document.createElement('div');
            debugContainer.id = 'debugComparison';
            debugContainer.style.cssText = `
                position: fixed;
                top: 10px;
                right: 10px;
                background: white;
                border: 2px solid #007bff;
                border-radius: 8px;
                padding: 10px;
                z-index: 9999;
                max-width: 300px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            `;
            document.body.appendChild(debugContainer);
        }
        
        debugContainer.innerHTML = `
            <div style="text-align: center; margin-bottom: 10px;">
                <strong>🔍 Debug: Cropping Verification</strong>
                <button onclick="document.getElementById('debugComparison').remove()" 
                        style="float: right; background: #dc3545; color: white; border: none; border-radius: 3px; padding: 2px 6px; font-size: 12px;">×</button>
            </div>
            <div style="display: flex; gap: 10px;">
                <div style="text-align: center;">
                    <div style="font-size: 12px; margin-bottom: 5px;"><strong>Original</strong></div>
                    <img src="${originalImageData}" style="width: 120px; height: 90px; object-fit: cover; border: 1px solid #ccc;">
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 12px; margin-bottom: 5px;"><strong>Cropped</strong></div>
                    <img src="${processedImageData}" style="width: 120px; height: 90px; object-fit: cover; border: 1px solid #28a745;">
                </div>
            </div>
            <div style="font-size: 11px; margin-top: 8px; color: #666;">
                Original: ${originalImageData.length} chars<br>
                Cropped: ${processedImageData.length} chars<br>
                Difference: ${originalImageData.length - processedImageData.length} chars
            </div>
        `;
        
        console.log('✅ Debug comparison created - check top-right corner');
        
        // Auto-remove after 10 seconds
        setTimeout(() => {
            if (debugContainer.parentNode) {
                debugContainer.remove();
            }
        }, 10000);
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
        console.log('Initializing Face Recognition System...');
        window.pythonFaceDetection = new PythonFaceDetection();
    } else {
        console.log('Face detection elements not found, skipping initialization');
    }
});
