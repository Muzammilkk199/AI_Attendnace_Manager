#!/usr/bin/env python3
"""
High-Quality PNG ER Diagram Generator for AI Attendance Manager
This script creates a clean, well-spaced PNG ER diagram with professional appearance
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Rectangle
import numpy as np
import os

class PNGERDiagramGenerator:
    def __init__(self):
        # Set up the figure with high DPI for crisp output
        self.fig, self.ax = plt.subplots(1, 1, figsize=(22, 16), dpi=300)
        self.ax.set_xlim(0, 18)
        self.ax.set_ylim(0, 14)
        self.ax.axis('off')
        
        # Professional color scheme
        self.colors = {
            'django_model': '#E3F2FD',      # Light blue
            'mongodb_collection': '#F3E5F5', # Light purple
            'primary_key': '#2E7D32',        # Dark green
            'foreign_key': '#E65100',        # Dark orange
            'unique_key': '#1565C0',         # Dark blue
            'text_primary': '#212121',       # Dark gray
            'text_secondary': '#424242',     # Medium gray
            'border_django': '#1976D2',      # Blue border
            'border_mongodb': '#7B1FA2',     # Purple border
        }
        
        # Entity positions with much better spacing
        self.positions = {
            'Student': (2.5, 9.5),
            'Attendance': (2.5, 6.5),
            'User': (2.5, 3.5),
            'MongoDB_Students': (12.5, 9.5),
            'MongoDB_Attendance': (12.5, 6.5),
        }
        
        # Entity sizes with more space
        self.entity_sizes = {
            'Student': (4, 2.5),
            'Attendance': (4, 2.5),
            'User': (4, 2.5),
            'MongoDB_Students': (4, 2.5),
            'MongoDB_Attendance': (4, 2.5),
        }

    def draw_entity(self, name, position, size, entity_type='django_model'):
        """Draw a clean entity box with proper spacing"""
        x, y = position
        width, height = size
        
        # Draw entity box with rounded corners
        if entity_type == 'django_model':
            color = self.colors['django_model']
            edge_color = self.colors['border_django']
        else:
            color = self.colors['mongodb_collection']
            edge_color = self.colors['border_mongodb']
        
        entity_box = FancyBboxPatch(
            (x - width/2, y - height/2), width, height,
            boxstyle="round,pad=0.15",
            facecolor=color,
            edgecolor=edge_color,
            linewidth=2.5
        )
        self.ax.add_patch(entity_box)
        
        # Add entity name with better typography
        self.ax.text(x, y + height/2 - 0.2, name, 
                    ha='center', va='center', fontsize=14, fontweight='bold',
                    color=self.colors['text_primary'],
                    bbox=dict(boxstyle="round,pad=0.4", facecolor='white', 
                             alpha=0.95, edgecolor=edge_color, linewidth=1))
        
        return entity_box

    def draw_fields(self, entity_name, fields, position, size):
        """Draw field information with clean spacing"""
        x, y = position
        width, height = size
        
        # Calculate field positions with much better spacing
        field_height = 0.25
        start_y = y + height/2 - 0.7
        
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
            color = self.colors['text_primary']
            if field.get('primary_key', False):
                color = self.colors['primary_key']
            elif field.get('unique', False):
                color = self.colors['unique_key']
            elif field.get('foreign_key', False):
                color = self.colors['foreign_key']
            
            self.ax.text(x - width/2 + 0.25, field_y, field_text,
                        ha='left', va='center', fontsize=11, color=color, 
                        fontweight='bold', fontfamily='monospace')

    def draw_relationship(self, entity1, entity2, relationship_type="one-to-many"):
        """Draw clean relationship lines"""
        pos1 = self.positions[entity1]
        pos2 = self.positions[entity2]
        
        if relationship_type == "one-to-many":
            # Line from entity1 to entity2
            start_x = pos1[0] + self.entity_sizes[entity1][0]/2
            start_y = pos1[1]
            end_x = pos2[0] - self.entity_sizes[entity2][0]/2
            end_y = pos2[1]
            
            # Draw clean line
            self.ax.plot([start_x, end_x], [start_y, end_y], 
                        'k-', linewidth=3, alpha=0.8, solid_capstyle='round')
            
            # Add cardinality indicators with better styling
            self.ax.text(start_x + 0.3, start_y + 0.3, "1", 
                        ha='center', va='center', fontsize=12, fontweight='bold',
                        bbox=dict(boxstyle="circle,pad=0.3", facecolor='white', 
                                 alpha=0.95, edgecolor='black', linewidth=1.5))
            self.ax.text(end_x - 0.3, end_y + 0.3, "M", 
                        ha='center', va='center', fontsize=12, fontweight='bold',
                        bbox=dict(boxstyle="circle,pad=0.3", facecolor='white', 
                                 alpha=0.95, edgecolor='black', linewidth=1.5))
        
        elif relationship_type == "sync":
            # Dotted line for synchronization
            start_x = pos1[0] + self.entity_sizes[entity1][0]/2
            start_y = pos1[1]
            end_x = pos2[0] - self.entity_sizes[entity2][0]/2
            end_y = pos2[1]
            
            self.ax.plot([start_x, end_x], [start_y, end_y], 
                        'k--', linewidth=2.5, alpha=0.7, dash_capstyle='round')
            
            # Add sync label
            mid_x = (start_x + end_x) / 2
            mid_y = (start_y + end_y) / 2
            self.ax.text(mid_x, mid_y + 0.4, "Data Sync", 
                        ha='center', va='center', fontsize=11, style='italic',
                        bbox=dict(boxstyle="round,pad=0.3", facecolor='#FFF9C4', 
                                 alpha=0.9, edgecolor='#F57F17', linewidth=1.5))

    def add_title(self):
        """Add professional title"""
        self.ax.text(8, 11.5, 'AI Attendance Manager - Entity Relationship Diagram', 
                    ha='center', va='center', fontsize=20, fontweight='bold',
                    color=self.colors['text_primary'],
                    bbox=dict(boxstyle="round,pad=0.6", facecolor='#E8F5E8', 
                             alpha=0.95, edgecolor='#4CAF50', linewidth=2))

    def add_database_labels(self):
        """Add clear database labels"""
        # SQLite label
        self.ax.text(3, 1.5, 'SQLite Database\n(Django ORM)', 
                    ha='center', va='center', fontsize=14, fontweight='bold',
                    color='white',
                    bbox=dict(boxstyle="round,pad=0.5", facecolor='#1976D2', 
                             alpha=0.95, edgecolor='#0D47A1', linewidth=2))
        
        # MongoDB label
        self.ax.text(11, 1.5, 'MongoDB Database\n(Face Recognition)', 
                    ha='center', va='center', fontsize=14, fontweight='bold',
                    color='white',
                    bbox=dict(boxstyle="round,pad=0.5", facecolor='#7B1FA2', 
                             alpha=0.95, edgecolor='#4A148C', linewidth=2))

    def add_legend(self):
        """Add professional legend"""
        legend_elements = [
            plt.Rectangle((0, 0), 1, 1, facecolor=self.colors['django_model'], 
                         edgecolor=self.colors['border_django'], label='Django Model (SQLite)'),
            plt.Rectangle((0, 0), 1, 1, facecolor=self.colors['mongodb_collection'], 
                         edgecolor=self.colors['border_mongodb'], label='MongoDB Collection'),
            plt.Line2D([0], [0], color='black', linewidth=3, label='One-to-Many Relationship'),
            plt.Line2D([0], [0], color='black', linewidth=2.5, linestyle='--', 
                      alpha=0.7, label='Data Synchronization'),
            plt.Line2D([0], [0], color=self.colors['primary_key'], linewidth=4, 
                      label='Primary Key (PK)'),
            plt.Line2D([0], [0], color=self.colors['foreign_key'], linewidth=4, 
                      label='Foreign Key (FK)'),
            plt.Line2D([0], [0], color=self.colors['unique_key'], linewidth=4, 
                      label='Unique Key (UK)'),
        ]
        
        self.ax.legend(handles=legend_elements, loc='upper right', 
                      bbox_to_anchor=(0.98, 0.98), fontsize=11,
                      frameon=True, fancybox=True, shadow=True,
                      facecolor='white', edgecolor='gray')

    def add_features_box(self):
        """Add key features information"""
        features_text = """Key Features:
• Ultra-Strict Face Recognition (92.98% threshold)
• Time-Based Attendance Logic
• Proxy Attack Prevention
• Hybrid Database Architecture
• Automatic Data Synchronization"""
        
        self.ax.text(8, 0.5, features_text, 
                    ha='center', va='center', fontsize=11, fontweight='bold',
                    color=self.colors['text_primary'],
                    bbox=dict(boxstyle="round,pad=0.4", facecolor='#FFF3E0', 
                             alpha=0.95, edgecolor='#FF9800', linewidth=2))

    def generate_diagram(self):
        """Generate the complete high-quality ER diagram"""
        # Add title
        self.add_title()
        
        # Add some spacing before entities
        self.ax.text(8, 13, '', ha='center', va='center', fontsize=1)
        
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
        
        # Set clean background
        self.ax.set_facecolor('#FAFAFA')
        
        # Adjust layout for much better spacing
        plt.tight_layout(pad=3.0)
        
        return self.fig

    def save_diagram(self, filename='ai_attendance_er_diagram.png', dpi=300):
        """Save the diagram as high-quality PNG"""
        self.fig.savefig(filename, dpi=dpi, bbox_inches='tight', 
                        facecolor='white', edgecolor='none', 
                        pad_inches=0.5, format='png')
        print(f"✅ High-quality PNG ER diagram saved as: {filename}")

def main():
    """Main function to generate high-quality PNG ER diagram"""
    try:
        print("🎨 Generating High-Quality PNG ER Diagram...")
        print("📐 Creating clean, well-spaced diagram with professional appearance...")
        
        # Create diagram generator
        generator = PNGERDiagramGenerator()
        
        # Generate diagram
        fig = generator.generate_diagram()
        
        # Save as high-quality PNG
        generator.save_diagram('ai_attendance_er_diagram.png', dpi=300)
        
        # Also save as PDF for vector format
        generator.save_diagram('ai_attendance_er_diagram.pdf', dpi=300)
        
        print("")
        print("🎉 High-quality ER diagram generated successfully!")
        print("📁 Files created:")
        print("   - ai_attendance_er_diagram.png (High-resolution PNG)")
        print("   - ai_attendance_er_diagram.pdf (Vector PDF)")
        print("")
        print("✨ Features:")
        print("   - Clean, professional spacing")
        print("   - High-resolution output (300 DPI)")
        print("   - Color-coded entities and relationships")
        print("   - Clear typography and layout")
        print("   - Ready for presentations and documentation")
        
    except Exception as e:
        print(f"❌ Error generating PNG ER diagram: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
