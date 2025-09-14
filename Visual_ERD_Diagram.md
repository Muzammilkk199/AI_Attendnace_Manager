# AI Attendance Manager - Visual ERD Diagram

## Interactive Database Schema

```mermaid
graph TB
    %% Define the main entities
    subgraph "Django SQLite Database"
        User[👤 User<br/>Django Built-in]
        Student[🎓 Student<br/>Core Entity]
        Attendance[📊 Attendance<br/>Daily Records]
    end
    
    subgraph "MongoDB Collections"
        MongoStudents[📚 MongoDB Students<br/>Face Embeddings]
        MongoAttendance[📈 MongoDB Attendance<br/>Extended Data]
    end
    
    subgraph "Face Recognition System"
        FaceEmbedding[🧠 Face Embedding<br/>128-dimensional array]
        FaceRecognition[👁️ Face Recognition<br/>AI Processing]
    end
    
    subgraph "Attendance Status Flow"
        Present[✅ Present<br/>≤ 8:00 AM]
        Late[⚠️ Late<br/>8:00 AM - 2:00 PM]
        DayFinished[🚫 Day Finished<br/>> 2:00 PM]
        Absent[❌ Absent<br/>Not Scanned]
        Checkout[🚪 Checkout<br/>End of Day]
    end
    
    %% Relationships
    User -->|manages| Student
    Student -->|has many| Attendance
    Student -.->|syncs to| MongoStudents
    Attendance -.->|syncs to| MongoAttendance
    
    %% Face recognition connections
    Student -->|stores| FaceEmbedding
    FaceEmbedding -->|processed by| FaceRecognition
    FaceRecognition -->|creates| Attendance
    
    %% Status flow
    Attendance --> Present
    Attendance --> Late
    Attendance --> DayFinished
    Attendance --> Absent
    Attendance --> Checkout
    
    %% Styling
    classDef djangoEntity fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef mongoEntity fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef aiEntity fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    classDef statusEntity fill:#fff3e0,stroke:#e65100,stroke-width:2px
    
    class User,Student,Attendance djangoEntity
    class MongoStudents,MongoAttendance mongoEntity
    class FaceEmbedding,FaceRecognition aiEntity
    class Present,Late,DayFinished,Absent,Checkout statusEntity
```

## Detailed Entity Relationship Diagram

```mermaid
erDiagram
    %% Django User Model (Built-in)
    User {
        int id PK "Primary Key"
        string username UK "Unique Username"
        string email "Email Address"
        string first_name "First Name"
        string last_name "Last Name"
        boolean is_staff "Admin Access"
        boolean is_active "Account Status"
        datetime date_joined "Registration Date"
    }
    
    %% Core Student Model
    Student {
        int id PK "Primary Key"
        string student_id UK "Unique Student ID"
        string name "Full Name"
        string first_name "First Name"
        string last_name "Last Name"
        string email "Email Address"
        string phone "Phone Number"
        string class_name "Class Name"
        string section "Section"
        datetime created_at "Creation Date"
        boolean is_active "Active Status"
    }
    
    %% Attendance Records
    Attendance {
        int id PK "Primary Key"
        int student_id FK "Student Reference"
        date date "Attendance Date"
        string status "Attendance Status"
        datetime timestamp "Record Time"
        float confidence "Recognition Confidence"
        text notes "Additional Notes"
    }
    
    %% MongoDB Students Collection
    MongoDB_Students {
        objectid _id PK "MongoDB ID"
        string student_id "Student ID"
        string name "Full Name"
        string first_name "First Name"
        string last_name "Last Name"
        string email "Email Address"
        string phone "Phone Number"
        string class_name "Class Name"
        string section "Section"
        array embedding "Face Embedding (128D)"
        boolean is_active "Active Status"
        int django_id FK "Django Reference"
        datetime created_at "Creation Date"
    }
    
    %% MongoDB Attendance Collection
    MongoDB_Attendance {
        objectid _id PK "MongoDB ID"
        string student_id "Student ID"
        string student_name "Student Name"
        string date "Attendance Date"
        string status "Attendance Status"
        float confidence "Recognition Confidence"
        text notes "Additional Notes"
        datetime timestamp "Record Time"
        int django_id FK "Django Reference"
        string image_data "Base64 Image Data"
    }
    
    %% Attendance Status Enum
    Attendance_Status {
        string present "On Time (≤8:00 AM)"
        string late "Late (8:00 AM - 2:00 PM)"
        string absent "Not Present"
        string checkout "End of Day"
        string day_finished "After Hours (>2:00 PM)"
    }
    
    %% Relationships
    User ||--o{ Student : "manages"
    Student ||--o{ Attendance : "has_attendance"
    Student ||--|| MongoDB_Students : "syncs_to"
    Attendance ||--|| MongoDB_Attendance : "syncs_to"
    Attendance ||--|| Attendance_Status : "has_status"
```

## System Architecture Flow

```mermaid
flowchart TD
    A[👤 Student Approaches Camera] --> B[📷 Face Detection]
    B --> C{🎯 Face Detected?}
    C -->|No| D[❌ No Face Found]
    C -->|Yes| E[🧠 Extract Face Embedding]
    E --> F[🔍 Compare with Database]
    F --> G{👤 Student Recognized?}
    G -->|No| H[🚫 Unregistered Face]
    G -->|Yes| I[⏰ Check Current Time]
    I --> J{🕐 Time Check}
    J -->|≤ 8:00 AM| K[✅ Mark as Present]
    J -->|8:00 AM - 2:00 PM| L[⚠️ Mark as Late]
    J -->|> 2:00 PM| M[🚫 Day Finished]
    K --> N[💾 Save to Database]
    L --> N
    M --> O[🚫 Block Attendance]
    N --> P[📊 Update Dashboard]
    O --> Q[📝 Log Error Message]
    
    %% Styling
    classDef process fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef decision fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef success fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef error fill:#ffebee,stroke:#d32f2f,stroke-width:2px
    classDef database fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    
    class A,B,E,F,I,N,P process
    class C,G,J decision
    class K,L success
    class D,H,M,O,Q error
    class N database
```

## Database Schema Summary

### **Core Tables (SQLite)**
- **User**: Django authentication system
- **Student**: Student information and face data references
- **Attendance**: Daily attendance records with timestamps

### **MongoDB Collections**
- **Students**: Face embeddings and extended student data
- **Attendance**: Image data and additional attendance information

### **Key Features**
- 🔄 **Dual Database Sync**: Automatic synchronization between SQLite and MongoDB
- 🧠 **AI Integration**: 128-dimensional face embeddings for recognition
- ⏰ **Time-based Logic**: Automatic status assignment based on scan time
- 🛡️ **Security**: Proxy prevention and unregistered face detection
- 📊 **Real-time Updates**: Live dashboard with attendance statistics

### **API Endpoints**
- `/api/face-detection/` - Face detection processing
- `/api/recognize-student/` - Student recognition and attendance marking
- `/api/attendance/summary/` - Attendance statistics
- `/api/attendance/initialize/` - Daily attendance initialization

This visual ERD shows the complete database architecture, data flow, and system relationships in your AI Attendance Manager project.

