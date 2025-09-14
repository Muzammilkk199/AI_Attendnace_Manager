# AI Attendance Manager - Graphical ER Diagram

## Visual Entity Relationship Diagram

```mermaid
erDiagram
    %% Main Django Models
    Student {
        int id PK "Primary Key"
        string student_id UK "Unique Student ID"
        string name "Full Name"
        string first_name "First Name"
        string last_name "Last Name"
        string email "Email Address"
        string phone "Phone Number"
        string class_name "Class/Grade"
        string section "Section"
        datetime created_at "Created Date"
        boolean is_active "Active Status"
    }

    Attendance {
        int id PK "Primary Key"
        int student_id FK "Foreign Key to Student"
        date date "Attendance Date"
        string status "Status: present/late/absent/checkout/day_finished"
        datetime timestamp "Timestamp"
        float confidence "Recognition Confidence"
        text notes "Additional Notes"
    }

    User {
        int id PK "Primary Key"
        string username UK "Username"
        string email "Email"
        string first_name "First Name"
        string last_name "Last Name"
        boolean is_staff "Staff Status"
        boolean is_active "Active Status"
        datetime date_joined "Join Date"
    }

    %% MongoDB Collections
    MongoDB_Students {
        objectid _id PK "MongoDB ObjectId"
        string student_id UK "Student ID"
        string name "Student Name"
        string first_name "First Name"
        string last_name "Last Name"
        string email "Email"
        string phone "Phone"
        string class_name "Class"
        string section "Section"
        array embedding "Face Embedding Vector"
        boolean is_active "Active Status"
        int django_id "Django Student ID"
        datetime created_at "Created Date"
        datetime updated_at "Updated Date"
    }

    MongoDB_Attendance {
        objectid _id PK "MongoDB ObjectId"
        string student_id "Student ID"
        string student_name "Student Name"
        string date "Attendance Date"
        string status "Attendance Status"
        float confidence "Confidence Score"
        text notes "Notes"
        string image_data "Base64 Image Data"
        datetime timestamp "Timestamp"
        int django_id "Django Attendance ID"
        datetime created_at "Created Date"
        datetime updated_at "Updated Date"
    }

    %% Relationships
    Student ||--o{ Attendance : "has attendance records"
    User ||--o{ Student : "manages students"
    
    %% MongoDB Sync (dotted lines for data synchronization)
    Student -.-> MongoDB_Students : "syncs face data"
    Attendance -.-> MongoDB_Attendance : "syncs attendance data"
```

## Database Architecture Overview

```mermaid
graph TB
    subgraph "Django Application"
        A[Student Model] --> B[Attendance Model]
        C[User Model] --> A
    end
    
    subgraph "SQLite Database"
        D[(Student Table)]
        E[(Attendance Table)]
        F[(User Table)]
    end
    
    subgraph "MongoDB Database"
        G[(Students Collection)]
        H[(Attendance Collection)]
    end
    
    subgraph "Face Recognition System"
        I[Face Embeddings]
        J[Similarity Search]
        K[Ultra-Strict Matching]
    end
    
    A --> D
    B --> E
    C --> F
    
    A -.-> G
    B -.-> H
    
    G --> I
    I --> J
    J --> K
    
    style A fill:#e1f5fe
    style B fill:#e8f5e8
    style C fill:#fff3e0
    style G fill:#f3e5f5
    style H fill:#f3e5f5
    style I fill:#ffebee
    style J fill:#ffebee
    style K fill:#ffebee
```

## Data Flow Diagram

