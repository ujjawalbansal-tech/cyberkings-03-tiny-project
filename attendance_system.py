import cv2
import os
import csv
from datetime import datetime

# Load trained face recognizer
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read("face_recognizer.yml")

# Load Haar cascade for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# Map User ID to names (change names as per your users)
user_names = {
    1: "Ujjawal",
    2: "Nupur",
    3: "Nandini"
}

# Attendance CSV
attendance_file = "attendance.csv"
if not os.path.exists(attendance_file):
    with open(attendance_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["UserID", "Name", "Date", "Time"])

# Function to mark attendance
def mark_attendance(user_id):
    now = datetime.now()
    dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
    name = user_names.get(user_id, "Unknown")
    
    # Check if user already marked today
    existing = []
    with open(attendance_file, "r") as f:
        reader = csv.reader(f)
        existing = list(reader)

    today = now.strftime("%Y-%m-%d")
    for row in existing:
        if row[0] == str(user_id) and row[2] == today:
            return  # Already marked today

    # Append attendance
    with open(attendance_file, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([user_id, name, now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S")])
    print(f"Attendance marked for {name}")

# Open webcam
cap = cv2.VideoCapture(0)

print("Press 'q' to quit the attendance system.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Camera error")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        face_img = gray[y:y+h, x:x+w]
        face_img = cv2.resize(face_img, (200, 200))
        
        # Predict user
        user_id, confidence = recognizer.predict(face_img)
        
        # Confidence threshold (lower is better)
        if confidence < 60:
            name = user_names.get(user_id, "Unknown")
            mark_attendance(user_id)
        else:
            name = "Unknown"

        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.putText(frame, name, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,0), 2)

    cv2.imshow("Attendance System - Press Q to Exit", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Attendance system closed")
        break

cap.release()
cv2.destroyAllWindows()