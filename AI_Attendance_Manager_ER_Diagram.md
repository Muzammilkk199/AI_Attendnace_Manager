# AI Attendance Manager - Entity Relationship Diagram

## Database Architecture Overview

This AI Attendance Manager uses a **hybrid database architecture**:
- **SQLite** (Django ORM) for relational data and business logic
- **MongoDB** for face embeddings and high-performance face recognition

## Entity Relationship Diagram

```mermaid
erDiagram
    %% Django Models (SQLite Database)
    Student {
        int id PK "Auto-increment primary key"
        string student_id UK "Unique student identifier"
        string name "Full name of student"
        string first_name "First name"
        string last_name "Last name"
        string email "Email address"
        string phone "Phone number"
        string class_name "Class/grade"
        string section "Section/division"
        datetime created_at "Record creation timestamp"
        boolean is_active "Active status flag"
    }

    Attendance {
        int id PK "Auto-increment primary key"
        int student_id FK "Foreign key to Student"
        date date "Attendance date"
        string status "present/late/absent/checkout/day_finished"
        datetime timestamp "Attendance timestamp"
        float confidence "Face recognition confidence score"
        text notes "Additional notes"
    }

    %% Django Built-in Models
    User {
        int id PK "Auto-increment primary key"
        string username UK "Unique username"
        string email "Email address"
        string first_name "First name"
        string last_name "Last name"
        boolean is_staff "Staff status"
        boolean is_active "Active status"
        datetime date_joined "Account creation date"
    }

    %% MongoDB Collections
    MongoDB_Students {
        objectid _id PK "MongoDB ObjectId"
        string student_id UK "Student identifier (sync with Django)"
        string name "Student name"
        string first_name "First name"
        string last_name "Last name"
        string email "Email address"
        string phone "Phone number"
        string class_name "Class/grade"
        string section "Section/division"
        array embedding "Face recognition embedding vector"
        boolean is_active "Active status"
        int django_id "Reference to Django Student.id"
        datetime created_at "Record creation timestamp"
        datetime updated_at "Last update timestamp"
    }

    MongoDB_Attendance {
        objectid _id PK "MongoDB ObjectId"
        string student_id "Student identifier"
        string student_name "Student name (denormalized)"
        string date "Attendance date"
        string status "Attendance status"
        float confidence "Recognition confidence"
        text notes "Additional notes"
        string image_data "Base64 encoded attendance image"
        datetime timestamp "Attendance timestamp"
        int django_id "Reference to Django Attendance.id"
        datetime created_at "Record creation timestamp"
        datetime updated_at "Last update timestamp"
    }

    %% Relationships
    Student ||--o{ Attendance : "has many"
    User ||--o{ Student : "manages (admin)"
    
    %% MongoDB Sync Relationships (dotted lines for data synchronization)
    Student -.-> MongoDB_Students : "syncs to"
    Attendance -.-> MongoDB_Attendance : "syncs to"
```

## Model Details

### 1. Student Model (Django/SQLite)
**Primary Entity** - Stores core student information
- **Primary Key**: `id` (auto-increment integer)
- **Unique Key**: `student_id` (string, 50 chars max)
- **Key Features**:
  - Automatic name generation from first_name + last_name
  - MongoDB synchronization on save
  - Face embedding storage in MongoDB
  - Ultra-strict face recognition (92.98% threshold)

### 2. Attendance Model (Django/SQLite)
**Transaction Entity** - Records daily attendance
- **Primary Key**: `id` (auto-increment integer)
- **Foreign Key**: `student_id` → Student.id
- **Status Options**: present, late, absent, checkout, day_finished
- **Key Features**:
  - Time-based status determination
  - Automatic attendance marking
  - Duplicate prevention
  - MongoDB synchronization

### 3. User Model (Django Built-in)
**Authentication Entity** - System administrators
- **Primary Key**: `id` (auto-increment integer)
- **Unique Key**: `username`
- **Purpose**: Admin access to the system

### 4. MongoDB Collections

#### MongoDB_Students Collection
**Face Recognition Storage** - Stores face embeddings and student data
- **Primary Key**: `_id` (MongoDB ObjectId)
- **Unique Key**: `student_id`
- **Key Features**:
  - Face embedding vectors for recognition
  - Cosine similarity search
  - Ultra-strict matching (92.98% threshold)
  - Django ID reference for synchronization

#### MongoDB_Attendance Collection
**Attendance Analytics** - Stores attendance data for reporting
- **Primary Key**: `_id` (MongoDB ObjectId)
- **Key Features**:
  - Image data storage (Base64)
  - Attendance statistics
  - Date range queries
  - Django ID reference for synchronization

## Database Relationships

### Primary Relationships
1. **Student → Attendance** (One-to-Many)
   - One student can have multiple attendance records
   - Each attendance record belongs to one student
   - Cascade delete: If student is deleted, all attendance records are deleted

2. **User → Student** (One-to-Many, Admin)
   - Admin users can manage multiple students
   - Students are managed by admin users

### Synchronization Relationships
3. **Student ↔ MongoDB_Students** (Bidirectional Sync)
   - Django Student model syncs to MongoDB on save
   - Face embeddings stored in MongoDB
   - Django ID maintained for reference

4. **Attendance ↔ MongoDB_Attendance** (Bidirectional Sync)
   - Django Attendance model syncs to MongoDB on save
   - Image data stored in MongoDB
   - Django ID maintained for reference

## Key Features

### Face Recognition System
- **Ultra-Strict Threshold**: 92.98% similarity required
- **Proxy Prevention**: Rejects unregistered faces
- **Confidence Levels**: VERY_HIGH, HIGH, LOW_CONFIDENCE
- **Embedding Storage**: 128-dimensional face vectors

### Attendance Logic
- **Time-Based Status**:
  - Before 8:00 AM: Present
  - 8:00 AM - 2:00 PM: Late
  - After 2:00 PM: Day Finished
- **Duplicate Prevention**: One attendance per student per day
- **Status Updates**: Can update from absent to present/late/checkout

### Data Synchronization
- **Dual Storage**: SQLite for relational data, MongoDB for embeddings
- **Automatic Sync**: Models automatically sync to MongoDB on save
- **Reference Integrity**: Django IDs maintained in MongoDB for consistency

## Database Configuration

### SQLite (Primary Database)
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

### MongoDB (Face Recognition Database)
```python
MONGODB_URI = 'mongodb+srv://...'
MONGODB_DB = 'attendance_ai'
```

## Security Features

1. **Face Recognition Security**:
   - Ultra-strict similarity threshold (92.98%)
   - Proxy attack prevention
   - Unregistered face rejection

2. **Data Security**:
   - XSS protection enabled
   - CSRF protection
   - Secure session management
   - Content type sniffing prevention

3. **Access Control**:
   - Django authentication system
   - Admin-only access to student management
   - Session-based authentication

## Performance Optimizations

1. **MongoDB Indexing**:
   - Student ID indexes for fast lookups
   - Embedding indexes for similarity search

2. **Caching Strategy**:
   - Face embeddings cached in MongoDB
   - Attendance statistics cached

3. **Query Optimization**:
   - Efficient similarity search algorithms
   - Date range queries for attendance reports

This hybrid architecture provides the benefits of both relational (SQLite) and document (MongoDB) databases, ensuring data integrity while enabling high-performance face recognition capabilities.
