# AI Attendance Manager - ER Diagram Generators

This directory contains multiple tools to generate visual Entity Relationship (ER) diagrams for the AI Attendance Manager project.

## 📁 Generated Files

The following files have been created for you:

### 🎨 Visual Diagrams
- **`ai_attendance_er_diagram.html`** - Interactive HTML ER diagram with modern styling
- **`ai_attendance_er_diagram.txt`** - Text-based ER diagram for console viewing
- **`Graphical_ER_Diagram.md`** - Mermaid-based ER diagram for GitHub/GitLab

### 🛠️ Generator Scripts
- **`simple_er_diagram_generator.py`** - Python script using matplotlib (requires matplotlib)
- **`text_er_diagram_generator.py`** - Text-based generator (no dependencies)
- **`html_er_diagram_generator.py`** - HTML generator (no dependencies)
- **`generate_er_diagram.py`** - Full Django-integrated generator

### 📋 Documentation
- **`AI_Attendance_Manager_ER_Diagram.md`** - Comprehensive ER diagram documentation
- **`ER_DIAGRAM_README.md`** - This file

## 🚀 How to Use

### 1. HTML ER Diagram (Recommended)
```bash
python html_er_diagram_generator.py
```
- **Output**: `ai_attendance_er_diagram.html`
- **Features**: Interactive, modern styling, responsive design
- **Dependencies**: None (uses only built-in Python)

### 2. Text ER Diagram
```bash
python text_er_diagram_generator.py
```
- **Output**: `ai_attendance_er_diagram.txt`
- **Features**: Console-friendly, ASCII art
- **Dependencies**: None (uses only built-in Python)

### 3. Graphical ER Diagram (Matplotlib)
```bash
# Install dependencies first
pip install matplotlib numpy

# Run the generator
python simple_er_diagram_generator.py
```
- **Output**: `ai_attendance_er_diagram.png`, `.pdf`, `.svg`
- **Features**: High-quality graphics, multiple formats
- **Dependencies**: matplotlib, numpy

### 4. Full Django Integration
```bash
python generate_er_diagram.py
```
- **Output**: `ai_attendance_er_diagram.png`, `.pdf`
- **Features**: Reads actual Django models, full integration
- **Dependencies**: Django, matplotlib, numpy

## 📊 Database Architecture Overview

### Hybrid Database System
The AI Attendance Manager uses a **hybrid database architecture**:

#### SQLite Database (Django ORM)
- **Purpose**: Relational data storage and business logic
- **Models**: Student, Attendance, User
- **Features**: ACID compliance, data integrity, Django ORM

#### MongoDB Database (Face Recognition)
- **Purpose**: Face embeddings and high-performance queries
- **Collections**: students, attendance
- **Features**: Document storage, similarity search, face recognition

### Entity Relationships

```
Student (1) ──→ (M) Attendance
User (1) ──→ (M) Student
Student ──sync──> MongoDB_Students
Attendance ──sync──> MongoDB_Attendance
```

## 🎯 Key Features Visualized

### 🔐 Security Features
- **Ultra-Strict Face Recognition**: 92.98% similarity threshold
- **Proxy Attack Prevention**: Rejects unregistered faces
- **Confidence Levels**: VERY_HIGH, HIGH, LOW_CONFIDENCE

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

## 🎨 Diagram Types

### 1. HTML ER Diagram
- **Best for**: Presentations, documentation, web viewing
- **Features**: 
  - Modern, responsive design
  - Interactive hover effects
  - Color-coded entities
  - Mobile-friendly
  - Professional styling

### 2. Text ER Diagram
- **Best for**: Console viewing, quick reference
- **Features**:
  - ASCII art representation
  - No dependencies
  - Fast generation
  - Terminal-friendly

### 3. Graphical ER Diagram
- **Best for**: High-quality graphics, printing
- **Features**:
  - Vector graphics (PDF, SVG)
  - High resolution (PNG)
  - Professional appearance
  - Multiple export formats

### 4. Mermaid ER Diagram
- **Best for**: GitHub, GitLab, documentation
- **Features**:
  - Renders in markdown
  - Version control friendly
  - Multiple diagram types
  - Interactive elements

## 🔧 Customization

### Modifying Entity Colors
Edit the color schemes in the generator scripts:

```python
self.colors = {
    'django_model': '#E3F2FD',      # Light blue
    'mongodb_collection': '#F3E5F5', # Light purple
    'primary_key': '#4CAF50',        # Green
    'foreign_key': '#FF9800',        # Orange
    'unique_key': '#2196F3',         # Blue
}
```

### Adding New Entities
1. Define the entity fields
2. Add entity position in the layout
3. Update relationships
4. Regenerate the diagram

### Changing Layout
Modify the `positions` dictionary in the generator scripts:

```python
self.positions = {
    'Student': (2, 7.5),
    'Attendance': (2, 5),
    'User': (2, 2.5),
    'MongoDB_Students': (8, 7.5),
    'MongoDB_Attendance': (8, 5),
}
```

## 📱 Viewing the Diagrams

### HTML Diagram
1. Open `ai_attendance_er_diagram.html` in any web browser
2. Use browser zoom for different sizes
3. Print directly from browser if needed

### Text Diagram
1. Open `ai_attendance_er_diagram.txt` in any text editor
2. Use monospace font for best appearance
3. Copy to console for quick viewing

### Graphical Diagram
1. Open generated image files in image viewer
2. Use PDF viewer for vector graphics
3. Import into documents or presentations

## 🐛 Troubleshooting

### Matplotlib Installation Issues
```bash
# Try different installation methods
pip install matplotlib --user
python -m pip install matplotlib
conda install matplotlib
```

### Django Integration Issues
```bash
# Ensure Django is properly configured
python manage.py check
python manage.py migrate
```

### Permission Issues
```bash
# Run with appropriate permissions
python html_er_diagram_generator.py
```

## 📈 Performance Tips

1. **Use HTML generator** for quick, dependency-free generation
2. **Use text generator** for console viewing
3. **Use graphical generator** for high-quality output
4. **Use Django generator** for model integration

## 🔄 Updating Diagrams

When you modify your Django models:

1. **Automatic**: Run the Django-integrated generator
2. **Manual**: Update field definitions in generator scripts
3. **Hybrid**: Use Django generator for models, manual for MongoDB

## 📚 Additional Resources

- [Django Model Documentation](https://docs.djangoproject.com/en/stable/topics/db/models/)
- [MongoDB Documentation](https://docs.mongodb.com/)
- [Matplotlib Documentation](https://matplotlib.org/stable/contents.html)
- [Mermaid Documentation](https://mermaid-js.github.io/mermaid/)

## 🎉 Success!

You now have multiple ways to visualize your AI Attendance Manager's database structure:

- ✅ **HTML ER Diagram** - Interactive and modern
- ✅ **Text ER Diagram** - Console-friendly
- ✅ **Graphical ER Diagram** - High-quality graphics
- ✅ **Mermaid ER Diagram** - Documentation-ready

Choose the format that best suits your needs!
