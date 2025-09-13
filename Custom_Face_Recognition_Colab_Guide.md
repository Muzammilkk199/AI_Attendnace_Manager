# Custom Face Recognition Model - Google Colab Guide

## 🎯 Goal
Create a custom face recognition model trained on your student dataset for better accuracy.

## 📋 Prerequisites
1. Google Colab account
2. Student face images (at least 5-10 per student)
3. Basic Python knowledge

## 🚀 Step 1: Setup Colab Environment

```python
# Install required libraries
!pip install tensorflow keras opencv-python numpy matplotlib pillow
!pip install face-recognition dlib
!pip install scikit-learn

# Import libraries
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import numpy as np
import cv2
import os
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import face_recognition
from PIL import Image
```

## 📁 Step 2: Prepare Dataset

```python
# Upload your student images to Colab
from google.colab import files
import zipfile

# Upload zip file containing student folders
uploaded = files.upload()

# Extract the zip file
for filename in uploaded.keys():
    with zipfile.ZipFile(filename, 'r') as zip_ref:
        zip_ref.extractall('/content/student_dataset')

# Dataset structure should be:
# /content/student_dataset/
#   ├── student_1/
#   │   ├── image1.jpg
#   │   ├── image2.jpg
#   │   └── ...
#   ├── student_2/
#   │   ├── image1.jpg
#   │   └── ...
```

## 🔧 Step 3: Preprocess Data

```python
def load_and_preprocess_data(dataset_path):
    faces = []
    labels = []
    student_names = []
    
    for student_folder in os.listdir(dataset_path):
        student_path = os.path.join(dataset_path, student_folder)
        if os.path.isdir(student_path):
            student_names.append(student_folder)
            
            for image_file in os.listdir(student_path):
                if image_file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    image_path = os.path.join(student_path, image_file)
                    
                    # Load image
                    image = face_recognition.load_image_file(image_path)
                    
                    # Find face locations
                    face_locations = face_recognition.face_locations(image)
                    
                    if len(face_locations) == 1:  # Only use images with exactly one face
                        # Extract face encoding
                        face_encoding = face_recognition.face_encodings(image, face_locations)[0]
                        
                        faces.append(face_encoding)
                        labels.append(student_folder)
    
    return np.array(faces), np.array(labels), student_names

# Load your dataset
faces, labels, student_names = load_and_preprocess_data('/content/student_dataset')
print(f"Loaded {len(faces)} face samples from {len(student_names)} students")
```

## 🧠 Step 4: Create Custom Model

```python
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, classification_report

# Encode labels
label_encoder = LabelEncoder()
encoded_labels = label_encoder.fit_transform(labels)

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    faces, encoded_labels, test_size=0.2, random_state=42, stratify=encoded_labels
)

# Try different models
models = {
    'SVM': SVC(kernel='rbf', probability=True),
    'Random Forest': RandomForestClassifier(n_estimators=100),
    'KNN': KNeighborsClassifier(n_neighbors=5)
}

best_model = None
best_accuracy = 0

for name, model in models.items():
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"{name} Accuracy: {accuracy:.3f}")
    
    if accuracy > best_accuracy:
        best_accuracy = accuracy
        best_model = model

print(f"\nBest Model Accuracy: {best_accuracy:.3f}")
```

## 💾 Step 5: Save Model

```python
import pickle

# Save the best model and label encoder
with open('custom_face_model.pkl', 'wb') as f:
    pickle.dump(best_model, f)

with open('label_encoder.pkl', 'wb') as f:
    pickle.dump(label_encoder, f)

# Download the models
files.download('custom_face_model.pkl')
files.download('label_encoder.pkl')
```

## 🔧 Step 6: Integration Code for Django

```python
# Add this to your Django project

import pickle
import face_recognition
import numpy as np

class CustomFaceRecognizer:
    def __init__(self, model_path, encoder_path):
        with open(model_path, 'rb') as f:
            self.model = pickle.load(f)
        with open(encoder_path, 'rb') as f:
            self.label_encoder = pickle.load(f)
    
    def recognize_face(self, face_encoding):
        # Reshape for single prediction
        face_encoding = np.array(face_encoding).reshape(1, -1)
        
        # Get prediction and probability
        prediction = self.model.predict(face_encoding)[0]
        probabilities = self.model.predict_proba(face_encoding)[0]
        
        # Get confidence
        confidence = np.max(probabilities)
        
        # Decode label
        student_name = self.label_encoder.inverse_transform([prediction])[0]
        
        return student_name, confidence

# Usage in your Django views
recognizer = CustomFaceRecognizer('custom_face_model.pkl', 'label_encoder.pkl')
student_name, confidence = recognizer.recognize_face(face_encoding)
```

## 🎯 Step 7: Advanced Model (Deep Learning)

```python
# For even better accuracy, create a CNN model
def create_face_recognition_model(num_students):
    model = keras.Sequential([
        layers.Dense(256, activation='relu', input_shape=(128,)),
        layers.Dropout(0.3),
        layers.Dense(128, activation='relu'),
        layers.Dropout(0.3),
        layers.Dense(64, activation='relu'),
        layers.Dense(num_students, activation='softmax')
    ])
    
    model.compile(
        optimizer='adam',
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    
    return model

# Train the model
num_students = len(np.unique(encoded_labels))
model = create_face_recognition_model(num_students)

history = model.fit(
    X_train, y_train,
    epochs=50,
    batch_size=32,
    validation_data=(X_test, y_test),
    verbose=1
)

# Save the model
model.save('face_recognition_model.h5')
files.download('face_recognition_model.h5')
```

## 📊 Performance Tips

1. **Data Quality:**
   - Use high-resolution images
   - Include different angles and lighting
   - Ensure clear face visibility

2. **Model Optimization:**
   - Experiment with different algorithms
   - Use cross-validation
   - Tune hyperparameters

3. **Integration:**
   - Use confidence thresholds
   - Implement fallback to original model
   - Monitor performance in production

## 🚀 Next Steps

1. Collect student images
2. Run this notebook in Colab
3. Download trained models
4. Integrate into your Django project
5. Test and fine-tune

## 💡 Pro Tips

- Start with at least 10 images per student
- Include variations in lighting, angles, expressions
- Use data augmentation for better generalization
- Regularly retrain with new data
