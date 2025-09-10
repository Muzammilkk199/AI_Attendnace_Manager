/**
 * Advanced Face Detection Module
 * Uses OpenCV.js for real face detection and recognition
 */

class AdvancedFaceDetection {
    constructor() {
        this.video = null;
        this.canvas = null;
        this.faceCascade = null;
        this.isInitialized = false;
        this.isDetecting = false;
        this.faceDetected = false;
        this.faceLocation = null;
        this.callbacks = {
            onFaceDetected: null,
            onFaceLost: null,
            onStatusUpdate: null
        };
    }

    async initialize() {
        try {
            // Load OpenCV.js
            await this.loadOpenCV();
            
            // Initialize face cascade
            this.faceCascade = new cv.CascadeClassifier();
            this.faceCascade.load('haarcascade_frontalface_default.xml');
            
            this.isInitialized = true;
            this.updateStatus('Face detection initialized successfully', 'success');
            return true;
        } catch (error) {
            console.error('Failed to initialize face detection:', error);
            this.updateStatus('Failed to initialize face detection', 'error');
            return false;
        }
    }

    async loadOpenCV() {
        return new Promise((resolve, reject) => {
            if (window.cv) {
                resolve();
                return;
            }

            const script = document.createElement('script');
            script.src = 'https://docs.opencv.org/4.8.0/opencv.js';
            script.onload = () => {
                cv.onRuntimeInitialized = () => {
                    resolve();
                };
            };
            script.onerror = () => {
                reject(new Error('Failed to load OpenCV.js'));
            };
            document.head.appendChild(script);
        });
    }

    async startDetection(videoElement, canvasElement) {
        if (!this.isInitialized) {
            const initialized = await this.initialize();
            if (!initialized) return false;
        }

        this.video = videoElement;
        this.canvas = canvasElement;
        this.isDetecting = true;

        this.detectFaces();
        return true;
    }

    detectFaces() {
        if (!this.isDetecting || !this.video || !this.canvas) return;

        try {
            const context = this.canvas.getContext('2d');
            this.canvas.width = this.video.videoWidth;
            this.canvas.height = this.video.videoHeight;
            context.drawImage(this.video, 0, 0);

            // Convert to OpenCV Mat
            const src = cv.imread(this.canvas);
            const gray = new cv.Mat();
            cv.cvtColor(src, gray, cv.COLOR_RGBA2GRAY, 0);

            // Detect faces
            const faces = new cv.RectVector();
            const msize = new cv.Size(0, 0);
            this.faceCascade.detectMultiScale(gray, faces, 1.1, 3, 0, msize, msize);

            // Process detected faces
            if (faces.size() > 0) {
                const face = faces.get(0);
                this.handleFaceDetected(face);
            } else {
                this.handleFaceLost();
            }

            // Clean up
            src.delete();
            gray.delete();
            faces.delete();

        } catch (error) {
            console.error('Error in face detection:', error);
        }

        // Continue detection
        requestAnimationFrame(() => this.detectFaces());
    }

    handleFaceDetected(face) {
        if (!this.faceDetected) {
            this.faceDetected = true;
            this.faceLocation = {
                x: face.x,
                y: face.y,
                width: face.width,
                height: face.height
            };

            if (this.callbacks.onFaceDetected) {
                this.callbacks.onFaceDetected(this.faceLocation);
            }

            this.updateStatus('Face detected! Ready to capture.', 'success');
        }
    }

    handleFaceLost() {
        if (this.faceDetected) {
            this.faceDetected = false;
            this.faceLocation = null;

            if (this.callbacks.onFaceLost) {
                this.callbacks.onFaceLost();
            }

            this.updateStatus('Position your face in the center', 'warning');
        }
    }

    captureFace() {
        if (!this.faceDetected || !this.faceLocation) {
            this.updateStatus('No face detected. Please position your face properly.', 'error');
            return null;
        }

        try {
            const context = this.canvas.getContext('2d');
            this.canvas.width = this.video.videoWidth;
            this.canvas.height = this.video.videoHeight;
            context.drawImage(this.video, 0, 0);

            // Extract face region
            const faceCanvas = document.createElement('canvas');
            const faceContext = faceCanvas.getContext('2d');
            const { x, y, width, height } = this.faceLocation;

            faceCanvas.width = width;
            faceCanvas.height = height;
            faceContext.drawImage(
                this.canvas,
                x, y, width, height,
                0, 0, width, height
            );

            // Convert to grayscale as per SRS requirement
            const imageData = faceContext.getImageData(0, 0, width, height);
            const data = imageData.data;

            for (let i = 0; i < data.length; i += 4) {
                const gray = data[i] * 0.299 + data[i + 1] * 0.587 + data[i + 2] * 0.114;
                data[i] = gray;     // Red
                data[i + 1] = gray; // Green
                data[i + 2] = gray; // Blue
                // Alpha channel remains unchanged
            }

            faceContext.putImageData(imageData, 0, 0);

            // Convert to base64
            const faceImageData = faceCanvas.toDataURL('image/jpeg', 0.8);

            this.updateStatus('Face captured successfully!', 'success');
            return {
                image: faceImageData,
                location: this.faceLocation,
                timestamp: new Date().toISOString()
            };

        } catch (error) {
            console.error('Error capturing face:', error);
            this.updateStatus('Error capturing face. Please try again.', 'error');
            return null;
        }
    }

    stopDetection() {
        this.isDetecting = false;
        this.faceDetected = false;
        this.faceLocation = null;
        this.updateStatus('Face detection stopped', 'info');
    }

    setCallback(event, callback) {
        this.callbacks[event] = callback;
    }

    updateStatus(message, type) {
        if (this.callbacks.onStatusUpdate) {
            this.callbacks.onStatusUpdate(message, type);
        }
    }

    // Generate mock face encoding for testing
    generateFaceEncoding() {
        const encoding = [];
        for (let i = 0; i < 128; i++) {
            encoding.push(Math.random() * 2 - 1);
        }
        return encoding;
    }
}

// Export for use in other modules
window.AdvancedFaceDetection = AdvancedFaceDetection;
