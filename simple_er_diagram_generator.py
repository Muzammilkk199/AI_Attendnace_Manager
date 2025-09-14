#!/usr/bin/env python3
"""
Simple AI Attendance Manager ER Diagram Generator
This script generates a visual ER diagram without requiring Django setup
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
import numpy as np

class SimpleERDiagramGenerator:
    def __init__(self):
        self.fig, self.ax = plt.subplots(1, 1, figsize=(18, 12))
        self.ax.set_xlim(0, 12)
        self.ax.set_ylim(0, 10)
        self.ax.axis('off')
        
        # Colors for different entity types
        self.colors = {
            'django_model': '#E3F2FD',      # Light blue
            'mongodb_collection': '#F3E5F5', # Light purple
            'primary_key': '#4CAF50',        # Green
            'foreign_key': '#FF9800',        # Orange
            'unique_key': '#2196F3',         # Blue
        }
        
        # Entity positions
        self.positions = {
            'Student': (2, 7.5),
            'Attendance': (2, 5),
            'User': (2, 2.5),
            'MongoDB_Students': (8, 7.5),
            'MongoDB_Attendance': (8, 5),
        }
        
        # Entity sizes
        self.entity_sizes = {
            'Student': (3, 2),
            'Attendance': (3, 2),
            'User': (3, 2),
            'MongoDB_Students': (3, 2),
            'MongoDB_Attendance': (3, 2),
        }

    def draw_entity(self, name, position, size, entity_type='django_model'):
        """Draw an entity box with fields"""
        x, y = position
        width, height = size
        
        # Draw entity box
        if entity_type == 'django_model':
            color = self.colors['django_model']
            edge_color = '#1976D2'
        else:
            color = self.colors['mongodb_collection']
            edge_color = '#7B1FA2'
        
        entity_box = FancyBboxPatch(
            (x - width/2, y - height/2), width, height,
            boxstyle="round,pad=0.1",
            facecolor=color,
            edgecolor=edge_color,
            linewidth=2
        )
        self.ax.add_patch(entity_box)
        
        # Add entity name
        self.ax.text(x, y + height/2 - 0.15, name, 
                    ha='center', va='center', fontsize=14, fontweight='bold',
                    bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.9))
        
        return entity_box

    def draw_fields(self, entity_name, fields, position, size):
        """Draw field information inside entity"""
        x, y = position
        width, height = size
        
        # Calculate field positions
        field_height = 0.18
        start_y = y + height/2 - 0.5
        
        for i, field in enumerate(fields):
            field_y = start_y - i * field_height
            
            # Field name and type
            field_text = f"{field['name']}: {field['type']}"
            
            # Add indicators for special field types
            indicators = []
            if field.get('primary_key', False):
                indicators.append("PK")
            if field.get('unique', False) and not field.get('primary_key', False):
                indicators.append("UK")
            if field.get('foreign_key', False):
                indicators.append("FK")
            
            if indicators:
                field_text += f" ({', '.join(indicators)})"
            
            # Color code the text
            color = 'black'
            if field.get('primary_key', False):
                color = self.colors['primary_key']
            elif field.get('unique', False):
                color = self.colors['unique_key']
            elif field.get('foreign_key', False):
                color = self.colors['foreign_key']
            
            self.ax.text(x - width/2 + 0.15, field_y, field_text,
                        ha='left', va='center', fontsize=10, color=color, fontweight='bold')

    def draw_relationship(self, entity1, entity2, relationship_type="one-to-many"):
        """Draw relationship line between entities"""
        pos1 = self.positions[entity1]
        pos2 = self.positions[entity2]
        
        # Calculate connection points
        if relationship_type == "one-to-many":
            # Line from entity1 to entity2
            start_x = pos1[0] + self.entity_sizes[entity1][0]/2
            start_y = pos1[1]
            end_x = pos2[0] - self.entity_sizes[entity2][0]/2
            end_y = pos2[1]
            
            # Draw line
            self.ax.plot([start_x, end_x], [start_y, end_y], 
                        'k-', linewidth=3, alpha=0.8)
            
            # Add cardinality indicators
            self.ax.text(start_x + 0.2, start_y + 0.2, "1", 
                        ha='center', va='center', fontsize=12, fontweight='bold',
                        bbox=dict(boxstyle="circle", facecolor='white', alpha=0.9))
            self.ax.text(end_x - 0.2, end_y + 0.2, "M", 
                        ha='center', va='center', fontsize=12, fontweight='bold',
                        bbox=dict(boxstyle="circle", facecolor='white', alpha=0.9))
        
        elif relationship_type == "sync":
            # Dotted line for synchronization
            start_x = pos1[0] + self.entity_sizes[entity1][0]/2
            start_y = pos1[1]
            end_x = pos2[0] - self.entity_sizes[entity2][0]/2
            end_y = pos2[1]
            
            self.ax.plot([start_x, end_x], [start_y, end_y], 
                        'k--', linewidth=2, alpha=0.6)
            
            # Add sync label
            mid_x = (start_x + end_x) / 2
            mid_y = (start_y + end_y) / 2
            self.ax.text(mid_x, mid_y + 0.3, "Data Sync", 
                        ha='center', va='center', fontsize=10, style='italic',
                        bbox=dict(boxstyle="round,pad=0.3", facecolor='yellow', alpha=0.8))

    def add_legend(self):
        """Add legend to the diagram"""
        legend_elements = [
            plt.Rectangle((0, 0), 1, 1, facecolor=self.colors['django_model'], 
                         edgecolor='#1976D2', label='Django Model (SQLite)'),
            plt.Rectangle((0, 0), 1, 1, facecolor=self.colors['mongodb_collection'], 
                         edgecolor='#7B1FA2', label='MongoDB Collection'),
            plt.Line2D([0], [0], color='black', linewidth=3, label='One-to-Many Relationship'),
            plt.Line2D([0], [0], color='black', linewidth=2, linestyle='--', 
                      alpha=0.6, label='Data Synchronization'),
            plt.Line2D([0], [0], color=self.colors['primary_key'], linewidth=4, 
                      label='Primary Key (PK)'),
            plt.Line2D([0], [0], color=self.colors['foreign_key'], linewidth=4, 
                      label='Foreign Key (FK)'),
            plt.Line2D([0], [0], color=self.colors['unique_key'], linewidth=4, 
                      label='Unique Key (UK)'),
        ]
        
        self.ax.legend(handles=legend_elements, loc='upper right', 
                      bbox_to_anchor=(0.98, 0.98), fontsize=11)

    def add_title(self):
        """Add title to the diagram"""
        self.ax.text(6, 9.5, 'AI Attendance Manager - Entity Relationship Diagram', 
                    ha='center', va='center', fontsize=18, fontweight='bold',
                    bbox=dict(boxstyle="round,pad=0.5", facecolor='lightblue', alpha=0.9))

    def add_database_labels(self):
        """Add database labels"""
        # SQLite label
        self.ax.text(2, 1, 'SQLite Database\n(Django ORM)\n\n• Relational Data\n• Business Logic\n• Data Integrity', 
                    ha='center', va='center', fontsize=12, fontweight='bold',
                    bbox=dict(boxstyle="round,pad=0.4", facecolor='lightgreen', alpha=0.9))
        
        # MongoDB label
        self.ax.text(8, 1, 'MongoDB Database\n(Face Recognition)\n\n• Face Embeddings\n• High Performance\n• Similarity Search', 
                    ha='center', va='center', fontsize=12, fontweight='bold',
                    bbox=dict(boxstyle="round,pad=0.4", facecolor='lightcoral', alpha=0.9))

    def add_features_box(self):
        """Add key features box"""
        features_text = """Key Features:
