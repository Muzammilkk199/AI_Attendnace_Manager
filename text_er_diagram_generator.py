#!/usr/bin/env python3
"""
Text-based ER Diagram Generator for AI Attendance Manager
This script creates a visual text-based ER diagram without external dependencies
"""

import os
import sys

class TextERDiagramGenerator:
    def __init__(self):
        self.width = 120
        self.height = 40
        
    def create_box(self, title, fields, width=30, height=15):
        """Create a text box for an entity"""
        lines = []
        
        # Top border
        lines.append("┌" + "─" * (width - 2) + "┐")
        
        # Title
        title_line = f"│ {title:<{width-4}} │"
        lines.append(title_line)
        
        # Separator
        lines.append("├" + "─" * (width - 2) + "┤")
        
        # Fields
        for field in fields:
            field_line = f"│ {field:<{width-4}} │"
            lines.append(field_line)
        
        # Fill remaining space
        remaining_height = height - len(lines) - 1
        for _ in range(remaining_height):
            lines.append("│" + " " * (width - 2) + "│")
        
        # Bottom border
        lines.append("└" + "─" * (width - 2) + "┘")
        
        return lines
    
    def create_relationship_line(self, start_pos, end_pos, label=""):
        """Create a relationship line between entities"""
        lines = []
        
        # Simple horizontal line for now
        if start_pos[0] < end_pos[0]:  # Left to right
            line = " " * start_pos[0] + "─" * (end_pos[0] - start_pos[0])
            if label:
                line += f" {label}"
            lines.append(line)
        
        return lines
    
    def generate_diagram(self):
        """Generate the complete text-based ER diagram"""
        diagram = []
        
        # Title
        title = "AI ATTENDANCE MANAGER - ENTITY RELATIONSHIP DIAGRAM"
        diagram.append("=" * len(title))
        diagram.append(title)
        diagram.append("=" * len(title))
        diagram.append("")
        
        # Define entity fields
        student_fields = [
            "id: AutoField (PK)",
            "student_id: CharField (UK)",
            "name: CharField",
            "first_name: CharField",
            "last_name: CharField",
            "email: EmailField",
            "phone: CharField",
            "class_name: CharField",
            "section: CharField",
            "created_at: DateTimeField",
            "is_active: BooleanField"
        ]
        
        attendance_fields = [
            "id: AutoField (PK)",
            "student: ForeignKey (FK)",
            "date: DateField",
            "status: CharField",
            "timestamp: DateTimeField",
            "confidence: FloatField",
            "notes: TextField"
        ]
        
        user_fields = [
            "id: AutoField (PK)",
            "username: CharField (UK)",
            "email: EmailField",
            "first_name: CharField",
            "last_name: CharField",
            "is_staff: BooleanField",
            "is_active: BooleanField",
            "date_joined: DateTimeField"
        ]
        
        mongodb_student_fields = [
            "_id: ObjectId (PK)",
            "student_id: String (UK)",
            "name: String",
            "first_name: String",
            "last_name: String",
            "email: String",
            "phone: String",
            "class_name: String",
            "section: String",
            "embedding: Array",
            "is_active: Boolean",
            "django_id: Integer",
            "created_at: DateTime",
            "updated_at: DateTime"
        ]
        
        mongodb_attendance_fields = [
            "_id: ObjectId (PK)",
            "student_id: String",
            "student_name: String",
            "date: String",
            "status: String",
            "confidence: Float",
            "notes: Text",
            "image_data: String",
            "timestamp: DateTime",
            "django_id: Integer",
            "created_at: DateTime",
            "updated_at: DateTime"
        ]
        
        # Create entities
        student_box = self.create_box("STUDENT (Django Model)", student_fields)
        attendance_box = self.create_box("ATTENDANCE (Django Model)", attendance_fields)
        user_box = self.create_box("USER (Django Model)", user_fields)
        mongodb_student_box = self.create_box("MONGODB_STUDENTS (Collection)", mongodb_student_fields)
        mongodb_attendance_box = self.create_box("MONGODB_ATTENDANCE (Collection)", mongodb_attendance_fields)
        
        # Arrange entities in a grid
        max_height = max(len(student_box), len(attendance_box), len(user_box), 
                        len(mongodb_student_box), len(mongodb_attendance_box))
        
        # Pad all boxes to same height
        for box in [student_box, attendance_box, user_box, mongodb_student_box, mongodb_attendance_box]:
            while len(box) < max_height:
                box.append("│" + " " * 28 + "│")
        
        # Create the layout
        diagram.append("SQLite Database (Django ORM)                    MongoDB Database (Face Recognition)")
        diagram.append("─" * 50 + "                    " + "─" * 50)
        diagram.append("")
        
        # Top row (Student and MongoDB_Students)
        for i in range(max_height):
            line = student_box[i] + "    " + mongodb_student_box[i]
            diagram.append(line)
        
        diagram.append("")
        diagram.append("    │ 1:M relationship                    Data Sync ────┐")
        diagram.append("    │                                         │")
        diagram.append("    ▼                                         ▼")
        diagram.append("")
        
        # Middle row (Attendance and MongoDB_Attendance)
        for i in range(max_height):
            line = attendance_box[i] + "    " + mongodb_attendance_box[i]
            diagram.append(line)
        
        diagram.append("")
        diagram.append("    ▲")
        diagram.append("    │ 1:M relationship")
        diagram.append("    │")
        diagram.append("")
        
        # Bottom row (User)
        for i in range(max_height):
            line = user_box[i] + "    " + " " * 34
            diagram.append(line)
        
        diagram.append("")
        diagram.append("=" * 80)
        diagram.append("")
        
        # Add relationships explanation
        diagram.append("RELATIONSHIPS:")
        diagram.append("─" * 20)
        diagram.append("• Student ──1:M──> Attendance (One student can have many attendance records)")
        diagram.append("• User ──1:M──> Student (One admin user can manage many students)")
        diagram.append("• Student ──sync──> MongoDB_Students (Data synchronization)")
        diagram.append("• Attendance ──sync──> MongoDB_Attendance (Data synchronization)")
        diagram.append("")
        
        # Add key features
        diagram.append("KEY FEATURES:")
        diagram.append("─" * 20)
        diagram.append("• Ultra-Strict Face Recognition (92.98% threshold)")
        diagram.append("• Time-Based Attendance Logic (Present/Late/Absent/Checkout/Day Finished)")
        diagram.append("• Proxy Attack Prevention (Rejects unregistered faces)")
        diagram.append("• Hybrid Database Architecture (SQLite + MongoDB)")
        diagram.append("• Automatic Data Synchronization")
        diagram.append("• Face Embedding Storage (128-dimensional vectors)")
        diagram.append("")
        
        # Add field type explanations
        diagram.append("FIELD TYPE LEGEND:")
        diagram.append("─" * 20)
        diagram.append("PK = Primary Key    UK = Unique Key    FK = Foreign Key")
        diagram.append("")
        
        return diagram
    
    def save_diagram(self, filename='ai_attendance_er_diagram.txt'):
        """Save the diagram to a text file"""
        diagram = self.generate_diagram()
        
        with open(filename, 'w', encoding='utf-8') as f:
            for line in diagram:
                f.write(line + '\n')
        
        print(f"✅ Text ER diagram saved as: {filename}")
    
    def print_diagram(self):
        """Print the diagram to console"""
        diagram = self.generate_diagram()
        
        for line in diagram:
            print(line)

def main():
    """Main function to generate ER diagram"""
    try:
        print("🎨 Generating AI Attendance Manager Text ER Diagram...")
        print("")
        
        # Create diagram generator
        generator = TextERDiagramGenerator()
        
        # Print diagram to console
        generator.print_diagram()
        
        # Save diagram to file
        generator.save_diagram('ai_attendance_er_diagram.txt')
        
        print("")
        print("🎉 Text ER diagram generated successfully!")
        print("📁 Files created:")
        print("   - ai_attendance_er_diagram.txt")
        
    except Exception as e:
        print(f"❌ Error generating ER diagram: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
