# cyberkings-03-tiny-project
# Smart-Attendance – Face Detection:
This project is a Smart Attendance System that detects faces from images. It helps mark students present automatically in a CSV file.

⚠️ Note: Currently, the system only detects faces in uploaded images individually. Face recognition (matching faces to registered students) is not implemented yet.

# Features:
 - Detects faces in images using OpenCV
 
 - Draws rectangles around detected faces
 
 - Saves detected faces locally in dataset/ folder
 
 - Generates an Attendance CSV file with detected faces


# Technologies Used
  Python
  
  OpenCV
  
  Pandas

# Installation:
    git clone https://github.com/<YourUsername>/Smart-Attendance.git
    cd Smart-Attendance
    python -m venv attendance_env
Windows PowerShell

    .\attendance_env\Scripts\Activate.ps1
    pip install opencv-python pandas


# How to Run
    python capture_faces.py   # to capture faces (optional)
    python train_model.py     # to train model (optional)
    python recognize_faces.py # to detect faces and mark attendance

  Detected faces will be saved in dataset/ folder
  
  Attendance will be saved in Attendance.csv

# Folder Structure
    Smart-Attendance/
    ├── capture_faces.py      # Capture faces from camera
    ├── train_model.py        # Train face model
    ├── recognize_faces.py    # Detect faces and mark attendance
    ├── dataset/              # Detected face images
    ├── Attendance.csv        # Generated attendance file