• Ultra-Strict Face Recognition (92.98% threshold)
• Time-Based Attendance Logic
• Proxy Attack Prevention
• Automatic Data Synchronization
• Hybrid Database Architecture"""
        
        self.ax.text(6, 0.5, features_text, 
                    ha='center', va='center', fontsize=10, fontweight='bold',
                    bbox=dict(boxstyle="round,pad=0.4", facecolor='lightyellow', alpha=0.9))

    def generate_diagram(self):
        """Generate the complete ER diagram"""
        # Add title
        self.add_title()
        
        # Define model fields
        student_fields = [
            {'name': 'id', 'type': 'AutoField', 'primary_key': True},
            {'name': 'student_id', 'type': 'CharField', 'unique': True},
            {'name': 'name', 'type': 'CharField'},
            {'name': 'first_name', 'type': 'CharField'},
            {'name': 'last_name', 'type': 'CharField'},
            {'name': 'email', 'type': 'EmailField'},
            {'name': 'phone', 'type': 'CharField'},
            {'name': 'class_name', 'type': 'CharField'},
            {'name': 'section', 'type': 'CharField'},
            {'name': 'created_at', 'type': 'DateTimeField'},
            {'name': 'is_active', 'type': 'BooleanField'},
        ]
        
        attendance_fields = [
            {'name': 'id', 'type': 'AutoField', 'primary_key': True},
            {'name': 'student', 'type': 'ForeignKey', 'foreign_key': True},
            {'name': 'date', 'type': 'DateField'},
            {'name': 'status', 'type': 'CharField'},
            {'name': 'timestamp', 'type': 'DateTimeField'},
            {'name': 'confidence', 'type': 'FloatField'},
            {'name': 'notes', 'type': 'TextField'},
        ]
        
        user_fields = [
            {'name': 'id', 'type': 'AutoField', 'primary_key': True},
            {'name': 'username', 'type': 'CharField', 'unique': True},
            {'name': 'email', 'type': 'EmailField'},
            {'name': 'first_name', 'type': 'CharField'},
            {'name': 'last_name', 'type': 'CharField'},
            {'name': 'is_staff', 'type': 'BooleanField'},
            {'name': 'is_active', 'type': 'BooleanField'},
            {'name': 'date_joined', 'type': 'DateTimeField'},
        ]
        
        mongodb_student_fields = [
            {'name': '_id', 'type': 'ObjectId', 'primary_key': True},
            {'name': 'student_id', 'type': 'String', 'unique': True},
            {'name': 'name', 'type': 'String'},
            {'name': 'first_name', 'type': 'String'},
            {'name': 'last_name', 'type': 'String'},
            {'name': 'email', 'type': 'String'},
            {'name': 'phone', 'type': 'String'},
            {'name': 'class_name', 'type': 'String'},
            {'name': 'section', 'type': 'String'},
            {'name': 'embedding', 'type': 'Array'},
            {'name': 'is_active', 'type': 'Boolean'},
            {'name': 'django_id', 'type': 'Integer'},
            {'name': 'created_at', 'type': 'DateTime'},
            {'name': 'updated_at', 'type': 'DateTime'},
        ]
        
        mongodb_attendance_fields = [
            {'name': '_id', 'type': 'ObjectId', 'primary_key': True},
            {'name': 'student_id', 'type': 'String'},
            {'name': 'student_name', 'type': 'String'},
            {'name': 'date', 'type': 'String'},
            {'name': 'status', 'type': 'String'},
            {'name': 'confidence', 'type': 'Float'},
            {'name': 'notes', 'type': 'Text'},
            {'name': 'image_data', 'type': 'String'},
            {'name': 'timestamp', 'type': 'DateTime'},
            {'name': 'django_id', 'type': 'Integer'},
            {'name': 'created_at', 'type': 'DateTime'},
            {'name': 'updated_at', 'type': 'DateTime'},
        ]
        
        # Draw entities
        self.draw_entity('Student', self.positions['Student'], 
                        self.entity_sizes['Student'], 'django_model')
        self.draw_entity('Attendance', self.positions['Attendance'], 
                        self.entity_sizes['Attendance'], 'django_model')
        self.draw_entity('User', self.positions['User'], 
                        self.entity_sizes['User'], 'django_model')
        self.draw_entity('MongoDB_Students', self.positions['MongoDB_Students'], 
                        self.entity_sizes['MongoDB_Students'], 'mongodb_collection')
        self.draw_entity('MongoDB_Attendance', self.positions['MongoDB_Attendance'], 
                        self.entity_sizes['MongoDB_Attendance'], 'mongodb_collection')
        
        # Draw fields
        self.draw_fields('Student', student_fields, self.positions['Student'], 
                        self.entity_sizes['Student'])
        self.draw_fields('Attendance', attendance_fields, self.positions['Attendance'], 
                        self.entity_sizes['Attendance'])
        self.draw_fields('User', user_fields, self.positions['User'], 
                        self.entity_sizes['User'])
        self.draw_fields('MongoDB_Students', mongodb_student_fields, 
                        self.positions['MongoDB_Students'], self.entity_sizes['MongoDB_Students'])
        self.draw_fields('MongoDB_Attendance', mongodb_attendance_fields, 
                        self.positions['MongoDB_Attendance'], self.entity_sizes['MongoDB_Attendance'])
        
        # Draw relationships
        self.draw_relationship('Student', 'Attendance', 'one-to-many')
        self.draw_relationship('User', 'Student', 'one-to-many')
        self.draw_relationship('Student', 'MongoDB_Students', 'sync')
        self.draw_relationship('Attendance', 'MongoDB_Attendance', 'sync')
        
        # Add database labels
        self.add_database_labels()
        
        # Add features box
        self.add_features_box()
        
        # Add legend
        self.add_legend()
        
        # Set background
        self.ax.set_facecolor('#F8F9FA')
        
        # Adjust layout
        plt.tight_layout()
        
        return self.fig

    def save_diagram(self, filename='ai_attendance_er_diagram.png', dpi=300):
        """Save the diagram to file"""
        self.fig.savefig(filename, dpi=dpi, bbox_inches='tight', 
                        facecolor='white', edgecolor='none')
        print(f"✅ ER diagram saved as: {filename}")

def main():
    """Main function to generate ER diagram"""
    try:
        print("🎨 Generating AI Attendance Manager ER Diagram...")
        
        # Create diagram generator
        generator = SimpleERDiagramGenerator()
        
        # Generate diagram
        fig = generator.generate_diagram()
        
        # Save diagram in multiple formats
        generator.save_diagram('ai_attendance_er_diagram.png')
        generator.save_diagram('ai_attendance_er_diagram.pdf')
        generator.save_diagram('ai_attendance_er_diagram.svg')
        
        # Show diagram
        plt.show()
        
        print("🎉 ER diagram generated successfully!")
        print("📁 Files created:")
        print("   - ai_attendance_er_diagram.png (High resolution)")
        print("   - ai_attendance_er_diagram.pdf (Vector format)")
        print("   - ai_attendance_er_diagram.svg (Scalable vector)")
        
    except Exception as e:
        print(f"❌ Error generating ER diagram: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
