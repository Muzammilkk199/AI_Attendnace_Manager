# AI Attendance Manager - Mermaid ER Diagram

## Complete Entity Relationship Diagram

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

    %% Primary Relationships
    Student ||--o{ Attendance : "has many"
    User ||--o{ Student : "manages"
    
    %% MongoDB Sync Relationships (dotted lines for data synchronization)
    Student -.-> MongoDB_Students : "syncs to"
    Attendance -.-> MongoDB_Attendance : "syncs to"
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
