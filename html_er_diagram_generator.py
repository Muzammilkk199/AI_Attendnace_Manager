#!/usr/bin/env python3
"""
HTML-based ER Diagram Generator for AI Attendance Manager
This script creates a visual HTML ER diagram with CSS styling
"""

import os
import sys

class HTMLERDiagramGenerator:
    def __init__(self):
        self.html_content = ""
        
    def generate_html_diagram(self):
        """Generate HTML ER diagram"""
        html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Attendance Manager - ER Diagram</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }
        
        .header p {
            margin: 10px 0 0 0;
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .diagram-container {
            padding: 40px;
            background: #f8f9fa;
        }
        
        .database-section {
            margin-bottom: 40px;
        }
        
        .database-title {
            font-size: 1.8em;
            font-weight: bold;
            margin-bottom: 20px;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            color: white;
        }
        
        .sqlite-title {
            background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);
        }
        
        .mongodb-title {
            background: linear-gradient(135deg, #4CAF50 0%, #388E3C 100%);
        }
        
        .entities-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 30px;
            margin-bottom: 30px;
        }
        
        .entity {
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            overflow: hidden;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .entity:hover {
            transform: translateY(-5px);
            box-shadow: 0 20px 40px rgba(0,0,0,0.15);
        }
        
        .entity-header {
            padding: 20px;
            color: white;
            font-weight: bold;
            font-size: 1.2em;
        }
        
        .django-entity {
            background: linear-gradient(135deg, #1976D2 0%, #1565C0 100%);
        }
        
        .mongodb-entity {
            background: linear-gradient(135deg, #7B1FA2 0%, #6A1B9A 100%);
        }
        
        .entity-fields {
            padding: 20px;
        }
        
        .field {
            padding: 8px 0;
            border-bottom: 1px solid #eee;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }
        
        .field:last-child {
            border-bottom: none;
        }
        
        .field-name {
            font-weight: bold;
            color: #333;
        }
        
        .field-type {
            color: #666;
        }
        
        .field-constraint {
            color: #e74c3c;
            font-weight: bold;
        }
        
        .relationships {
            margin: 40px 0;
            padding: 30px;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        }
        
        .relationships h2 {
            color: #333;
            margin-bottom: 20px;
            font-size: 1.8em;
        }
        
        .relationship-item {
            padding: 15px;
            margin: 10px 0;
            background: #f8f9fa;
            border-left: 5px solid #4CAF50;
            border-radius: 5px;
        }
        
        .features {
            margin: 40px 0;
            padding: 30px;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        }
        
        .features h2 {
            color: #333;
            margin-bottom: 20px;
            font-size: 1.8em;
        }
        
        .feature-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }
        
        .feature-item {
            padding: 20px;
            background: linear-gradient(135deg, #FFE0B2 0%, #FFCC02 100%);
            border-radius: 10px;
            border-left: 5px solid #FF9800;
        }
        
        .feature-item h3 {
            margin: 0 0 10px 0;
            color: #E65100;
        }
        
        .legend {
            margin: 40px 0;
            padding: 30px;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        }
        
        .legend h2 {
            color: #333;
            margin-bottom: 20px;
            font-size: 1.8em;
        }
        
        .legend-items {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }
        
        .legend-item {
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            color: white;
            font-weight: bold;
        }
        
        .pk { background: #4CAF50; }
        .fk { background: #FF9800; }
        .uk { background: #2196F3; }
        .django { background: #1976D2; }
        .mongodb { background: #7B1FA2; }
        
        .sync-arrow {
            text-align: center;
            font-size: 2em;
            color: #4CAF50;
            margin: 20px 0;
        }
        
        @media (max-width: 768px) {
            .entities-grid {
                grid-template-columns: 1fr;
            }
            
            .header h1 {
                font-size: 2em;
            }
            
            .diagram-container {
                padding: 20px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>AI Attendance Manager</h1>
            <p>Entity Relationship Diagram</p>
        </div>
        
        <div class="diagram-container">
            <div class="database-section">
                <div class="database-title sqlite-title">
                    📊 SQLite Database (Django ORM)
                </div>
                <div class="entities-grid">
                    <div class="entity">
                        <div class="entity-header django-entity">
                            👤 Student Model
                        </div>
                        <div class="entity-fields">
                            <div class="field">
                                <span class="field-name">id</span>: 
                                <span class="field-type">AutoField</span> 
                                <span class="field-constraint">(PK)</span>
                            </div>
                            <div class="field">
                                <span class="field-name">student_id</span>: 
                                <span class="field-type">CharField</span> 
                                <span class="field-constraint">(UK)</span>
                            </div>
                            <div class="field">
                                <span class="field-name">name</span>: 
                                <span class="field-type">CharField</span>
                            </div>
                            <div class="field">
                                <span class="field-name">first_name</span>: 
                                <span class="field-type">CharField</span>
                            </div>
                            <div class="field">
                                <span class="field-name">last_name</span>: 
                                <span class="field-type">CharField</span>
                            </div>
                            <div class="field">
                                <span class="field-name">email</span>: 
                                <span class="field-type">EmailField</span>
                            </div>
                            <div class="field">
                                <span class="field-name">phone</span>: 
                                <span class="field-type">CharField</span>
                            </div>
                            <div class="field">
                                <span class="field-name">class_name</span>: 
                                <span class="field-type">CharField</span>
                            </div>
                            <div class="field">
                                <span class="field-name">section</span>: 
                                <span class="field-type">CharField</span>
                            </div>
                            <div class="field">
                                <span class="field-name">created_at</span>: 
                                <span class="field-type">DateTimeField</span>
                            </div>
                            <div class="field">
                                <span class="field-name">is_active</span>: 
                                <span class="field-type">BooleanField</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="entity">
                        <div class="entity-header django-entity">
                            📅 Attendance Model
                        </div>
                        <div class="entity-fields">
                            <div class="field">
                                <span class="field-name">id</span>: 
                                <span class="field-type">AutoField</span> 
                                <span class="field-constraint">(PK)</span>
                            </div>
                            <div class="field">
                                <span class="field-name">student</span>: 
                                <span class="field-type">ForeignKey</span> 
                                <span class="field-constraint">(FK)</span>
                            </div>
                            <div class="field">
                                <span class="field-name">date</span>: 
                                <span class="field-type">DateField</span>
                            </div>
                            <div class="field">
                                <span class="field-name">status</span>: 
                                <span class="field-type">CharField</span>
                            </div>
                            <div class="field">
                                <span class="field-name">timestamp</span>: 
                                <span class="field-type">DateTimeField</span>
                            </div>
                            <div class="field">
                                <span class="field-name">confidence</span>: 
                                <span class="field-type">FloatField</span>
                            </div>
                            <div class="field">
                                <span class="field-name">notes</span>: 
                                <span class="field-type">TextField</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="entity">
                        <div class="entity-header django-entity">
                            👨‍💼 User Model
                        </div>
                        <div class="entity-fields">
                            <div class="field">
                                <span class="field-name">id</span>: 
                                <span class="field-type">AutoField</span> 
                                <span class="field-constraint">(PK)</span>
                            </div>
                            <div class="field">
                                <span class="field-name">username</span>: 
                                <span class="field-type">CharField</span> 
                                <span class="field-constraint">(UK)</span>
                            </div>
                            <div class="field">
                                <span class="field-name">email</span>: 
                                <span class="field-type">EmailField</span>
                            </div>
                            <div class="field">
                                <span class="field-name">first_name</span>: 
                                <span class="field-type">CharField</span>
                            </div>
                            <div class="field">
                                <span class="field-name">last_name</span>: 
                                <span class="field-type">CharField</span>
                            </div>
                            <div class="field">
                                <span class="field-name">is_staff</span>: 
                                <span class="field-type">BooleanField</span>
                            </div>
                            <div class="field">
                                <span class="field-name">is_active</span>: 
                                <span class="field-type">BooleanField</span>
                            </div>
                            <div class="field">
                                <span class="field-name">date_joined</span>: 
                                <span class="field-type">DateTimeField</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="sync-arrow">
                ⬇️ Data Synchronization ⬇️
            </div>
            
            <div class="database-section">
                <div class="database-title mongodb-title">
                    🍃 MongoDB Database (Face Recognition)
                </div>
                <div class="entities-grid">
                    <div class="entity">
                        <div class="entity-header mongodb-entity">
                            👤 MongoDB Students Collection
                        </div>
                        <div class="entity-fields">
                            <div class="field">
                                <span class="field-name">_id</span>: 
                                <span class="field-type">ObjectId</span> 
                                <span class="field-constraint">(PK)</span>
                            </div>
                            <div class="field">
                                <span class="field-name">student_id</span>: 
                                <span class="field-type">String</span> 
                                <span class="field-constraint">(UK)</span>
                            </div>
                            <div class="field">
                                <span class="field-name">name</span>: 
                                <span class="field-type">String</span>
                            </div>
                            <div class="field">
                                <span class="field-name">first_name</span>: 
                                <span class="field-type">String</span>
                            </div>
                            <div class="field">
                                <span class="field-name">last_name</span>: 
                                <span class="field-type">String</span>
                            </div>
                            <div class="field">
                                <span class="field-name">email</span>: 
                                <span class="field-type">String</span>
                            </div>
                            <div class="field">
                                <span class="field-name">phone</span>: 
                                <span class="field-type">String</span>
                            </div>
                            <div class="field">
                                <span class="field-name">class_name</span>: 
                                <span class="field-type">String</span>
                            </div>
                            <div class="field">
                                <span class="field-name">section</span>: 
                                <span class="field-type">String</span>
                            </div>
                            <div class="field">
                                <span class="field-name">embedding</span>: 
                                <span class="field-type">Array</span>
                            </div>
                            <div class="field">
                                <span class="field-name">is_active</span>: 
                                <span class="field-type">Boolean</span>
                            </div>
                            <div class="field">
                                <span class="field-name">django_id</span>: 
                                <span class="field-type">Integer</span>
                            </div>
                            <div class="field">
                                <span class="field-name">created_at</span>: 
                                <span class="field-type">DateTime</span>
                            </div>
                            <div class="field">
                                <span class="field-name">updated_at</span>: 
                                <span class="field-type">DateTime</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="entity">
                        <div class="entity-header mongodb-entity">
                            📅 MongoDB Attendance Collection
                        </div>
                        <div class="entity-fields">
                            <div class="field">
                                <span class="field-name">_id</span>: 
                                <span class="field-type">ObjectId</span> 
                                <span class="field-constraint">(PK)</span>
                            </div>
                            <div class="field">
                                <span class="field-name">student_id</span>: 
                                <span class="field-type">String</span>
                            </div>
                            <div class="field">
                                <span class="field-name">student_name</span>: 
                                <span class="field-type">String</span>
                            </div>
                            <div class="field">
                                <span class="field-name">date</span>: 
                                <span class="field-type">String</span>
                            </div>
                            <div class="field">
                                <span class="field-name">status</span>: 
                                <span class="field-type">String</span>
                            </div>
                            <div class="field">
                                <span class="field-name">confidence</span>: 
                                <span class="field-type">Float</span>
                            </div>
                            <div class="field">
                                <span class="field-name">notes</span>: 
                                <span class="field-type">Text</span>
                            </div>
                            <div class="field">
                                <span class="field-name">image_data</span>: 
                                <span class="field-type">String</span>
                            </div>
                            <div class="field">
                                <span class="field-name">timestamp</span>: 
                                <span class="field-type">DateTime</span>
                            </div>
                            <div class="field">
                                <span class="field-name">django_id</span>: 
                                <span class="field-type">Integer</span>
                            </div>
                            <div class="field">
                                <span class="field-name">created_at</span>: 
                                <span class="field-type">DateTime</span>
                            </div>
                            <div class="field">
                                <span class="field-name">updated_at</span>: 
                                <span class="field-type">DateTime</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="relationships">
                <h2>🔗 Relationships</h2>
                <div class="relationship-item">
                    <strong>Student ──1:M──> Attendance</strong><br>
                    One student can have many attendance records
                </div>
                <div class="relationship-item">
                    <strong>User ──1:M──> Student</strong><br>
                    One admin user can manage many students
                </div>
                <div class="relationship-item">
                    <strong>Student ──sync──> MongoDB_Students</strong><br>
                    Data synchronization between Django and MongoDB
                </div>
                <div class="relationship-item">
                    <strong>Attendance ──sync──> MongoDB_Attendance</strong><br>
                    Data synchronization between Django and MongoDB
                </div>
            </div>
            
            <div class="features">
                <h2>✨ Key Features</h2>
                <div class="feature-grid">
                    <div class="feature-item">
                        <h3>🔐 Ultra-Strict Face Recognition</h3>
                        <p>92.98% similarity threshold to prevent unregistered face matches</p>
                    </div>
                    <div class="feature-item">
                        <h3>⏰ Time-Based Attendance Logic</h3>
                        <p>Present/Late/Absent/Checkout/Day Finished based on time</p>
                    </div>
                    <div class="feature-item">
                        <h3>🛡️ Proxy Attack Prevention</h3>
                        <p>Rejects unregistered faces and prevents proxy attacks</p>
                    </div>
                    <div class="feature-item">
                        <h3>🔄 Hybrid Database Architecture</h3>
                        <p>SQLite for relational data, MongoDB for face recognition</p>
                    </div>
                    <div class="feature-item">
                        <h3>🔄 Automatic Data Synchronization</h3>
                        <p>Real-time sync between Django models and MongoDB collections</p>
                    </div>
                    <div class="feature-item">
                        <h3>🧠 Face Embedding Storage</h3>
                        <p>128-dimensional vectors for high-performance face recognition</p>
                    </div>
                </div>
            </div>
            
            <div class="legend">
                <h2>📋 Legend</h2>
                <div class="legend-items">
                    <div class="legend-item pk">PK - Primary Key</div>
                    <div class="legend-item fk">FK - Foreign Key</div>
                    <div class="legend-item uk">UK - Unique Key</div>
                    <div class="legend-item django">Django Model</div>
                    <div class="legend-item mongodb">MongoDB Collection</div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
        """
        return html
    
    def save_html_diagram(self, filename='ai_attendance_er_diagram.html'):
        """Save the HTML diagram to file"""
        html_content = self.generate_html_diagram()
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ HTML ER diagram saved as: {filename}")

def main():
    """Main function to generate HTML ER diagram"""
    try:
        print("🎨 Generating AI Attendance Manager HTML ER Diagram...")
        
        # Create diagram generator
        generator = HTMLERDiagramGenerator()
        
        # Save HTML diagram
        generator.save_html_diagram('ai_attendance_er_diagram.html')
        
        print("")
        print("🎉 HTML ER diagram generated successfully!")
        print("📁 Files created:")
        print("   - ai_attendance_er_diagram.html")
        print("")
        print("🌐 Open the HTML file in your browser to view the interactive ER diagram!")
        
    except Exception as e:
        print(f"❌ Error generating HTML ER diagram: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