```mermaid
flowchart TD
    A[Student Registration] --> B[Face Capture]
    B --> C[Generate Embedding]
    C --> D[Store in MongoDB]
    D --> E[Sync to SQLite]
    
    F[Attendance Scan] --> G[Face Detection]
    G --> H[Generate Embedding]
    H --> I[Similarity Search]
    I --> J{Match Found?}
    J -->|Yes| K[Check Confidence]
    J -->|No| L[Reject - Unregistered Face]
    K --> M{Confidence >= 92.98%?}
    M -->|Yes| N[Mark Attendance]
    M -->|No| O[Reject - Low Confidence]
    N --> P[Update SQLite]
    P --> Q[Sync to MongoDB]
    
    style A fill:#e3f2fd
    style B fill:#e8f5e8
    style C fill:#fff3e0
    style D fill:#f3e5f5
    style E fill:#e1f5fe
    style F fill:#e3f2fd
    style G fill:#e8f5e8
    style H fill:#fff3e0
    style I fill:#f3e5f5
    style J fill:#ffecb3
    style K fill:#ffecb3
    style M fill:#ffecb3
    style N fill:#c8e6c9
    style L fill:#ffcdd2
    style O fill:#ffcdd2
    style P fill:#e1f5fe
    style Q fill:#f3e5f5
```

## System Architecture

```mermaid
graph LR
    subgraph "Frontend"
        A[Web Interface]
        B[Camera Component]
        C[Face Detection JS]
    end
    
    subgraph "Backend"
        D[Django Views]
        E[Face Recognition Module]
        F[MongoDB Manager]
    end
    
    subgraph "Databases"
        G[(SQLite)]
        H[(MongoDB)]
    end
    
    subgraph "External Services"
        I[Face Detection API]
        J[Embedding Generation]
    end
    
    A --> D
    B --> C
    C --> I
    D --> E
    E --> F
    F --> G
    F --> H
    E --> J
    
    style A fill:#e3f2fd
    style B fill:#e8f5e8
    style C fill:#fff3e0
    style D fill:#f3e5f5
    style E fill:#ffebee
    style F fill:#e1f5fe
    style G fill:#e8f5e8
    style H fill:#fff3e0
    style I fill:#f3e5f5
    style J fill:#ffebee
```

## Attendance Status Flow

```mermaid
stateDiagram-v2
    [*] --> CheckTime
    
    CheckTime --> Present : Before 8:00 AM
    CheckTime --> Late : 8:00 AM - 2:00 PM
    CheckTime --> DayFinished : After 2:00 PM
    
    Present --> Checkout : End of Day
    Late --> Checkout : End of Day
    
    Checkout --> [*]
    DayFinished --> [*]
    
    note right of Present
        Student arrives on time
        Face recognition successful
    end note
    
    note right of Late
        Student arrives late
        Face recognition successful
    end note
    
    note right of Checkout
        End of day checkout
        Can be manual or automatic
    end note
    
    note right of DayFinished
        No more attendance allowed
        Day is considered finished
    end note
```

## Face Recognition Process

```mermaid
sequenceDiagram
    participant U as User
    participant C as Camera
    participant F as Face Detection
    participant E as Embedding Generator
    participant M as MongoDB
    participant S as SQLite
    participant A as Attendance System
    
    U->>C: Start Camera
    C->>F: Capture Frame
    F->>E: Detect Face
    E->>M: Generate Embedding
    M->>M: Search Similar Faces
    M-->>E: Return Matches
    E->>E: Calculate Similarity
    alt Similarity >= 92.98%
        E->>A: Valid Match Found
        A->>S: Create Attendance Record
        A->>M: Sync to MongoDB
        A-->>U: Attendance Marked
    else Similarity < 92.98%
        E-->>U: Face Not Recognized
    end
```

## Key Features Summary

### 🔐 Security Features
- **Ultra-Strict Face Recognition**: 92.98% similarity threshold
- **Proxy Attack Prevention**: Rejects unregistered faces
- **Confidence Levels**: VERY_HIGH, HIGH, LOW_CONFIDENCE
- **Session Management**: Secure authentication

### 📊 Data Management
- **Hybrid Database**: SQLite + MongoDB
- **Automatic Synchronization**: Real-time data sync
- **Face Embeddings**: 128-dimensional vectors
- **Image Storage**: Base64 encoded attendance photos

### ⏰ Time-Based Logic
- **Present**: Before 8:00 AM
- **Late**: 8:00 AM - 2:00 PM  
- **Day Finished**: After 2:00 PM
- **Checkout**: End of day process

### 🎯 Performance Optimizations
- **MongoDB Indexing**: Fast similarity searches
- **Caching Strategy**: Optimized face recognition
- **Query Optimization**: Efficient data retrieval
