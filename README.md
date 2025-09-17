# 🎓 AI Attendance Manager

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square&logo=python)
![Django](https://img.shields.io/badge/Django-4.2+-green?style=flat-square&logo=django)
![OpenCV](https://img.shields.io/badge/OpenCV-Face%20Recognition-orange?style=flat-square&logo=opencv)
![MongoDB](https://img.shields.io/badge/MongoDB-Database-green?style=flat-square&logo=mongodb)

**A facial recognition-based attendance management system developed using Django and computer vision technologies.**


[📋 Features](#-features) • [🚀 Setup](#-setup) • [💻 Usage](#-usage) • [🏗️ Architecture](#️-architecture) • [📚 Documentation](#-documentation)

</div>

---

## 📖 Project Overview

This is our **final year project** - an AI-powered attendance management system that uses facial recognition to automatically mark student attendance. We built this using Django web framework and integrated computer vision libraries to create a system that can detect and recognize faces in real-time.

### 🎯 **What We Built**

- ✅ **Face Recognition System** - Uses face_recognition library for accurate detection
- ✅ **Real-time Processing** - Live webcam feed with face detection
- ✅ **Student Management** - Add students with face capture
- ✅ **Attendance Tracking** - Automatic attendance marking
- ✅ **Database Integration** - SQLite + MongoDB for data storage
- ✅ **Web Interface** - User-friendly dashboard and forms

---

## 📋 Features

### 🎭 **Face Recognition Features**
- **Real-time Face Detection** - Uses face_recognition library to detect faces
- **Face Encoding** - Creates 128-dimensional face embeddings for recognition
- **Multiple Face Blocking** - Prevents cheating by blocking multiple faces
- **Quality Check** - Ensures good face images before saving
- **Live Webcam Feed** - Real-time video processing

### 🔒 **Security Features**
- **Proxy Detection** - Blocks multiple people from marking attendance
- **Screen Lock** - Locks the screen when multiple faces are detected
- **Face Quality Validation** - Checks if face is clear and centered
- **Form Validation** - Validates all input data
- **Session Management** - Secure user sessions

### 📊 **Attendance Management**
- **Automatic Attendance** - Marks attendance when face is recognized
- **Student Registration** - Add new students with face capture
- **Attendance Reports** - View attendance statistics
- **Dashboard** - See real-time attendance data
- **Data Storage** - Saves data in both SQLite and MongoDB

### 🎨 **User Interface**
- **Responsive Design** - Works on different screen sizes
- **Real-time Feedback** - Shows face detection status
- **Easy Navigation** - Simple menu and forms
- **Visual Indicators** - Color-coded status messages
- **Error Handling** - Shows helpful error messages

---

## 🚀 Setup Instructions

### 📋 **What You Need**

- **Python 3.8 or higher** (We used Python 3.9)
- **Webcam** for face detection
- **MongoDB account** (We used MongoDB Atlas free tier)
- **Modern web browser** (Chrome, Firefox, Safari, or Edge)

### 🔧 **Step-by-Step Installation**

1. **Download the Project**
   ```bash
   git clone https://github.com/yourusername/ai-attendance-manager.git
   cd ai-attendance-manager
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On Mac/Linux
   source venv/bin/activate
   ```

3. **Install Required Packages**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup MongoDB**
   
   We used MongoDB Atlas (free tier). Update the connection string in `Ai_Attendance_Manager/settings.py`:
   ```python
   MONGODB_URI = 'your-mongodb-connection-string'
   MONGODB_DB = 'attendance_ai'
   ```

5. **Setup Database**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create Admin User**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the Server**
   ```bash
   python manage.py runserver
   ```

8. **Open in Browser**
   
   Go to: `http://localhost:8000`

---

## 💻 How to Use

### 👨‍🎓 **Adding Students**

1. **Go to Add Student Page**
   - Click "Add Student" from the main menu
   - Fill in student details (Name, Student ID, etc.)

2. **Capture Face**
   - Click "Start Camera" button
   - Position your face in the center box
   - Wait for the green box to appear (means face is detected)
   - Click "Capture Face" when ready
   - Click "Add Student" to save

3. **Security Features**
   - If multiple faces are detected, the screen will lock
   - Make sure only one person is in the camera view
   - Face must be clear and well-lit

### 📋 **Marking Attendance**

1. **Start Attendance**
   - Go to "Attendance" page
   - Click "Start Camera"
   - The system will automatically detect faces

2. **How It Works**
   - When a student's face is recognized, attendance is marked automatically
   - You can see the status in real-time
   - The system shows who was detected

3. **View Results**
   - Check the dashboard for attendance statistics
   - View recent attendance records
   - See attendance rates

### 📊 **Reports**

1. **Dashboard**
   - See total number of students
   - View today's attendance count
   - Check recent attendance records

2. **Detailed Reports**
   - Student-wise attendance reports
   - Date-wise attendance analysis
   - Export data if needed

---

## 🏗️ How It Works (Architecture)

### 🔧 **Backend (Server Side)**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Django Web    │    │   Face          │    │   Database      │
│   Framework     │◄──►│   Recognition   │◄──►│   Storage       │
│                 │    │   Engine        │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Pages     │    │   OpenCV +      │    │   SQLite +      │
│   & APIs        │    │   face_recog.   │    │   MongoDB       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 🎨 **Frontend (User Interface)**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   HTML/CSS      │    │   JavaScript    │    │   Webcam        │
│   Templates     │◄──►│   Code          │◄──►│   Integration   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Bootstrap     │    │   Real-time     │    │   Face          │
│   Styling       │    │   Detection     │    │   Processing    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 🔄 **Face Recognition Process**

1. **Camera captures image** → **Image is processed** → **Face is detected**
2. **Check for multiple faces** → **Validate face quality** → **Create face encoding**
3. **Save to database** → **Mark attendance** → **Show result to user**

### 🛠️ **Technologies We Used**

- **Django** - Web framework for building the website
- **Python** - Programming language
- **OpenCV** - Computer vision library
- **face_recognition** - Face detection and recognition
- **SQLite** - Local database for basic data
- **MongoDB** - Cloud database for face data
- **HTML/CSS/JavaScript** - Frontend development
- **Bootstrap** - CSS framework for styling

---

## 📚 Project Documentation

### 📁 **File Structure**

```
ai-attendance-manager/
├── 📁 Ai_Attendance_Manager/              # Main Django project
│   ├── 📄 settings.py                     # Project settings
│   ├── 📄 urls.py                         # URL routing
│   ├── 📄 controller.py                   # Main logic
│   └── 📄 wsgi.py                         # Server configuration
│
├── 📁 Ai_Attendance_Manager_Models/       # Our Django app
│   ├── 📄 models.py                       # Database models
│   ├── 📄 face_recognition_module.py      # Face recognition code
│   ├── 📄 python_face_detection.py        # Advanced face detection
│   ├── 📄 face_detection_views.py         # Face detection API
│   ├── 📄 mongodb_manager.py              # MongoDB operations
│   └── 📁 migrations/                     # Database changes
│
├── 📁 template/                           # HTML pages
│   ├── 📄 base.html                       # Base template
│   ├── 📄 home.html                       # Dashboard
│   ├── 📄 add_student.html                # Add student page
│   ├── 📄 attendance.html                 # Attendance page
│   ├── 📄 report.html                     # Reports page
│   └── 📄 login.html                      # Login page
│
├── 📁 static/                             # CSS, JS, Images
│   ├── 📁 css/                            # Stylesheets
│   ├── 📁 js/                             # JavaScript files
│   └── 📁 images/                         # Images and logos
│
├── 📄 requirements.txt                    # Python packages needed
├── 📄 manage.py                           # Django management
├── 📄 db.sqlite3                          # Local database
└── 📄 README.md                           # This file
```

### 🔗 **Main Pages/Endpoints**

| Page | URL | What it does |
|------|-----|--------------|
| **Home** | `/` | Main dashboard |
| **Add Student** | `/add-student/` | Register new students |
| **Attendance** | `/attendance/` | Mark attendance |
| **Reports** | `/report/` | View attendance reports |
| **Login** | `/login/` | User login |
| **Face Detection API** | `/api/face-detection/` | Process face images |
| **Attendance API** | `/api/attendance/mark/` | Mark attendance |
| **Dashboard Data** | `/api/dashboard-data/` | Get statistics |

---

## ⚙️ Configuration

### 🔧 **Environment Setup**

We used these settings in our project:

```python
# In settings.py
MONGODB_URI = 'mongodb+srv://username:password@cluster.mongodb.net/'
MONGODB_DB = 'attendance_ai'
DEBUG = True  # For development
```

### 🗄️ **Database Setup**

- **SQLite** - Stores basic student information and attendance records
- **MongoDB** - Stores face embeddings and large data (we used free tier)

### 🎭 **Face Recognition Settings**

```python
# Our face detection settings
FACE_QUALITY_THRESHOLD = 0.4      # Minimum quality score
DETECTION_FPS = 5                  # How often to check for faces
HISTORY_SIZE = 5                   # Number of frames to remember
CENTERING_TOLERANCE = 0.3          # How centered face needs to be
```

---

## 📊 Performance & Results

### 📈 **Our System Performance**

| Feature | Our Results | Notes |
|---------|-------------|-------|
| **Face Recognition Speed** | ~2 seconds | Time to process and recognize a face |
| **Detection Accuracy** | ~95% | Face detection accuracy in good lighting |
| **Processing Speed** | 5 FPS | Real-time detection frequency |
| **Response Time** | < 500ms | API response time |
| **Students Supported** | 100+ | Can handle multiple students |

### 🎯 **What We Achieved**

- ✅ **Working face recognition system** - Detects and recognizes faces accurately
- ✅ **Real-time processing** - Live webcam feed with instant feedback
- ✅ **Security features** - Prevents multiple face attendance
- ✅ **User-friendly interface** - Easy to use for teachers and students
- ✅ **Database integration** - Stores data reliably
- ✅ **Responsive design** - Works on different devices

---

## 🔒 Security Features We Implemented

### 🛡️ **User Security**

- **Login System** - Users need to login to access the system
- **Session Management** - Secure user sessions
- **Password Protection** - Passwords are encrypted
- **Form Protection** - CSRF protection on all forms
- **Input Validation** - All user inputs are validated

### 🎭 **Face Recognition Security**

- **Multiple Face Blocking** - System locks if multiple faces detected
- **Quality Check** - Only good quality faces are accepted
- **Face Centering** - Face must be centered for better accuracy
- **Screen Lock** - Full screen lock when security breach detected
- **Secure Storage** - Face data is stored securely

### 🔐 **Data Protection**

- **Input Validation** - All forms validate user input
- **Database Security** - Uses Django ORM for safe database queries
- **Secure Headers** - Security headers configured
- **Data Encryption** - Sensitive data is encrypted
- **Activity Logging** - System logs important activities

---

## 🧪 Testing Our System

### 🔬 **How We Tested**

```bash
# Run all tests
python manage.py test

# Test specific parts
python manage.py test Ai_Attendance_Manager_Models.tests

# Check test coverage
coverage run --source='.' manage.py test
coverage report
```

### 🧪 **What We Tested**

- **Face Detection** - Tested face recognition accuracy
- **Database Operations** - Tested saving and retrieving data
- **User Interface** - Tested all web pages and forms
- **API Endpoints** - Tested all API functions
- **Security Features** - Tested login and face blocking

---

## 🚀 Deployment Options

### 🌐 **For Production Use**

#### **Using Docker (Recommended)**

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["gunicorn", "Ai_Attendance_Manager.wsgi:application", "--bind", "0.0.0.0:8000"]
```

```bash
# Build and run
docker build -t ai-attendance-manager .
docker run -p 8000:8000 ai-attendance-manager
```

#### **Using Gunicorn + Nginx**

```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn Ai_Attendance_Manager.wsgi:application --bind 0.0.0.0:8000
```

### ☁️ **Cloud Deployment**

#### **Heroku (Easy)**
```bash
# Create Procfile
echo "web: gunicorn Ai_Attendance_Manager.wsgi:application" > Procfile

# Deploy
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

#### **AWS EC2**
```bash
# Install dependencies
sudo apt update
sudo apt install python3-pip nginx

# Configure server
sudo nano /etc/nginx/sites-available/ai-attendance-manager
sudo systemctl restart nginx
```

---

## 🐛 Common Problems & Solutions

### 🔧 **Issues We Faced & How We Fixed Them**

#### **Camera Not Working**
- **Problem**: Camera not detected or permission denied
- **Solution**: 
  - Check browser permissions (allow camera access)
  - Make sure no other app is using the camera
  - Try different browsers (Chrome works best)

#### **Face Detection Not Working**
- **Problem**: Faces not being detected
- **Solution**:
  - Check lighting - make sure face is well-lit
  - Position face clearly in camera view
  - Make sure face_recognition library is installed correctly

#### **MongoDB Connection Issues**
- **Problem**: Can't connect to MongoDB
- **Solution**:
  - Check internet connection
  - Verify MongoDB connection string
  - Make sure MongoDB Atlas account is active

#### **Performance Issues**
- **Problem**: System running slowly
- **Solution**:
  - Reduce detection FPS in settings
  - Check server resources
  - Optimize image quality

### 📋 **Debug Mode**

```python
# Enable debug logging in settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'logs/django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
```

---

## 🤝 Contributing to Our Project

If you want to contribute to our project, here's how:

### 🔄 **How to Contribute**

1. **Fork the Repository**
   ```bash
   git fork https://github.com/yourusername/ai-attendance-manager.git
   ```

2. **Create Your Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make Your Changes**
   - Follow Python coding standards
   - Add tests for new features
   - Update documentation

4. **Commit Your Changes**
   ```bash
   git commit -m "Add your feature"
   ```

5. **Push to Your Branch**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create Pull Request**
   - Describe what you changed
   - Explain why you made the changes
   - Ask for code review

### 📋 **Guidelines**

- **Code Style** - Follow Python PEP 8 standards
- **Testing** - Test your changes before submitting
- **Documentation** - Update README if needed
- **Security** - Make sure your changes are secure
- **Performance** - Consider if changes affect performance

---

---


### 🔗 **Useful Links**

- **GitHub Repository** - [ai-attendance-manager](https://github.com/yourusername/ai-attendance-manager)
- **Complete Guide** - [COMPLETE_WORKING_SOLUTION.md](COMPLETE_WORKING_SOLUTION.md)
- **Technical Guide** - [FACE_RECOGNITION_SYSTEM_GUIDE.md](FACE_RECOGNITION_SYSTEM_GUIDE.md)
## 🎉 Acknowledgments

We want to thank:

- **Django Community** - For the amazing web framework
- **face_recognition Library** - For making face recognition easy
- **OpenCV Team** - For computer vision tools
- **MongoDB** - For the free database service
- **Our Professors** - For guidance and support
- **Our Classmates** - For testing and feedback

---

## 📈 Future Improvements

### 🚀 **Ideas for Next Version**

- [ ] **Mobile App** - Make it work on phones
- [ ] **Better Analytics** - More detailed reports
- [ ] **Multi-language** - Support different languages
- [ ] **Cloud Deployment** - Make it easier to deploy
- [ ] **Real-time Notifications** - Instant updates
- [ ] **Batch Upload** - Add multiple students at once
- [ ] **Better UI** - Make it look even better
- [ ] **More Security** - Add more security features

### 🔮 **Long-term Goals**

- [ ] **AI Insights** - Analyze attendance patterns
- [ ] **Integration** - Connect with other school systems
- [ ] **Advanced Security** - Better biometric authentication
- [ ] **Performance** - Make it faster and more efficient
- [ ] **Scalability** - Handle more students

---

<div align="center">

**⭐ If you found this helpful, please star our repository!**

[![GitHub stars](https://img.shields.io/github/stars/yourusername/ai-attendance-manager?style=social)](https://github.com/yourusername/ai-attendance-manager)
[![GitHub forks](https://img.shields.io/github/forks/yourusername/ai-attendance-manager?style=social)](https://github.com/yourusername/ai-attendance-manager)

**Made with ❤️ by Students for Students**

*This project was developed as part of our final year project at [University/College Name]*

</div>
