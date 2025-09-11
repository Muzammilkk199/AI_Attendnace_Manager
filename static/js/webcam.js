// webcam functionality for attendance
class WebcamManager {
    constructor() {
        this.video = null;
        this.canvas = null;
        this.stream = null;
        this.isStreaming = false;
        
        this.init();
    }
    
    init() {
        this.video = document.getElementById('webcam');
        this.canvas = document.getElementById('canvas');
        
        if (!this.video || !this.canvas) {
            return;
        }
        
        this.setupEventListeners();
    }
    
    setupEventListeners() {
        const startBtn = document.getElementById('startWebcam');
        const stopBtn = document.getElementById('stopWebcam');
        const captureBtn = document.getElementById('capturePhoto');
        
        if (startBtn) {
            startBtn.addEventListener('click', () => this.startWebcam());
        }
        
        if (stopBtn) {
            stopBtn.addEventListener('click', () => this.stopWebcam());
        }
        
        if (captureBtn) {
            captureBtn.addEventListener('click', () => this.captureAttendance());
        }
    }
    
    async startWebcam() {
        try {
            this.stream = await navigator.mediaDevices.getUserMedia({
                video: true,
                audio: false
            });
            
            this.video.srcObject = this.stream;
            this.isStreaming = true;
            
            this.video.addEventListener('loadedmetadata', () => {
                this.video.play();
                this.updateButtonStates(true);
            });
            
        } catch (error) {
            console.error('Error accessing webcam:', error);
            alert('Error accessing camera');
        }
    }
    
    stopWebcam() {
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = null;
        }
        
        this.video.srcObject = null;
        this.isStreaming = false;
        this.updateButtonStates(false);
    }
    
    updateButtonStates(isStreaming) {
        const startBtn = document.getElementById('startWebcam');
        const stopBtn = document.getElementById('stopWebcam');
        const captureBtn = document.getElementById('capturePhoto');
        
        if (startBtn) startBtn.disabled = isStreaming;
        if (stopBtn) stopBtn.disabled = !isStreaming;
        if (captureBtn) captureBtn.disabled = !isStreaming;
    }
    
    async captureAttendance() {
        if (!this.isStreaming) {
            alert('Please start the camera first');
            return;
        }
        
        const studentIdInput = document.getElementById('studentId');
        if (!studentIdInput || !studentIdInput.value.trim()) {
            alert('Please enter Student ID');
            return;
        }
        
        const imageData = this.captureImage();
        await this.processAttendance(studentIdInput.value.trim(), imageData);
    }
    
    captureImage() {
        const context = this.canvas.getContext('2d');
        this.canvas.width = this.video.videoWidth;
        this.canvas.height = this.video.videoHeight;
        
        context.drawImage(this.video, 0, 0);
        return this.canvas.toDataURL('image/jpeg', 0.8);
    }
                
    async processAttendance(studentId, imageData) {
        try {
            const formData = new FormData();
            formData.append('student_id', studentId);
            formData.append('image_data', imageData);
            formData.append('csrfmiddlewaretoken', this.getCSRFToken());
            
            const response = await fetch('/api/attendance/mark/', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (result.success) {
                alert('Attendance marked successfully!');
                this.updateRecentAttendance(result.attendance);
                this.clearForm();
            } else {
                alert(result.message || 'Failed to mark attendance');
            }
            
        } catch (error) {
            console.error('Error processing attendance:', error);
            alert('Network error. Please try again.');
        }
    }
    
    updateRecentAttendance(attendance) {
        const recentDiv = document.getElementById('recentAttendance');
        if (!recentDiv) return;
        
        const attendanceItem = document.createElement('div');
        attendanceItem.className = 'mb-2 p-2 border rounded';
        attendanceItem.innerHTML = `
            <div>
                <strong>${attendance.student_id}</strong> - ${attendance.status}
                <br><small>${new Date(attendance.timestamp).toLocaleTimeString()}</small>
            </div>
        `;
        
        recentDiv.insertBefore(attendanceItem, recentDiv.firstChild);
        
        const items = recentDiv.querySelectorAll('.mb-2');
        if (items.length > 5) {
            recentDiv.removeChild(items[items.length - 1]);
        }
    }
    
    clearForm() {
        const studentIdInput = document.getElementById('studentId');
        if (studentIdInput) studentIdInput.value = '';
    }
    
    getCSRFToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    }
}

// initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    window.webcamManager = new WebcamManager();
});
