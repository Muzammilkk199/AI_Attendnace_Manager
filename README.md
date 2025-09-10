# AI Attendance Manager

A comprehensive facial recognition-based attendance management system built with Django and OpenCV.

## Features

### Core Functionality
- **Real-time Face Detection**: Uses OpenCV and face_recognition libraries for accurate face detection
- **Student Registration**: Complete student management with face capture and embedding storage
- **Automated Attendance**: Mark attendance automatically using facial recognition
- **Dual Database Storage**: SQLite for relational data, MongoDB for face embeddings and large data
- **Grayscale Image Processing**: Images are converted to grayscale as per SRS requirements
- **Proxy Detection**: Prevents duplicate attendance and proxy marking

### Technical Features
- **Face Embedding Generation**: 128-dimensional face encodings for accurate recognition
- **Real-time Webcam Integration**: Live face detection with visual feedback
- **Responsive UI**: Modern, mobile-friendly interface
- **Data Validation**: Comprehensive form validation and error handling
- **Security**: CSRF protection and secure data handling

## Installation

### Prerequisites
- Python 3.8+
- Webcam/Camera access
- MongoDB (for face embeddings)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Ai_Attendance_Manager
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure MongoDB**
   - Update MongoDB connection string in `Ai_Attendance_Manager/settings.py`
   - Ensure MongoDB is running and accessible

4. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Open browser and navigate to `http://localhost:8000`
   - Login with your superuser credentials

## Usage

### Adding Students
1. Navigate to "Add Student" from the dashboard
2. Fill in student information (First Name, Last Name, Student ID are required)
3. Click "Start Camera" to begin face detection
4. Position the student's face in the center circle
5. Click "Capture Face" when face is detected
6. Review the captured face and click "Add Student"

### Marking Attendance
1. Navigate to "Attendance" from the dashboard
2. Click "Start Camera" to begin live attendance
3. Students' faces will be automatically detected and recognized
4. Attendance is marked automatically based on face recognition
5. View real-time attendance status and recent records

### Viewing Reports
1. Navigate to "Report" from the dashboard
2. View attendance statistics and student records
3. Export data as needed

## Technical Architecture

### Backend
- **Django 4.2+**: Web framework
- **SQLite**: Primary database for relational data
- **MongoDB**: NoSQL database for face embeddings and large data
- **OpenCV**: Computer vision and image processing
- **face_recognition**: Face detection and recognition

### Frontend
- **HTML5/CSS3**: Modern responsive design
- **JavaScript**: Interactive face detection and webcam integration
- **OpenCV.js**: Client-side face detection (optional)
- **Bootstrap**: UI framework

### Face Recognition Pipeline
1. **Image Capture**: Webcam captures real-time video
2. **Face Detection**: OpenCV detects faces in video frames
3. **Preprocessing**: Images are converted to grayscale and resized
4. **Feature Extraction**: 128-dimensional face encodings are generated
5. **Matching**: Face encodings are compared with stored embeddings
6. **Attendance Marking**: Matched faces are automatically marked present

## File Structure

```
Ai_Attendance_Manager/
├── Ai_Attendance_Manager/          # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── controller.py
├── Ai_Attendance_Manager_Models/   # Django app
│   ├── models.py                   # Database models
│   ├── face_recognition_module.py  # Face recognition logic
│   └── mongodb_manager.py          # MongoDB operations
├── template/                       # HTML templates
│   ├── base.html
│   ├── add_student.html
│   ├── attendance.html
│   └── report.html
├── static/                         # Static files
│   ├── css/
│   ├── js/
│   │   ├── webcam.js
│   │   └── face-detection.js
│   └── images/
├── requirements.txt
└── README.md
```

## API Endpoints

### Student Management
- `POST /add-student/` - Add new student with face data
- `GET /add-student/` - Student registration form

### Attendance
- `POST /api/attendance/mark/` - Mark attendance
- `GET /attendance/` - Attendance interface
- `POST /api/attendance/data/` - Get attendance data

### Reports
- `GET /report/` - Attendance reports
- `POST /api/dashboard-data/` - Dashboard statistics

## Configuration

### Environment Variables
Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key
DEBUG=True
MONGODB_URI=mongodb://localhost:27017/attendance_ai
MONGODB_DB=attendance_ai
```

### MongoDB Setup
1. Install MongoDB
2. Create database: `attendance_ai`
3. Update connection string in settings.py

## Performance Requirements

- **Face Recognition Speed**: < 2 seconds per face
- **Accuracy**: > 95% recognition accuracy
- **Scalability**: Support up to 1000 students
- **Uptime**: 99% availability during working hours

## Security Features

- CSRF protection on all forms
- Secure face data storage
- Input validation and sanitization
- Session management
- Password reset functionality

## Browser Compatibility

- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

## Troubleshooting

### Common Issues

1. **Camera not working**
   - Check browser permissions
   - Ensure HTTPS in production
   - Try different browsers

2. **Face detection not working**
   - Ensure good lighting
   - Check camera positioning
   - Verify OpenCV installation

3. **MongoDB connection issues**
   - Check MongoDB service status
   - Verify connection string
   - Check network connectivity

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions, please contact the development team or create an issue in the repository.

## Changelog

### Version 1.0.0
- Initial release
- Basic face recognition functionality
- Student registration with face capture
- Automated attendance marking
- MongoDB integration
- Responsive UI design
